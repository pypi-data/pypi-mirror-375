#!/usr/bin/env python3
"""
TCP P2P Direct Connection Module for SimpleLinks
Handles direct peer-to-peer communication within the same private network
"""

import asyncio
import logging
import socket
import json
import time
import ipaddress
import subprocess
import platform
from typing import Dict, Optional, Tuple, List

logger = logging.getLogger("TCP_P2P")

def is_local_network(ip1: str, ip2: str) -> bool:
    """检查两个IP是否在可路由的本地网络内（RFC1918私有地址空间）"""
    try:
        addr1 = ipaddress.IPv4Address(ip1)
        addr2 = ipaddress.IPv4Address(ip2)
        
        # RFC1918私有地址空间
        private_networks = [
            ipaddress.IPv4Network('10.0.0.0/8'),
            ipaddress.IPv4Network('172.16.0.0/12'),
            ipaddress.IPv4Network('192.168.0.0/16'),
        ]
        
        # 先检查两个地址是否都是私有地址
        ip1_private = any(addr1 in network for network in private_networks)
        ip2_private = any(addr2 in network for network in private_networks)
        
        if not (ip1_private and ip2_private):
            # 如果不是都是私有地址，则不考虑P2P
            return False
        
        # 只要都是 RFC1918 私有地址，就认为可能可达
        # 这将包括跨子网的情况，但会在连接时快速失败并回退
        return True
        
    except Exception as e:
        logger.debug(f"Error checking local network for {ip1}, {ip2}: {e}")
        return False

async def test_ping_connectivity(target_ip: str, timeout: float = 1.0) -> bool:
    """测试对目标IP的ping连通性"""
    try:
        system = platform.system().lower()
        
        if system == 'linux' or system == 'darwin':  # Linux or macOS
            # 使用-c 1只发送一个ping包，-W/-w设置超时
            if system == 'linux':
                cmd = ['ping', '-c', '1', '-W', str(int(timeout)), target_ip]
            else:  # macOS
                cmd = ['ping', '-c', '1', '-W', str(int(timeout * 1000)), target_ip]
        elif system == 'windows':
            # Windows使用-n 1发送一个ping包，-w设置超时(毫秒)
            cmd = ['ping', '-n', '1', '-w', str(int(timeout * 1000)), target_ip]
        else:
            logger.debug(f"Unsupported platform for ping: {system}")
            return False
        
        # 使用asyncio.subprocess执行ping命令
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        
        try:
            # 等待进程完成，最多等待timeout*2时间
            await asyncio.wait_for(process.wait(), timeout=timeout * 2)
            return process.returncode == 0
        except asyncio.TimeoutError:
            # 如果超时，杀死进程
            try:
                process.kill()
                await process.wait()
            except:
                pass
            return False
            
    except Exception as e:
        logger.debug(f"Ping test to {target_ip} failed: {e}")
        return False

class TcpP2PManager:
    """管理TCP P2P直连的类"""
    
    def __init__(self, local_port: int = 20002, timeout: float = 0.5):
        self.local_port = local_port
        self.timeout = timeout
        self.server = None
        self.running = False
        
        # 存储已知的内网节点信息 {virtual_ip: (private_ip, last_seen)}
        self.peers: Dict[str, Tuple[str, float]] = {}
        
        # 存储活跃的TCP连接 {virtual_ip: (reader, writer)}
        self.active_connections: Dict[str, Tuple[asyncio.StreamReader, asyncio.StreamWriter]] = {}
        
        # 待处理的数据包队列
        self.pending_packets: asyncio.Queue = asyncio.Queue()
        
        # 获取本机IP地址
        self.local_ip = self._get_local_ip()
        
        # 连通性测试缓存 {ip: (is_reachable, test_time)}
        self.connectivity_cache: Dict[str, Tuple[bool, float]] = {}
        self.connectivity_cache_ttl = 300  # 5分钟缓存
        
    def _get_local_ip(self) -> str:
        """获取本机私有IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"
    
    async def _test_connectivity_cached(self, target_ip: str) -> bool:
        """带缓存的连通性测试"""
        current_time = time.time()
        
        # 检查缓存
        if target_ip in self.connectivity_cache:
            is_reachable, test_time = self.connectivity_cache[target_ip]
            if current_time - test_time < self.connectivity_cache_ttl:
                logger.debug(f"P2P: Using cached connectivity result for {target_ip}: {is_reachable}")
                return is_reachable
        
        # 执行ping测试
        logger.debug(f"P2P: Testing ping connectivity to {target_ip}...")
        ping_start = time.time()
        is_reachable = await test_ping_connectivity(target_ip, timeout=0.5)  # 500ms超时
        ping_time = (time.time() - ping_start) * 1000  # ms
        
        # 缓存结果
        self.connectivity_cache[target_ip] = (is_reachable, current_time)
        
        logger.info(f"P2P: Ping test to {target_ip}: {'SUCCESS' if is_reachable else 'FAILED'} ({ping_time:.1f}ms)")
        return is_reachable
        
    async def start(self):
        """启动TCP监听器"""
        try:
            self.server = await asyncio.start_server(
                self._handle_incoming_connection,
                '0.0.0.0',
                self.local_port
            )
            
            self.running = True
            logger.info(f"TCP P2P manager started on port {self.local_port}")
            
            # 启动后台任务
            asyncio.create_task(self._connection_monitor())
            
        except Exception as e:
            logger.error(f"Failed to start TCP P2P manager: {e}")
            raise
    
    async def stop(self):
        """停止TCP监听器"""
        self.running = False
        
        # 关闭所有活跃连接
        for virtual_ip, (reader, writer) in self.active_connections.items():
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                logger.debug(f"Error closing connection to {virtual_ip}: {e}")
        
        self.active_connections.clear()
        
        # 关闭服务器
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
            
        logger.info("TCP P2P manager stopped")
    
    def update_peers(self, peer_list: List[Dict]):
        """更新节点列表"""
        current_time = time.time()
        
        for peer in peer_list:
            virtual_ip = peer["virtual_ip"]
            private_ip = peer["private_ip"]
            if private_ip:  # 只处理有效的private_ip
                self.peers[virtual_ip] = (private_ip, current_time)
                logger.debug(f"P2P: Added/updated peer {virtual_ip}@{private_ip}")
            else:
                logger.debug(f"P2P: Skipping peer {virtual_ip} (no private IP)")
            
        logger.info(f"P2P: Updated peer list: {len(self.peers)} peers")
        logger.debug(f"P2P: Active peers: {[(vip, pip) for vip, (pip, _) in self.peers.items()]}")
    
    async def try_direct_send(self, target_virtual_ip: str, data: bytes) -> bool:
        """
        尝试直接发送数据包到目标节点
        返回True表示成功发送，False表示需要回退到服务器中转
        """
        logger.debug(f"P2P: Attempting to send packet to {target_virtual_ip} ({len(data)} bytes)")
        
        if target_virtual_ip not in self.peers:
            logger.debug(f"P2P: No peer info for {target_virtual_ip}, using server relay")
            return False
        
        # 检查是否已有活跃连接
        if target_virtual_ip in self.active_connections:
            try:
                reader, writer = self.active_connections[target_virtual_ip]
                await self._send_packet(writer, data)
                logger.debug(f"Sent packet via existing connection to {target_virtual_ip} ({len(data)} bytes)")
                return True
            except Exception as e:
                logger.debug(f"Existing connection to {target_virtual_ip} failed: {e}")
                # 移除失效的连接
                await self._close_connection(target_virtual_ip)
        
        # 尝试建立新连接
        private_ip, last_seen = self.peers[target_virtual_ip]
        
        # 检查节点信息是否过期（超过5分钟认为过期）
        if time.time() - last_seen > 300:
            logger.debug(f"Peer info for {target_virtual_ip} is stale, using server relay")
            return False
        
        # 检查是否在同一个本地网络内，只对本地网络尝试P2P直连
        local_net_check = is_local_network(self.local_ip, private_ip)
        logger.debug(f"P2P: Local network check - self: {self.local_ip}, peer: {private_ip}, result: {local_net_check}")
        
        if not local_net_check:
            logger.debug(f"P2P: Peer {target_virtual_ip}@{private_ip} not in local network, using server relay")
            return False
        
        # 测试ping连通性
        connectivity_ok = await self._test_connectivity_cached(private_ip)
        if not connectivity_ok:
            logger.debug(f"P2P: Peer {target_virtual_ip}@{private_ip} not reachable via ping, using server relay")
            return False
        
        try:
            import time
            start_time = time.time()
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(private_ip, self.local_port),
                timeout=self.timeout
            )
            connect_time = (time.time() - start_time) * 1000  # ms
            
            # 建立连接成功，缓存连接
            self.active_connections[target_virtual_ip] = (reader, writer)
            
            # 启动接收任务
            asyncio.create_task(self._handle_connection_data(target_virtual_ip, reader))
            
            # 发送数据包
            send_start = time.time()
            await self._send_packet(writer, data)
            send_time = (time.time() - send_start) * 1000  # ms
            
            logger.info(f"Established new P2P connection to {target_virtual_ip}@{private_ip} (connect: {connect_time:.1f}ms, send: {send_time:.1f}ms)")
            logger.debug(f"Sent packet via new connection to {target_virtual_ip} ({len(data)} bytes)")
            return True
            
        except Exception as e:
            logger.debug(f"Direct connection to {target_virtual_ip}@{private_ip} failed: {e}")
            return False
    
    async def _send_packet(self, writer: asyncio.StreamWriter, data: bytes):
        """发送数据包到TCP连接"""
        # 发送数据长度（4字节，大端）+ 数据
        length = len(data)
        length_bytes = length.to_bytes(4, 'big')
        writer.write(length_bytes + data)
        await writer.drain()
    
    async def _handle_incoming_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """处理传入的TCP连接"""
        peer_addr = writer.get_extra_info('peername')
        logger.debug(f"New incoming connection from {peer_addr}")
        
        try:
            # 查找对应的虚拟IP
            peer_virtual_ip = None
            for virtual_ip, (private_ip, _) in self.peers.items():
                if private_ip == peer_addr[0]:
                    peer_virtual_ip = virtual_ip
                    break
            
            if peer_virtual_ip is None:
                logger.warning(f"Unknown peer connection from {peer_addr[0]}")
                writer.close()
                await writer.wait_closed()
                return
            
            # 缓存连接
            self.active_connections[peer_virtual_ip] = (reader, writer)
            logger.info(f"Accepted P2P connection from {peer_virtual_ip}@{peer_addr[0]}")
            
            # 处理连接数据
            await self._handle_connection_data(peer_virtual_ip, reader)
            
        except Exception as e:
            logger.error(f"Error handling incoming connection from {peer_addr}: {e}")
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
    
    async def _handle_connection_data(self, peer_virtual_ip: str, reader: asyncio.StreamReader):
        """处理连接数据"""
        try:
            while self.running and peer_virtual_ip in self.active_connections:
                # 读取数据长度（4字节）
                length_bytes = await reader.readexactly(4)
                length = int.from_bytes(length_bytes, 'big')
                
                # 读取数据
                if length > 0:
                    data = await reader.readexactly(length)
                    await self.pending_packets.put((peer_virtual_ip, data))
                    logger.debug(f"Received packet from {peer_virtual_ip} via P2P ({length} bytes)")
                
        except asyncio.IncompleteReadError:
            logger.debug(f"P2P connection to {peer_virtual_ip} closed by peer")
        except Exception as e:
            logger.debug(f"Error reading from P2P connection to {peer_virtual_ip}: {e}")
        finally:
            await self._close_connection(peer_virtual_ip)
    
    async def _close_connection(self, virtual_ip: str):
        """关闭指定的连接"""
        if virtual_ip in self.active_connections:
            reader, writer = self.active_connections.pop(virtual_ip)
            try:
                writer.close()
                await writer.wait_closed()
                logger.debug(f"Closed P2P connection to {virtual_ip}")
            except Exception as e:
                logger.debug(f"Error closing connection to {virtual_ip}: {e}")
    
    async def get_received_packet(self) -> Optional[Tuple[str, bytes]]:
        """获取接收到的数据包（非阻塞）"""
        try:
            return self.pending_packets.get_nowait()
        except asyncio.QueueEmpty:
            return None
    
    async def wait_for_packet(self, timeout: float = 0.001) -> Optional[Tuple[str, bytes]]:
        """等待数据包（阻塞版本，用于高性能处理）"""
        try:
            return await asyncio.wait_for(self.pending_packets.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
    
    async def _connection_monitor(self):
        """连接监控器，清理过期的连接和节点信息"""
        while self.running:
            try:
                current_time = time.time()
                
                # 清理过期的节点信息（超过10分钟）
                expired_peers = [
                    virtual_ip for virtual_ip, (_, last_seen) in self.peers.items()
                    if current_time - last_seen > 600
                ]
                
                for virtual_ip in expired_peers:
                    del self.peers[virtual_ip]
                    await self._close_connection(virtual_ip)
                    logger.debug(f"Removed expired peer: {virtual_ip}")
                
                # 清理过期的连通性缓存
                expired_cache = [
                    ip for ip, (_, test_time) in self.connectivity_cache.items()
                    if current_time - test_time > self.connectivity_cache_ttl
                ]
                for ip in expired_cache:
                    del self.connectivity_cache[ip]
                    logger.debug(f"Removed expired connectivity cache for: {ip}")
                
                # 每30秒运行一次
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Connection monitor error: {e}")
                await asyncio.sleep(30)
    
    def get_stats(self) -> Dict:
        """获取P2P连接统计信息"""
        return {
            'running': self.running,
            'local_port': self.local_port,
            'known_peers': len(self.peers),
            'active_connections': len(self.active_connections),
            'pending_packets': self.pending_packets.qsize(),
            'connectivity_cache': len(self.connectivity_cache),
            'reachable_peers': sum(1 for is_reachable, _ in self.connectivity_cache.values() if is_reachable)
        }
