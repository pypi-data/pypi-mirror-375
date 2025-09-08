"""
네트워크 리소스 모니터링 유틸리티
"""

import socket
import requests
import psutil
import ipaddress
from typing import Dict, List, Tuple, Any, Optional
import subprocess
import platform


def get_public_ip() -> str:
    """공용 IP 주소 반환"""
    try:
        # 여러 서비스를 시도
        services = [
            "https://api.ipify.org",
            "https://icanhazip.com",
            "https://ipecho.net/plain",
            "https://checkip.amazonaws.com"
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    return response.text.strip()
            except:
                continue
        
        return "Unable to determine"
        
    except Exception as e:
        return f"Error: {e}"


def get_interface_ips(ignore_interfaces: List[str] = None, detail: bool = False) -> List[Tuple[str, Dict[str, Any]]]:
    """네트워크 인터페이스 IP 정보 반환"""
    if ignore_interfaces is None:
        ignore_interfaces = ['lo', 'lo0']
    
    interfaces = []
    
    try:
        # psutil을 사용하여 네트워크 인터페이스 정보 가져오기
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()
        
        for interface_name, addresses in net_if_addrs.items():
            if interface_name in ignore_interfaces:
                continue
            
            interface_info = {
                "ip": None,
                "subnet": None,
                "gateway": None,
                "status": "down"
            }
            
            # 인터페이스 상태 확인
            if interface_name in net_if_stats:
                stats = net_if_stats[interface_name]
                interface_info["status"] = "up" if stats.isup else "down"
            
            # IPv4 주소 찾기
            for addr in addresses:
                if addr.family == socket.AF_INET:
                    interface_info["ip"] = addr.address
                    if addr.netmask:
                        # 서브넷 마스크를 CIDR로 변환
                        try:
                            network = ipaddress.IPv4Network(f"{addr.address}/{addr.netmask}", strict=False)
                            interface_info["subnet"] = str(network.prefixlen)
                        except:
                            interface_info["subnet"] = addr.netmask
                    break
            
            # 게이트웨이 정보 (기본 게이트웨이 확인)
            if detail and interface_info["ip"]:
                gateway = get_default_gateway()
                if gateway and is_same_network(interface_info["ip"], gateway, interface_info.get("subnet")):
                    interface_info["gateway"] = gateway
            
            if interface_info["ip"]:
                interfaces.append((interface_name, interface_info))
    
    except Exception as e:
        # 오류 발생 시 기본 방법으로 시도
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            interfaces.append(("default", {"ip": local_ip, "subnet": None, "gateway": None, "status": "up"}))
        except:
            pass
    
    return interfaces


def get_default_gateway() -> Optional[str]:
    """기본 게이트웨이 IP 반환"""
    try:
        system = platform.system().lower()
        
        if system == "linux":
            result = subprocess.run(['ip', 'route', 'show', 'default'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'default via' in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            return parts[2]
        
        elif system == "darwin":  # macOS
            result = subprocess.run(['route', '-n', 'get', 'default'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'gateway:' in line:
                        return line.split(':')[1].strip()
        
        elif system == "windows":
            result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for i, line in enumerate(lines):
                    if 'Default Gateway' in line and ':' in line:
                        gateway = line.split(':')[1].strip()
                        if gateway and gateway != '':
                            return gateway
    
    except Exception:
        pass
    
    return None


def is_same_network(ip1: str, ip2: str, subnet: str) -> bool:
    """두 IP가 같은 네트워크에 있는지 확인"""
    try:
        if not subnet:
            return False
        
        # CIDR 형태로 변환
        if '.' in subnet:  # 서브넷 마스크 형태
            network = ipaddress.IPv4Network(f"{ip1}/{subnet}", strict=False)
        else:  # CIDR 형태
            network = ipaddress.IPv4Network(f"{ip1}/{subnet}", strict=False)
        
        return ipaddress.IPv4Address(ip2) in network
    
    except Exception:
        return False


def get_location_with_ip_api(ip: str = None) -> Dict[str, Any]:
    """ip-api.com을 사용하여 IP 위치 정보 반환"""
    try:
        url = "http://ip-api.com/json/"
        if ip:
            url += ip
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        
        return {"status": "fail", "message": "API request failed"}
        
    except Exception as e:
        return {"status": "fail", "message": str(e)}


def get_location(ip: str) -> Optional[Dict[str, Any]]:
    """IP 위치 정보 반환 (대체 서비스 사용)"""
    try:
        # ipinfo.io 사용
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "region": data.get("region", ""),
                "country": data.get("country", ""),
                "city": data.get("city", ""),
                "timezone": data.get("timezone", ""),
                "asn": {
                    "org": data.get("org", "")
                }
            }
    
    except Exception:
        pass
    
    return None


def get_network_stats() -> Dict[str, Any]:
    """네트워크 통계 정보 반환"""
    try:
        net_io = psutil.net_io_counters()
        
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "errin": net_io.errin,
            "errout": net_io.errout,
            "dropin": net_io.dropin,
            "dropout": net_io.dropout
        }
    
    except Exception as e:
        return {"error": str(e)}


def get_network_connections(kind: str = "inet") -> List[Dict[str, Any]]:
    """네트워크 연결 정보 반환"""
    try:
        connections = []
        
        for conn in psutil.net_connections(kind=kind):
            connection_info = {
                "fd": conn.fd,
                "family": conn.family.name if conn.family else None,
                "type": conn.type.name if conn.type else None,
                "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                "status": conn.status,
                "pid": conn.pid
            }
            connections.append(connection_info)
        
        return connections
    
    except Exception as e:
        return [{"error": str(e)}]


def ping_host(host: str, count: int = 4) -> Dict[str, Any]:
    """호스트 핑 테스트"""
    try:
        system = platform.system().lower()
        
        if system == "windows":
            cmd = ["ping", "-n", str(count), host]
        else:
            cmd = ["ping", "-c", str(count), host]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        return {
            "host": host,
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None
        }
    
    except Exception as e:
        return {
            "host": host,
            "success": False,
            "error": str(e)
        }