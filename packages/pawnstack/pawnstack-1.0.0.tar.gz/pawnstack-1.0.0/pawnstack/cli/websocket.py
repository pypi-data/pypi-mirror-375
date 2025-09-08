"""
PawnStack WebSocket 연결 도구

WebSocket 연결 테스트 및 모니터링
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from argparse import ArgumentParser

from pawnstack import __version__
from pawnstack.config.global_config import pawn
from pawnstack.cli.base import AsyncBaseCLI
from pawnstack.cli.banner import generate_banner

# 모듈 메타데이터
__description__ = 'WebSocket connection testing and monitoring tool'

__epilog__ = (
    "WebSocket connection testing and monitoring tool.\n\n"
    "Usage examples:\n"
    "  1. Basic connection test:\n\tpawns websocket ws://localhost:8080\n\n"
    "  2. Send message and monitor:\n\tpawns websocket ws://localhost:8080 --message 'Hello World'\n\n"
    "  3. Continuous monitoring:\n\tpawns websocket ws://localhost:8080 --monitor --interval 5\n\n"
    "  4. With custom headers:\n\tpawns websocket ws://localhost:8080 --headers '{\"Authorization\": \"Bearer token\"}'\n\n"
    "For more details, use the -h or --help flag."
)


@dataclass
class WebSocketTask:
    """WebSocket 작업 설정"""
    url: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    message: Optional[str] = None
    timeout: float = 10.0
    ping_interval: float = 30.0
    max_size: int = 1024 * 1024  # 1MB


class WebSocketCLI(AsyncBaseCLI):
    """WebSocket CLI"""
    
    def __init__(self, args=None):
        super().__init__(args)
        self.connection_count = 0
        self.message_count = 0
        self.error_count = 0
        self.response_times = []
    
    def get_arguments(self, parser: ArgumentParser):
        """인수 정의"""
        parser.add_argument('url', help='WebSocket URL to connect to', type=str, nargs='?', default="")
        
        parser.add_argument('-m', '--message', type=str, help='Message to send after connection')
        parser.add_argument('-t', '--timeout', type=float, help='Connection timeout in seconds (default: 10)', default=10)
        parser.add_argument('-i', '--interval', type=float, help='Monitoring interval in seconds (default: 5)', default=5)
        parser.add_argument('--headers', type=str, help='HTTP headers in JSON format')
        parser.add_argument('--ping-interval', type=float, help='WebSocket ping interval (default: 30)', default=30)
        parser.add_argument('--max-size', type=int, help='Maximum message size in bytes (default: 1MB)', default=1024*1024)
        
        parser.add_argument('--monitor', action='store_true', help='Enable continuous monitoring mode')
        parser.add_argument('--once', action='store_true', help='Connect once and exit')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be done without actual connection')
        
        parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                          help='Logging level (default: INFO)', default="INFO")
    
    def setup_config(self):
        """설정 초기화"""
        args = self.args
        app_name = 'websocket'
        
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
            app_name="WebSocket",
            author="PawnStack Team",
            version=__version__,
            font="graffiti"
        )
        print(banner)
    
    def parse_headers(self) -> Dict[str, str]:
        """헤더 파싱"""
        headers = {}
        
        if hasattr(self.args, 'headers') and self.args.headers:
            try:
                headers = json.loads(self.args.headers)
            except Exception as e:
                self.log_warning(f"Failed to parse headers: {e}")
        
        return headers
    
    def create_task(self) -> Optional[WebSocketTask]:
        """WebSocket 작업 생성"""
        if not getattr(self.args, 'url', ''):
            self.log_error("WebSocket URL is required")
            return None
        
        url = self.args.url
        if not url.startswith(('ws://', 'wss://')):
            self.log_error(f"Invalid WebSocket URL: {url}")
            return None
        
        return WebSocketTask(
            url=url,
            headers=self.parse_headers(),
            message=getattr(self.args, 'message', None),
            timeout=getattr(self.args, 'timeout', 10.0),
            ping_interval=getattr(self.args, 'ping_interval', 30.0),
            max_size=getattr(self.args, 'max_size', 1024*1024)
        )
    
    async def test_websocket_connection(self, task: WebSocketTask) -> Dict[str, Any]:
        """WebSocket 연결 테스트"""
        start_time = time.time()
        
        try:
            # websockets 라이브러리가 설치되어 있지 않을 수 있으므로 동적 import
            try:
                import websockets
            except ImportError:
                return {
                    "url": task.url,
                    "error": "websockets library not installed. Install with: pip install websockets",
                    "success": False,
                    "timestamp": time.time()
                }
            
            # WebSocket 연결
            async with websockets.connect(
                task.url,
                extra_headers=task.headers,
                ping_interval=task.ping_interval,
                max_size=task.max_size,
                timeout=task.timeout
            ) as websocket:
                
                connection_time = time.time() - start_time
                self.connection_count += 1
                self.response_times.append(connection_time)
                
                result = {
                    "url": task.url,
                    "connection_time": connection_time,
                    "success": True,
                    "timestamp": time.time(),
                    "messages_sent": 0,
                    "messages_received": 0
                }
                
                # 메시지 전송 (있는 경우)
                if task.message:
                    message_start = time.time()
                    await websocket.send(task.message)
                    self.message_count += 1
                    result["messages_sent"] = 1
                    
                    # 응답 대기 (타임아웃 설정)
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        message_time = time.time() - message_start
                        result["message_time"] = message_time
                        result["response"] = response[:100] + "..." if len(response) > 100 else response
                        result["messages_received"] = 1
                    except asyncio.TimeoutError:
                        result["message_timeout"] = True
                
                return result
                
        except Exception as e:
            self.error_count += 1
            return {
                "url": task.url,
                "error": str(e),
                "connection_time": time.time() - start_time,
                "success": False,
                "timestamp": time.time()
            }
    
    def display_result(self, result: Dict[str, Any]):
        """결과 출력"""
        if 'error' in result:
            pawn.console.log(f"[red]❌ {result['url']} - Error: {result['error']}[/red]")
        else:
            status_icon = "✅" if result.get('success') else "❌"
            
            message = f"{status_icon} {result['url']} - Connection: {result['connection_time']:.3f}s"
            
            if result.get('messages_sent', 0) > 0:
                message += f", Messages: {result['messages_sent']}"
                if 'message_time' in result:
                    message += f", Response: {result['message_time']:.3f}s"
                if result.get('message_timeout'):
                    message += " (timeout)"
            
            color = "green" if result.get('success') else "red"
            pawn.console.log(f"[{color}]{message}[/{color}]")
    
    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보 반환"""
        if not self.response_times:
            return {}
        
        return {
            "total_connections": self.connection_count,
            "total_messages": self.message_count,
            "total_errors": self.error_count,
            "success_rate": ((self.connection_count - self.error_count) / self.connection_count * 100) if self.connection_count > 0 else 0,
            "avg_connection_time": sum(self.response_times) / len(self.response_times),
            "min_connection_time": min(self.response_times),
            "max_connection_time": max(self.response_times),
        }
    
    async def run_monitoring(self, task: WebSocketTask):
        """모니터링 실행"""
        interval = getattr(self.args, 'interval', 5.0)
        
        pawn.console.log(f"🚀 Starting WebSocket monitoring for {task.url}")
        
        if getattr(self.args, 'dry_run', False):
            pawn.console.log(f"[DRY RUN] Would connect to: {task.url}")
            if task.message:
                pawn.console.log(f"[DRY RUN] Would send message: {task.message}")
            return
        
        try:
            if getattr(self.args, 'once', False):
                # 한 번만 연결
                result = await self.test_websocket_connection(task)
                self.display_result(result)
            else:
                # 연속 모니터링
                while True:
                    result = await self.test_websocket_connection(task)
                    self.display_result(result)
                    
                    # 통계 출력
                    if self.connection_count > 0:
                        stats = self.get_statistics()
                        pawn.console.log(f"📊 Stats: {stats['total_connections']} connections, "
                                       f"{stats['total_errors']} errors, {stats['success_rate']:.1f}% success, "
                                       f"avg: {stats['avg_connection_time']:.3f}s")
                    
                    await asyncio.sleep(interval)
                    
        except KeyboardInterrupt:
            self.log_info("WebSocket monitoring stopped by user")
    
    async def run_async(self) -> int:
        """WebSocket CLI 실행"""
        self.setup_config()
        self.print_banner()
        
        # 작업 생성
        task = self.create_task()
        if not task:
            return 1
        
        # 모니터링 실행
        await self.run_monitoring(task)
        
        return 0


def get_arguments(parser: ArgumentParser):
    """인수 정의 (레거시 호환)"""
    cli = WebSocketCLI()
    cli.get_arguments(parser)


def main():
    """메인 함수 (레거시 호환)"""
    cli = WebSocketCLI()
    return cli.main()


if __name__ == '__main__':
    import sys
    sys.exit(main())