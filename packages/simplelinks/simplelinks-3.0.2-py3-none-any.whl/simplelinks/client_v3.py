#!/usr/bin/env python3
"""
SimpleLinks Client v3 with TCP P2P Support
Supports both WebSocket server relay and direct TCP P2P communication
"""

import argparse
import asyncio
import websockets
import logging
import os
import fcntl
import struct
import ssl
import socket
import json
import time
from typing import Optional
from tcp_p2p import TcpP2PManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CLIENT_V3")

# TUN设备常量
TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000

def get_private_ip() -> str:
    """获取本机私有IP地址"""
    try:
        # 尝试连接到一个外部地址来获取本机IP（不会实际连接）
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        private_ip = s.getsockname()[0]
        s.close()
        return private_ip
    except Exception:
        # 如果失败，使用localhost
        return "127.0.0.1"

def parse_ipv4_packet(data):
    """Parse IPv4 packet and extract destination IP"""
    if len(data) < 20:
        return None
    
    try:
        dst_ip_bytes = data[16:20]
        dst_ip = socket.inet_ntoa(dst_ip_bytes)
        return dst_ip
    except Exception:
        return None

def create_tun(ip):
    try:
        # 创建TUN设备
        tun_fd = os.open("/dev/net/tun", os.O_RDWR)
        ifr = struct.pack("16sH", b"slink0", IFF_TUN | IFF_NO_PI)
        ifname = fcntl.ioctl(tun_fd, TUNSETIFF, ifr)
        
        # 配置IP地址 - 使用10.254.254.x网段
        os.system(f"ip addr add {ip}/24 dev slink0")
        os.system("ip link set slink0 up")
        logger.info(f"Created TUN device slink0 with IP: {ip}")
        return tun_fd
    except Exception as e:
        logger.error(f"Failed to create TUN device: {str(e)}")
        raise

class P2PClient:
    def __init__(self, server_host: str, secret: str, virtual_ip: str, enable_p2p: bool = True):
        self.server_host = server_host
        self.secret = secret
        self.virtual_ip = virtual_ip
        self.enable_p2p = enable_p2p
        self.private_ip = get_private_ip()
        
        # TCP P2P管理器
        self.p2p_manager = TcpP2PManager() if enable_p2p else None
        
        # WebSocket连接
        self.ws = None
        self.tun_fd = None
        
        # 统计信息
        self.stats = {
            'p2p_sent': 0,
            'relay_sent': 0,
            'p2p_received': 0,
            'relay_received': 0
        }
    
    async def start(self):
        """启动客户端"""
        try:
            # 创建TUN设备
            self.tun_fd = create_tun(self.virtual_ip)
            
            # 启动TCP P2P管理器
            if self.p2p_manager:
                await self.p2p_manager.start()
                logger.info(f"P2P enabled - Private IP: {self.private_ip}, TCP port: {self.p2p_manager.local_port}")
            else:
                logger.info("P2P disabled - using server relay only")
            
            # SSL上下文
            ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE
            
            # 连接WebSocket服务器
            async with websockets.connect(
                self.server_host,
                ssl=ssl_ctx,
                ping_interval=30,
                ping_timeout=None
            ) as ws:
                self.ws = ws
                
                # 注册客户端（包含私有IP）
                register_msg = f"{self.secret}|{self.virtual_ip}|{self.virtual_ip}|{self.private_ip}"
                await ws.send(register_msg)
                logger.info("Registration sent to server")
                
                # 启动所有任务
                tasks = [
                    self.tun_reader(),
                    self.ws_reader(),
                ]
                
                if self.p2p_manager:
                    tasks.append(self.p2p_packet_processor())
                
                await asyncio.gather(*tasks)
                
        except Exception as e:
            logger.error(f"Client error: {e}")
        finally:
            await self.cleanup()
    
    async def tun_reader(self):
        """读取TUN设备数据并发送"""
        loop = asyncio.get_event_loop()
        
        while True:
            try:
                # 读取TUN设备数据
                data = await loop.run_in_executor(
                    None, 
                    lambda: os.read(self.tun_fd, 1500)
                )
                
                if not data:
                    break
                
                # 解析目标IP
                target_ip = parse_ipv4_packet(data)
                if target_ip is None:
                    logger.debug("Failed to parse IPv4 packet, skipping")
                    continue
                
                # 只处理10.254.254.x网段的包
                if not target_ip.startswith("10.254.254."):
                    logger.debug(f"Ignoring packet to {target_ip} (not in VPN network)")
                    continue
                
                # 尝试P2P直接发送
                sent_via_p2p = False
                if self.p2p_manager:
                    sent_via_p2p = await self.p2p_manager.try_direct_send(target_ip, data)
                    if sent_via_p2p:
                        self.stats['p2p_sent'] += 1
                        logger.debug(f"Sent packet via P2P to {target_ip} ({len(data)} bytes)")
                
                # 如果P2P发送失败，使用服务器中转
                if not sent_via_p2p:
                    if self.ws:
                        await self.ws.send(f"{target_ip}|{data.hex()}")
                        self.stats['relay_sent'] += 1
                        logger.debug(f"Sent packet via server to {target_ip} ({len(data)} bytes)")
                    else:
                        logger.warning("No connection available for packet delivery")
                
            except Exception as e:
                logger.error(f"TUN read error: {e}")
                break
    
    async def ws_reader(self):
        """读取WebSocket数据"""
        try:
            async for message in self.ws:
                try:
                    # 检查是否是控制消息（P2P发现相关）
                    if "|" in message and message.startswith("PEER_LIST|"):
                        # 处理节点列表
                        _, peer_list_json = message.split("|", 1)
                        peer_list = json.loads(peer_list_json)
                        
                        if self.p2p_manager:
                            self.p2p_manager.update_peers(peer_list)
                            logger.info(f"Updated P2P peer list: {len(peer_list)} peers")
                        continue
                    
                    # 处理数据包（服务器转发的）
                    payload = message
                    await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: os.write(self.tun_fd, bytes.fromhex(payload))
                    )
                    self.stats['relay_received'] += 1
                    logger.debug(f"Received packet via server ({len(payload)//2} bytes)")
                    
                except ValueError as e:
                    logger.error(f"Invalid message format: {e}")
                    
        except Exception as e:
            logger.error(f"WebSocket read error: {e}")
    
    async def p2p_packet_processor(self):
        """处理P2P接收到的数据包"""
        if not self.p2p_manager:
            return
        
        while True:
            try:
                # 获取P2P接收到的数据包
                packet = await self.p2p_manager.get_received_packet()
                if packet:
                    peer_virtual_ip, data = packet
                    
                    # 将数据包写入TUN设备
                    await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: os.write(self.tun_fd, data)
                    )
                    self.stats['p2p_received'] += 1
                    logger.debug(f"Received packet via P2P from {peer_virtual_ip} ({len(data)} bytes)")
                
                # 避免CPU占用过高
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"P2P packet processor error: {e}")
                await asyncio.sleep(1)
    
    async def cleanup(self):
        """清理资源"""
        if self.p2p_manager:
            await self.p2p_manager.stop()
        
        if self.tun_fd is not None:
            os.close(self.tun_fd)
            os.system("ip link del slink0 2>/dev/null")
            logger.info("TUN device cleaned up")
        
        # 输出统计信息
        total_sent = self.stats['p2p_sent'] + self.stats['relay_sent']
        total_received = self.stats['p2p_received'] + self.stats['relay_received']
        
        if total_sent > 0 or total_received > 0:
            logger.info("=== Traffic Statistics ===")
            logger.info(f"Sent - P2P: {self.stats['p2p_sent']}, Relay: {self.stats['relay_sent']}")
            logger.info(f"Received - P2P: {self.stats['p2p_received']}, Relay: {self.stats['relay_received']}")
            
            if total_sent > 0:
                p2p_percentage = (self.stats['p2p_sent'] / total_sent) * 100
                logger.info(f"P2P efficiency: {p2p_percentage:.1f}% of sent traffic")

async def main():
    parser = argparse.ArgumentParser(description="SimpleLinks Client v3 with TCP P2P Support")
    parser.add_argument("--host", required=True, 
                       help="WSS server address (e.g. wss://demo.devnull.cn:20001)")
    parser.add_argument("-s", "--secret", required=True, help="Shared secret")
    parser.add_argument("-i", "--ip", required=True, help="Virtual TUN IP (10.254.254.x)")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--no-p2p", action="store_true", help="Disable P2P, use server relay only")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger("TCP_P2P").setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 创建并启动客户端
    client = P2PClient(
        server_host=args.host,
        secret=args.secret,
        virtual_ip=args.ip,
        enable_p2p=not args.no_p2p
    )
    
    try:
        await client.start()
    except KeyboardInterrupt:
        logger.info("Client stopped by user")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program terminated")
