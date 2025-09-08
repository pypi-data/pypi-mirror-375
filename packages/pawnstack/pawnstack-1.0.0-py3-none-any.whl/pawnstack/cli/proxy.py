"""
PawnStack Proxy 도구

HTTP 프록시 및 리플렉터 서버
"""

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional
from argparse import ArgumentParser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

from pawnstack import __version__
from pawnstack.config.global_config import pawn
from pawnstack.cli.base import BaseCLI
from pawnstack.cli.banner import generate_banner

# 모듈 메타데이터
__description__ = 'HTTP proxy and reflector server'

__epilog__ = (
    "HTTP proxy and reflector server for testing and debugging.\n\n"
    "Usage examples:\n"
    "  1. Start reflector server:\n\tpawns proxy --reflector --port 8080\n\n"
    "  2. Start proxy server:\n\tpawns proxy --proxy --port 8080 --target http://example.com\n\n"
    "  3. Enable request logging:\n\tpawns proxy --reflector --port 8080 --log-requests\n\n"
    "  4. Add custom headers:\n\tpawns proxy --reflector --port 8080 --headers '{\"X-Custom\": \"value\"}'\n\n"
    "For more details, use the -h or --help flag."
)


class ReflectorHandler(BaseHTTPRequestHandler):
    """HTTP 리플렉터 핸들러"""
    
    def __init__(self, *args, custom_headers=None, log_requests=False, **kwargs):
        self.custom_headers = custom_headers or {}
        self.log_requests = log_requests
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        self._handle_request()
    
    def do_POST(self):
        self._handle_request()
    
    def do_PUT(self):
        self._handle_request()
    
    def do_DELETE(self):
        self._handle_request()
    
    def do_PATCH(self):
        self._handle_request()
    
    def do_HEAD(self):
        self._handle_request()
    
    def do_OPTIONS(self):
        self._handle_request()
    
    def _handle_request(self):
        """요청 처리"""
        try:
            # 요청 본문 읽기
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b''
            
            # 응답 데이터 생성
            response_data = {
                "method": self.command,
                "path": self.path,
                "headers": dict(self.headers),
                "body": body.decode('utf-8', errors='ignore') if body else "",
                "timestamp": time.time(),
                "client_address": self.client_address[0]
            }
            
            # 요청 로깅
            if self.log_requests:
                pawn.console.log(f"📥 {self.command} {self.path} from {self.client_address[0]}")
            
            # 응답 전송
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            
            # 커스텀 헤더 추가
            for key, value in self.custom_headers.items():
                self.send_header(key, value)
            
            # CORS 헤더 추가
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            
            response_json = json.dumps(response_data, indent=2)
            self.send_header('Content-Length', str(len(response_json)))
            self.end_headers()
            
            if self.command != 'HEAD':
                self.wfile.write(response_json.encode('utf-8'))
                
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def log_message(self, format, *args):
        """로그 메시지 오버라이드 (기본 로깅 비활성화)"""
        pass


class ProxyCLI(BaseCLI):
    """Proxy CLI"""
    
    def __init__(self, args=None):
        super().__init__(args)
        self.server = None
        self.server_thread = None
    
    def get_arguments(self, parser: ArgumentParser):
        """인수 정의"""
        parser.add_argument('-p', '--port', type=int, help='Server port (default: 8080)', default=8080)
        parser.add_argument('--host', type=str, help='Server host (default: 0.0.0.0)', default='0.0.0.0')
        
        # 서버 모드
        parser.add_argument('--reflector', action='store_true', help='Start HTTP reflector server')
        parser.add_argument('--proxy', action='store_true', help='Start HTTP proxy server')
        
        # 프록시 설정
        parser.add_argument('--target', type=str, help='Target URL for proxy mode')
        
        # 추가 옵션
        parser.add_argument('--headers', type=str, help='Custom headers in JSON format')
        parser.add_argument('--log-requests', action='store_true', help='Log incoming requests')
        parser.add_argument('--timeout', type=int, help='Request timeout in seconds (default: 30)', default=30)
        
        parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                          help='Logging level (default: INFO)', default="INFO")
    
    def setup_config(self):
        """설정 초기화"""
        args = self.args
        app_name = 'proxy'
        
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
            app_name="Proxy",
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
    
    def create_reflector_handler(self):
        """리플렉터 핸들러 생성"""
        custom_headers = self.parse_headers()
        log_requests = getattr(self.args, 'log_requests', False)
        
        class CustomReflectorHandler(ReflectorHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, custom_headers=custom_headers, log_requests=log_requests, **kwargs)
        
        return CustomReflectorHandler
    
    def start_reflector_server(self):
        """리플렉터 서버 시작"""
        host = getattr(self.args, 'host', '0.0.0.0')
        port = getattr(self.args, 'port', 8080)
        
        handler_class = self.create_reflector_handler()
        
        try:
            self.server = HTTPServer((host, port), handler_class)
            
            pawn.console.log(f"🚀 Starting HTTP Reflector Server")
            pawn.console.log(f"📡 Listening on http://{host}:{port}")
            pawn.console.log(f"💡 Send requests to see them reflected back as JSON")
            pawn.console.log(f"⏹️  Press Ctrl+C to stop")
            
            # 서버를 별도 스레드에서 실행
            def run_server():
                self.server.serve_forever()
            
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            
            # 메인 스레드에서 대기
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.log_info("Shutting down reflector server...")
                self.server.shutdown()
                self.server.server_close()
                
        except OSError as e:
            if "Address already in use" in str(e):
                self.log_error(f"Port {port} is already in use")
                return 1
            else:
                self.log_error(f"Failed to start server: {e}")
                return 1
        except Exception as e:
            self.log_error(f"Server error: {e}")
            return 1
        
        return 0
    
    def start_proxy_server(self):
        """프록시 서버 시작 (향후 구현)"""
        target = getattr(self.args, 'target', None)
        
        if not target:
            self.log_error("Target URL is required for proxy mode (--target)")
            return 1
        
        self.log_error("Proxy mode is not implemented yet. Use --reflector for now.")
        return 1
    
    def run(self) -> int:
        """Proxy CLI 실행"""
        self.setup_config()
        self.print_banner()
        
        # 모드 확인
        if getattr(self.args, 'reflector', False):
            return self.start_reflector_server()
        elif getattr(self.args, 'proxy', False):
            return self.start_proxy_server()
        else:
            self.log_error("Please specify --reflector or --proxy mode")
            return 1


def get_arguments(parser: ArgumentParser):
    """인수 정의 (레거시 호환)"""
    cli = ProxyCLI()
    cli.get_arguments(parser)


def main():
    """메인 함수 (레거시 호환)"""
    cli = ProxyCLI()
    return cli.main()


if __name__ == '__main__':
    import sys
    sys.exit(main())