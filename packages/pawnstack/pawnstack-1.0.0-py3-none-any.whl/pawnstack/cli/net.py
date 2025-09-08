"""
PawnStack Net 도구

네트워크 연결 테스트 및 스캔 도구
"""

import asyncio
import socket
import ipaddress
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple
from argparse import ArgumentParser
import concurrent.futures

from pawnstack import __version__
from pawnstack.config.global_config import pawn
from pawnstack.cli.base import BaseCLI
from pawnstack.cli.banner import generate_banner

# 모듈 메타데이터
__description__ = 'Network connectivity testing and scanning tool'

__epilog__ = (
    "This script provides various options to check network status.\n\n"
    "Usage examples:\n"
    "  1. Network check:\n\tpawns net check --verbose\n\n"
    "  2. Wait for port:\n\tpawns net wait --host 192.168.1.1 --port 80\n\n"
    "  3. Port scan:\n\tpawns net scan --host-range 192.168.1.1-192.168.1.10 --port-range 20-80\n\n"
    "For more details, use the -h or --help flag."
)


@dataclass
class NetConfig:
    """네트워크 설정"""
    command: str = "check"
    host: str = "8.8.8.8"
    port: int = 80
    timeout: float = 5.0
    workers: int = 50
    host_range: str = ""
    port_range: str = ""
    view_type: str = "all"


class NetCLI(BaseCLI):
    """Net CLI"""
    
    def __init__(self, args=None):
        super().__init__(args)
    
    def get_arguments(self, parser: ArgumentParser):
        """인수 정의"""
        parser.add_argument('command', help='Command to execute (check, wait, scan)', 
                          nargs='?', choices=['check', 'wait', 'scan'], default='check')
        
        parser.add_argument('--host', type=str, help='Target host (default: 8.8.8.8)', default='8.8.8.8')
        parser.add_argument('--port', type=int, help='Target port (default: 80)', default=80)
        parser.add_argument('--timeout', type=float, help='Connection timeout in seconds (default: 5)', default=5.0)
        parser.add_argument('--workers', type=int, help='Number of concurrent workers (default: 50)', default=50)
        
        # 스캔 관련 옵션
        parser.add_argument('--host-range', type=str, help='Host range (e.g., 192.168.1.1-192.168.1.255)')
        parser.add_argument('--port-range', type=str, help='Port range (e.g., 20-80)')
        parser.add_argument('--view-type', type=str, choices=['all', 'open', 'closed'], 
                          help='View type for scan results (default: all)', default='all')
        
        parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                          help='Logging level (default: INFO)', default="INFO")
    
    def setup_config(self):
        """설정 초기화"""
        args = self.args
        app_name = 'net'
        
        pawn.set(
            PAWN_LOGGER=dict(
                log_level=getattr(args, 'log_level', 'INFO'),
                stdout_level=getattr(args, 'log_level', 'INFO'),
                stdout=True,
                use_hook_exception=True,
                show_path=False,
            ),
            PAWN_CONSOLE=dict(
                redirect=True,
                record=True,
            ),
            app_name=app_name,
            args=args,
        )
    
    def print_banner(self):
        """배너 출력"""
        banner = generate_banner(
            app_name="Net",
            author="PawnStack Team",
            version=__version__,
            font="graffiti"
        )
        print(banner)
    
    def create_config(self) -> NetConfig:
        """설정 객체 생성"""
        return NetConfig(
            command=getattr(self.args, 'command', 'check'),
            host=getattr(self.args, 'host', '8.8.8.8'),
            port=getattr(self.args, 'port', 80),
            timeout=getattr(self.args, 'timeout', 5.0),
            workers=getattr(self.args, 'workers', 50),
            host_range=getattr(self.args, 'host_range', ''),
            port_range=getattr(self.args, 'port_range', ''),
            view_type=getattr(self.args, 'view_type', 'all')
        )
    
    def validate_ip(self, ip: str) -> bool:
        """IP 주소 유효성 검사"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def parse_host_range(self, host_range: str) -> List[str]:
        """호스트 범위 파싱"""
        if not host_range:
            return []
        
        if '-' not in host_range:
            if self.validate_ip(host_range):
                return [host_range]
            else:
                self.log_error(f"Invalid IP address: {host_range}")
                return []
        
        try:
            start_ip, end_ip = host_range.split('-')
            start = ipaddress.ip_address(start_ip)
            end = ipaddress.ip_address(end_ip)
            
            if start > end:
                self.log_error("Start IP must be less than or equal to end IP")
                return []
            
            # IP 범위 생성
            hosts = []
            current = start
            while current <= end:
                hosts.append(str(current))
                current += 1
                if len(hosts) > 1000:  # 안전장치
                    self.log_warning("Host range too large, limiting to 1000 hosts")
                    break
            
            return hosts
            
        except ValueError as e:
            self.log_error(f"Invalid host range: {e}")
            return []
    
    def parse_port_range(self, port_range: str) -> List[int]:
        """포트 범위 파싱"""
        if not port_range:
            return []
        
        if '-' not in port_range:
            try:
                port = int(port_range)
                if 0 <= port <= 65535:
                    return [port]
                else:
                    self.log_error(f"Port must be between 0-65535: {port}")
                    return []
            except ValueError:
                self.log_error(f"Invalid port: {port_range}")
                return []
        
        try:
            start_port, end_port = map(int, port_range.split('-'))
            if not (0 <= start_port <= 65535 and 0 <= end_port <= 65535):
                self.log_error("Ports must be between 0-65535")
                return []
            
            if start_port > end_port:
                self.log_error("Start port must be less than or equal to end port")
                return []
            
            return list(range(start_port, end_port + 1))
            
        except ValueError:
            self.log_error(f"Invalid port range: {port_range}")
            return []
    
    def check_port(self, host: str, port: int, timeout: float) -> Dict[str, Any]:
        """포트 연결 확인"""
        start_time = time.time()
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            response_time = time.time() - start_time
            
            return {
                "host": host,
                "port": port,
                "open": result == 0,
                "response_time": response_time,
                "error": None
            }
            
        except Exception as e:
            return {
                "host": host,
                "port": port,
                "open": False,
                "response_time": time.time() - start_time,
                "error": str(e)
            }
    
    def network_check(self, config: NetConfig):
        """네트워크 연결 확인"""
        pawn.console.log(f"🔍 Checking network connectivity to {config.host}:{config.port}")
        
        result = self.check_port(config.host, config.port, config.timeout)
        
        if result["open"]:
            pawn.console.log(f"[green]✅ {config.host}:{config.port} is reachable "
                           f"(response time: {result['response_time']:.3f}s)[/green]")
        else:
            error_msg = f" - {result['error']}" if result['error'] else ""
            pawn.console.log(f"[red]❌ {config.host}:{config.port} is not reachable "
                           f"(timeout: {result['response_time']:.3f}s){error_msg}[/red]")
        
        # 추가 네트워크 정보
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            pawn.console.log(f"📡 Local hostname: {hostname}")
            pawn.console.log(f"📡 Local IP: {local_ip}")
        except Exception as e:
            pawn.console.log(f"[yellow]⚠️  Could not get local network info: {e}[/yellow]")
    
    def wait_for_port(self, config: NetConfig):
        """포트가 열릴 때까지 대기"""
        pawn.console.log(f"⏳ Waiting for {config.host}:{config.port} to be available...")
        pawn.console.log("Press Ctrl+C to stop")
        
        attempt = 0
        try:
            while True:
                attempt += 1
                result = self.check_port(config.host, config.port, config.timeout)
                
                if result["open"]:
                    pawn.console.log(f"[green]✅ {config.host}:{config.port} is now available! "
                                   f"(attempt {attempt}, response time: {result['response_time']:.3f}s)[/green]")
                    break
                else:
                    pawn.console.log(f"[yellow]⏳ Attempt {attempt}: {config.host}:{config.port} not available, "
                                   f"retrying in 2s...[/yellow]")
                    time.sleep(2)
                    
        except KeyboardInterrupt:
            pawn.console.log(f"[yellow]⚠️  Wait cancelled by user after {attempt} attempts[/yellow]")
    
    def port_scan(self, config: NetConfig):
        """포트 스캔"""
        hosts = self.parse_host_range(config.host_range) if config.host_range else [config.host]
        ports = self.parse_port_range(config.port_range) if config.port_range else [config.port]
        
        if not hosts:
            self.log_error("No valid hosts to scan")
            return
        
        if not ports:
            self.log_error("No valid ports to scan")
            return
        
        total_scans = len(hosts) * len(ports)
        pawn.console.log(f"🔍 Starting port scan: {len(hosts)} hosts × {len(ports)} ports = {total_scans} scans")
        pawn.console.log(f"⚙️  Using {config.workers} workers, timeout: {config.timeout}s")
        
        open_ports = []
        closed_ports = []
        
        # 스캔 작업 생성
        scan_tasks = []
        for host in hosts:
            for port in ports:
                scan_tasks.append((host, port))
        
        # 병렬 스캔 실행
        with concurrent.futures.ThreadPoolExecutor(max_workers=config.workers) as executor:
            future_to_task = {
                executor.submit(self.check_port, host, port, config.timeout): (host, port)
                for host, port in scan_tasks
            }
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_task):
                result = future.result()
                completed += 1
                
                if result["open"]:
                    open_ports.append(result)
                    if config.view_type in ['all', 'open']:
                        pawn.console.log(f"[green]✅ {result['host']}:{result['port']} OPEN "
                                       f"({result['response_time']:.3f}s)[/green]")
                else:
                    closed_ports.append(result)
                    if config.view_type in ['all', 'closed']:
                        error_msg = f" - {result['error']}" if result['error'] else ""
                        pawn.console.log(f"[red]❌ {result['host']}:{result['port']} CLOSED{error_msg}[/red]")
                
                # 진행률 표시
                if completed % 50 == 0 or completed == total_scans:
                    progress = (completed / total_scans) * 100
                    pawn.console.log(f"📊 Progress: {completed}/{total_scans} ({progress:.1f}%)")
        
        # 결과 요약
        pawn.console.log(f"\n📊 Scan Results:")
        pawn.console.log(f"  Total scanned: {total_scans}")
        pawn.console.log(f"  Open ports: {len(open_ports)}")
        pawn.console.log(f"  Closed ports: {len(closed_ports)}")
        
        if open_ports:
            pawn.console.log(f"\n🔓 Open Ports:")
            for result in open_ports:
                pawn.console.log(f"  {result['host']}:{result['port']} ({result['response_time']:.3f}s)")
    
    def run(self) -> int:
        """Net CLI 실행"""
        self.setup_config()
        self.print_banner()
        
        config = self.create_config()
        
        if config.command == "check":
            self.network_check(config)
        elif config.command == "wait":
            self.wait_for_port(config)
        elif config.command == "scan":
            self.port_scan(config)
        else:
            self.log_error(f"Unknown command: {config.command}")
            return 1
        
        return 0


def get_arguments(parser: ArgumentParser):
    """인수 정의 (레거시 호환)"""
    cli = NetCLI()
    cli.get_arguments(parser)


def main():
    """메인 함수 (레거시 호환)"""
    cli = NetCLI()
    return cli.main()


if __name__ == '__main__':
    import sys
    import time
    sys.exit(main())