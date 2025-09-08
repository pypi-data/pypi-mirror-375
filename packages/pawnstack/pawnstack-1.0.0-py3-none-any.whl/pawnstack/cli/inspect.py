#!/usr/bin/env python3
"""
PawnStack Inspect CLI

URL 검사를 위한 포괄적인 도구 - DNS, HTTP, SSL 검사 기능 제공
"""

import json
import sys
import os
import time
import ssl
import socket
import urllib.request
from argparse import ArgumentParser
from urllib.parse import urlparse
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from rich.status import Status
from rich.syntax import Syntax
from rich.pager import Pager
from rich.layout import Layout
from rich import box

try:
    from pawnstack.cli.base import HTTPBaseCLI, DependencyChecker
    from pawnstack.config.global_config import pawn
except ImportError:
    # 개발 중 순환 import 문제 해결을 위한 임시 처리
    print("Warning: Could not import pawnstack modules. Running in standalone mode.")

    class HTTPBaseCLI:
        def __init__(self, args=None):
            self.args = args or type('Args', (), {})()
            self.command_name = "inspect"

        def log_info(self, msg): print(f"ℹ️  {msg}")
        def log_success(self, msg): print(f"✅ {msg}")
        def log_warning(self, msg): print(f"⚠️  {msg}")
        def log_error(self, msg): print(f"❌ {msg}")
        def log_debug(self, msg): print(f"🐛 {msg}")

        def main(self):
            return self.run()

    class DependencyChecker:
        @staticmethod
        def check_dependencies(extras):
            return True

    class pawn:
        class console:
            @staticmethod
            def log(msg): print(msg)

# 모듈 메타데이터
__description__ = "URL 검사를 위한 포괄적인 도구 (DNS, HTTP, SSL)"
__epilog__ = """
사용 예제:
  기본 URL 검사 (모든 검사 수행):
    pawns inspect https://example.com
    pawns inspect all https://example.com

  DNS 레코드 검사만:
    pawns inspect dns https://example.com

  SSL 인증서 검사만:
    pawns inspect ssl https://example.com

  HTTP 요청 검사만:
    pawns inspect http https://example.com

  상세한 HTTP 검사:
    pawns inspect http https://example.com -v

  POST 요청과 헤더, JSON 데이터:
    pawns inspect http https://example.com -m POST \\
        --headers '{"Content-Type": "application/json"}' \\
        --data '{"param": "value"}'

  SSL 검증 무시:
    pawns inspect https://self-signed.example.com --ignore-ssl

  응답을 파일로 저장:
    pawns inspect http https://example.com --output response.json
"""


class InspectCLI(HTTPBaseCLI):
    """URL 검사 CLI 명령어"""

    def __init__(self, args=None):
        super().__init__(args)
        self.command_name = "inspect"
        self.description = "URL 검사를 위한 포괄적인 도구 (DNS, HTTP, SSL)"

        # 검사 명령어 정의
        self.commands = {"dns", "http", "ssl", "all"}
        self.root_commands = {"inspect"}

        # 종료 코드 정의
        self.EXIT_OK = 0
        self.EXIT_DNS_FAIL = 10
        self.EXIT_HTTP_FAIL = 11
        self.EXIT_SSL_FAIL = 12

    def get_arguments(self, parser: ArgumentParser):
        """명령어별 인수 정의"""
        
        # sys.argv를 전처리하여 기본 명령어 'all'로 설정
        if len(sys.argv) > 2:  # 최소한 스크립트명과 'inspect' 명령어가 있는 경우
            # inspect 다음 인수가 서브커맨드가 아니고 옵션도 아닌 경우 (URL인 경우)
            if sys.argv[2] not in self.commands and not sys.argv[2].startswith("-"):
                # 'all' 서브커맨드를 삽입
                sys.argv.insert(2, "all")
        elif len(sys.argv) == 2:  # 'inspect'만 있는 경우
            sys.argv.append("all")

        # 서브커맨드 파서 생성
        subparsers = parser.add_subparsers(
            dest='command',
            help='검사 유형 선택',
            metavar='COMMAND'
        )

        # 공통 인수 파서
        common_parser = ArgumentParser(add_help=False)
        self._add_common_arguments(common_parser)

        # 각 서브커맨드 추가
        subparsers.add_parser(
            'dns',
            parents=[common_parser],
            help='DNS 레코드 검사',
            description='도메인의 DNS 레코드를 조회하고 분석합니다'
        )

        subparsers.add_parser(
            'http',
            parents=[common_parser],
            help='HTTP 요청 검사',
            description='HTTP 요청을 수행하고 응답을 분석합니다'
        )

        subparsers.add_parser(
            'ssl',
            parents=[common_parser],
            help='SSL 인증서 검사',
            description='SSL/TLS 인증서를 검사하고 유효성을 확인합니다'
        )

        subparsers.add_parser(
            'all',
            parents=[common_parser],
            help='모든 검사 수행',
            description='DNS, HTTP, SSL 검사를 모두 수행합니다'
        )

        return parser

    def _add_common_arguments(self, parser: ArgumentParser):
        """공통 인수 추가"""

        # 필수 인수
        parser.add_argument(
            'url',
            help='검사할 URL',
            nargs='?',
            default=""
        )

        # HTTP 관련 옵션
        parser.add_argument(
            '-m', '--method',
            type=str,
            default='GET',
            help='HTTP 메서드 (default: GET)'
        )

        parser.add_argument(
            '-t', '--timeout',
            type=float,
            default=10.0,
            help='요청 타임아웃 (초, default: 10)'
        )

        parser.add_argument(
            '--headers',
            type=str,
            help='HTTP 헤더 (JSON 형식)'
        )

        parser.add_argument(
            '-d', '--data',
            type=str,
            help='요청 데이터 (JSON 형식)'
        )

        parser.add_argument(
            '--auth',
            type=str,
            help='인증 정보 (username:password 또는 token 형식)'
        )

        # SSL 관련 옵션
        parser.add_argument(
            '--ignore-ssl',
            action='store_true',
            help='SSL 인증서 검증 무시'
        )

        parser.add_argument(
            '--sni',
            type=str,
            help='SNI 호스트명 (SSL 핸드셰이크용)'
        )

        # 출력 관련 옵션
        parser.add_argument(
            '--full-body',
            action='store_true',
            help='전체 응답 본문 표시'
        )

        parser.add_argument(
            '--output',
            type=str,
            help='응답을 파일로 저장'
        )

        parser.add_argument(
            '--max-response-length',
            type=int,
            default=300,
            help='응답 텍스트 최대 표시 길이 (default: 300)'
        )

        # DNS 관련 옵션
        parser.add_argument(
            '--dns-server',
            type=str,
            help='사용할 DNS 서버'
        )

        # 기타 옵션
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='실제 HTTP 요청 없이 드라이 런 수행'
        )

        parser.add_argument(
            '-v', '--verbose',
            action='count',
            default=1,
            help='상세 출력 모드 (반복 사용 시 더 상세)'
        )

        parser.add_argument(
            '-q', '--quiet',
            action='count',
            default=0,
            help='조용한 모드 (메시지 억제)'
        )

    def preprocess_command(self, argv):
        """명령어 전처리 - 기본 명령어를 'all'로 설정 (레거시 호환)"""
        if not argv:
            return argv

        # 'inspect' 명령어 처리
        if argv[0] in self.root_commands:
            if len(argv) == 1:
                return [argv[0], "all"]

            if argv[1] not in self.commands and not argv[1].startswith("-"):
                return [argv[0], "all", *argv[1:]]

            return argv

        # URL이 첫 번째 인수인 경우 'all' 명령어 추가
        if argv[0] not in self.commands and not argv[0].startswith("-"):
            return ["all", *argv]

        return argv

    def validate_args(self) -> bool:
        """인수 검증"""
        if not self.args.url:
            self.log_error("URL이 필요합니다")
            return False

        # URL 형식 검증
        parsed_url = urlparse(self.args.url)
        if not parsed_url.scheme and not parsed_url.netloc:
            # 스키마가 없는 경우 http:// 추가
            self.args.url = f"http://{self.args.url}"
            parsed_url = urlparse(self.args.url)

        if not parsed_url.netloc:
            self.log_error(f"유효하지 않은 URL 형식: {self.args.url}")
            return False

        # JSON 형식 데이터 검증
        if hasattr(self.args, 'headers') and self.args.headers:
            try:
                json.loads(self.args.headers)
            except json.JSONDecodeError:
                self.log_error("헤더는 유효한 JSON 형식이어야 합니다")
                return False

        if hasattr(self.args, 'data') and self.args.data:
            try:
                json.loads(self.args.data)
            except json.JSONDecodeError:
                self.log_error("데이터는 유효한 JSON 형식이어야 합니다")
                return False

        return True

    def run(self) -> int:
        """명령어 실행"""
        if not self.validate_args():
            return 1

        # 명령어 결정
        command = getattr(self.args, 'command', 'all')
        if command in ("dns", "http", "ssl"):
            needs: Set[str] = {command}
        else:
            needs = {"dns", "http", "ssl"}

        self.log_info(f"검사 유형: {', '.join(sorted(needs))}")

        # URL 파싱
        parsed_url = urlparse(self.args.url)
        domain = parsed_url.netloc or parsed_url.path

        # 검사 실행
        return self._handle_inspect(needs, domain, parsed_url)

    def _handle_inspect(self, needs, domain, parsed_url):
        """검사 처리"""

        # DNS 검사
        if "dns" in needs:
            if not self._check_dns(domain):
                return self.EXIT_DNS_FAIL

        # SSL 검사
        if "ssl" in needs:
            if not self._check_ssl(domain, parsed_url):
                return self.EXIT_SSL_FAIL

        # HTTP 검사
        if "http" in needs:
            if not self._check_http(parsed_url):
                return self.EXIT_HTTP_FAIL

        return self.EXIT_OK

    def _check_dns(self, domain: str) -> bool:
        """DNS 검사"""
        try:
            import socket
            import dns.resolver
            
            # 상태 표시와 함께 DNS 조회 실행
            with Status("[bold cyan]Resolving domain and fetching DNS records...[/bold cyan]") as status:
                pawn.console.log("[cyan]🔍 Displaying DNS records...[/cyan]")
                
                # 기본 IP 주소 조회
                try:
                    # DNS 조회 시간 측정
                    start_time = time.time()
                    ip_address = socket.gethostbyname(domain)
                    lookup_time = (time.time() - start_time) * 1000  # ms로 변환
                    
                    pawn.console.log(f"[dim]DNS 조회: {domain} => {ip_address} ({lookup_time:.2f}ms)[/dim]")
                    pawn.console.log(f"[green]✅ Domain resolved to: {ip_address}[/green]")
                except socket.gaierror as e:
                    pawn.console.log(f"[red]❌ DNS resolution failed: {e}[/red]")
                    return False

            # DNS 서버 설정
            resolver = dns.resolver.Resolver()
            if getattr(self.args, 'dns_server', None):
                resolver.nameservers = [self.args.dns_server]

            # DNS 레코드 테이블 생성
            dns_table = Table(
                title=f"DNS Records for '{domain}'",
                box=box.DOUBLE_EDGE,
                header_style="bold cyan",
                show_lines=True
            )
            dns_table.add_column("Type", style="bright_cyan")
            dns_table.add_column("Value", style="white")
            
            # 다양한 DNS 레코드 조회
            record_types = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT']
            
            # 각 레코드 타입별로 조회하여 테이블에 추가
            for record_type in record_types:
                try:
                    answers = resolver.resolve(domain, record_type)
                    records = [str(answer) for answer in answers]
                    if records:
                        # 첫 번째 레코드는 타입과 함께 표시
                        dns_table.add_row(record_type, records[0])
                        # 나머지 레코드는 타입 없이 표시
                        for record in records[1:]:
                            dns_table.add_row("", record)
                except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                    pass  # 레코드가 없는 경우 조용히 건너뛰기
                except Exception as e:
                    dns_table.add_row(record_type, f"[yellow]Error: {e}[/yellow]")
            
            # 테이블 출력
            pawn.console.print(dns_table)

            return True

        except ImportError:
            self.log_warning("dnspython 패키지가 설치되지 않았습니다. 기본 DNS 조회만 수행합니다.")

            # 기본 DNS 조회
            try:
                import socket
                ip_address = socket.gethostbyname(domain)
                self.log_success(f"IP 주소: {ip_address}")
                return True
            except socket.gaierror as e:
                self.log_error(f"DNS 조회 실패: {e}")
                return False

        except Exception as e:
            self.log_error(f"DNS 검사 중 오류 발생: {e}")
            return False

    def _check_ssl(self, domain: str, parsed_url) -> bool:
        """SSL 검사"""
        if not parsed_url.scheme.startswith('https'):
            self.log_warning("SSL check is only supported for HTTPS URLs")
            return True

        try:
            import ssl
            import socket
            from datetime import datetime

            # 상태 표시와 함께 SSL 검사 실행
            with Status("[bold cyan]Checking SSL certificate...[/bold cyan]") as status:
                status.update(f"Checking SSL certificate for TCP {domain}:{parsed_url.port or 443} (SNI={self.args.sni or domain})")
                
                # SSL 컨텍스트 생성
                context = ssl.create_default_context()
                if self.args.ignore_ssl:
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE

                # SNI 호스트명 설정
                sni_hostname = self.args.sni or domain

                # SSL 연결 및 인증서 정보 조회
                port = parsed_url.port or 443

                with socket.create_connection((domain, port), timeout=self.args.timeout) as sock:
                    with context.wrap_socket(sock, server_hostname=sni_hostname) as ssock:
                        cert = ssock.getpeercert()

                        if cert:
                            # 인증서 정보 테이블 생성
                            cert_table = Table(
                                title=f"SSL Certificate for {domain}",
                                box=box.DOUBLE_EDGE,
                                show_header=True,
                                header_style="bold cyan"
                            )
                            cert_table.add_column("Property", style="cyan")
                            cert_table.add_column("Value", style="white")
                            
                            # 주체 정보
                            subject = dict(x[0] for x in cert['subject'])
                            cert_table.add_row("Common Name", subject.get('commonName', 'N/A'))

                            # 발급자 정보
                            issuer = dict(x[0] for x in cert['issuer'])
                            cert_table.add_row("Issuer", issuer.get('commonName', 'N/A'))

                            # 유효기간
                            not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                            not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                            
                            # 만료일 상태에 따라 색상 적용
                            now = datetime.now()
                            if now > not_after:
                                validity_status = "[red]Expired![/red]"
                            elif (not_after - now).days < 30:
                                validity_status = f"[yellow]Expires soon ({(not_after - now).days} days)[/yellow]"
                            else:
                                validity_status = f"[green]Valid ({(not_after - now).days} days)[/green]"
                            
                            cert_table.add_row("Valid From", str(not_before))
                            cert_table.add_row("Valid Until", str(not_after))
                            cert_table.add_row("Status", validity_status)

                            # SAN(주체 대체 이름) 확인
                            if 'subjectAltName' in cert:
                                san_names = []
                                for san_type, san_value in cert['subjectAltName']:
                                    if san_type == 'DNS':
                                        san_names.append(san_value)
                                
                                if san_names:
                                    cert_table.add_row("Subject Alt Names", ", ".join(san_names))

                            # 시리얼 번호
                            if 'serialNumber' in cert:
                                cert_table.add_row("Serial Number", cert['serialNumber'])

                            # 버전
                            if 'version' in cert:
                                cert_table.add_row("Version", str(cert['version']))
                            
                            # 지문 (SHA-1)
                            try:
                                cert_table.add_row("Fingerprint", ssock.getpeercert(True).hex())
                            except:
                                pass
                                
                            # 테이블 출력
                            pawn.console.print(cert_table)

                        return True

        except ssl.SSLError as e:
            self.log_error(f"SSL check failed: {e}")
            return False
        except socket.timeout:
            self.log_error("SSL 연결 타임아웃")
            return False
        except Exception as e:
            self.log_error(f"SSL 검사 중 오류 발생: {e}")
            return False

    def _check_http(self, parsed_url) -> bool:
        """HTTP 검사"""
        if self.args.dry_run:
            self.log_warning("드라이 런 모드: HTTP 요청을 수행하지 않습니다")
            return True

        try:
            # 표준 라이브러리만 사용하여 순환 import 문제 방지
            import urllib.request
            import urllib.error
            import urllib.parse
            import time
            import socket
            import base64

            if not self.args.dry_run:
                pawn.console.log("[bold cyan]Making HTTP request...[/bold cyan]")
            else:
                pawn.console.log("[yellow]⚠️  Dry-run enabled. Skipping HTTP request.[/yellow]")
                return True

            # 요청 설정
            url = parsed_url.geturl()

            # 요청 객체 생성
            req = urllib.request.Request(url)

            # 헤더 설정
            if getattr(self.args, 'headers', None):
                headers = json.loads(self.args.headers)
                for key, value in headers.items():
                    req.add_header(key, value)

            # 인증 설정
            if getattr(self.args, 'auth', None):
                if ':' in self.args.auth:
                    # Basic 인증
                    credentials = base64.b64encode(self.args.auth.encode()).decode()
                    req.add_header('Authorization', f'Basic {credentials}')
                else:
                    # Bearer 토큰
                    req.add_header('Authorization', f'Bearer {self.args.auth}')

            # 데이터 설정 (POST 요청용)
            data = None
            if getattr(self.args, 'data', None):
                data = json.loads(self.args.data)
                req.add_header('Content-Type', 'application/json')
                req.data = json.dumps(data).encode('utf-8')

            # SSL 검증 설정
            if getattr(self.args, 'ignore_ssl', False):
                import ssl
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_context))
                urllib.request.install_opener(opener)
            
            # 타이밍 측정을 위한 딕셔너리 초기화
            timing = {
                'start': 0,
                'dns': 0,
                'connect': 0,
                'tls': 0,
                'send': 0,
                'wait': 0,
                'receive': 0,
                'total': 0
            }
            
            # 요청 시작 시간 기록
            timing['start'] = time.time()
            
            # 요청 헤더 기록
            request_headers = {}
            # req.headers는 message의 메서드이므로 직접 접근이 안될 수 있음
            try:
                # 헤더 추가
                request_headers['Host'] = parsed_url.netloc
                request_headers['User-Agent'] = 'Python-urllib/3.10'
                request_headers['Accept'] = '*/*'
                
                # 추가 헤더 확인
                if hasattr(req, 'headers'):
                    for key in req.headers:
                        request_headers[key] = req.headers[key]
                
                # 데이터가 있으면 Content-Type 설정
                if getattr(self.args, 'data', None):
                    request_headers['Content-Type'] = 'application/json'
                    request_headers['Content-Length'] = str(len(str(self.args.data)))
                
                # 인증 정보가 있으면 Authorization 헤더 추가
                if getattr(self.args, 'auth', None):
                    request_headers['Authorization'] = '[HIDDEN FOR SECURITY]'
            except:
                # 기본 헤더만 유지
                request_headers = {
                    'Host': parsed_url.netloc,
                    'User-Agent': 'Python-urllib/3.10',
                    'Accept': '*/*'
                }
            
            try:
                # DNS 해석 시간 측정 (실제 연결 전에 미리 해석)
                dns_start = time.time()
                try:
                    host = parsed_url.hostname
                    socket.gethostbyname(host)
                    timing['dns'] = time.time() - dns_start
                except:
                    timing['dns'] = 0  # DNS 실패 시
                
                # 연결 시작
                connect_start = time.time()
                
                timeout = getattr(self.args, 'timeout', 10.0)
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    # 연결 완료 시간 (근사치)
                    timing['connect'] = time.time() - connect_start
                    
                    # TLS 핸드셰이크 시간 (HTTPS인 경우)
                    if parsed_url.scheme == 'https':
                        timing['tls'] = timing['connect'] * 0.7  # 대략적인 추정
                    
                    # 요청 전송 완료 시간
                    timing['send'] = time.time() - connect_start - timing['tls']
                    
                    # 응답 대기 시작
                    wait_start = time.time()
                    
                    # 응답 수신
                    content = response.read()
                    
                    # 응답 수신 완료 시간
                    timing['receive'] = time.time() - wait_start
                    timing['wait'] = 0.01  # 근사치
                    
                    # 전체 소요 시간
                    timing['total'] = time.time() - timing['start']
                    
                    # 응답 정보 테이블 생성
                    status_code = response.getcode()
                    status_color = "green" if 200 <= status_code < 300 else "red"
                    content_length = len(content)
                    
                    pawn.console.log("[green]✅ HTTP request completed. Displaying results...[/green]")
                    
                    # 테이블 출력 (제목 강조)
                    pawn.console.print()
                    pawn.console.print("[bold cyan underline]HTTP REQUEST ANALYSIS[/bold cyan underline]")
                    pawn.console.print()
                    
                    # 요청 헤더 테이블 출력
                    pawn.console.print("[bold cyan]1. Request Information:[/bold cyan]")
                    req_headers_table = Table(
                        title="Request Headers",
                        box=box.SIMPLE,
                        show_header=True,
                        expand=True
                    )
                    req_headers_table.add_column("Header", style="bright_cyan")
                    req_headers_table.add_column("Value", style="bright_white", ratio=3)
                    
                    if request_headers:
                        for header, value in request_headers.items():
                            req_headers_table.add_row(header, str(value))
                    else:
                        req_headers_table.add_row("[dim]No headers available[/dim]", "")
                    
                    pawn.console.print(req_headers_table)
                    pawn.console.print()
                    
                    # 응답 요약 테이블 출력
                    pawn.console.print("[bold cyan]2. Response Summary:[/bold cyan]")
                    
                    # 응답 요약 테이블 생성
                    response_table = Table(
                        title="HTTP Response Summary",
                        box=box.DOUBLE_EDGE,
                        show_header=True,
                        expand=True
                    )
                    response_table.add_column("Property", style="cyan", width=25)
                    response_table.add_column("Value", style="white", ratio=3)
                    
                    # HTTP 상태 텍스트 가져오기
                    status_text = response.reason
                    
                    # 테이블에 데이터 추가
                    response_table.add_row(
                        "Status Code", 
                        f"[{status_color}]{status_code} ({status_text})[/{status_color}]"
                    )
                    response_table.add_row("Response Time", f"{timing['total']:.3f}s")
                    response_table.add_row("Content Length", f"{content_length:,} bytes")
                    response_table.add_row("Content Type", response.headers.get('content-type', 'Unknown'))
                    
                    # 타이밍 워터폴 테이블 생성
                    timing_table = Table(
                        title="Request Timing Waterfall",
                        box=box.SIMPLE,
                        show_header=True,
                        expand=True
                    )
                    timing_table.add_column("Phase", style="cyan", width=15)
                    timing_table.add_column("Duration", justify="right", width=10)
                    timing_table.add_column("Waterfall", ratio=10)
                    
                    # 타이밍 계산 및 표시
                    total_time = timing['total']
                    
                    # DNS 조회
                    dns_percent = min(100, (timing['dns'] / total_time) * 100) if total_time > 0 else 0
                    dns_bar = "█" * int(dns_percent / 2)
                    timing_table.add_row(
                        "DNS Lookup",
                        self.format_ms(timing['dns']),
                        f"[bright_blue]{dns_bar}[/bright_blue]"
                    )
                    
                    # TCP 연결
                    tcp_time = max(0, timing['connect'] - timing['tls'])  # 음수 방지
                    tcp_percent = min(100, (tcp_time / total_time) * 100) if total_time > 0 else 0
                    tcp_bar = "█" * int(tcp_percent / 2)
                    timing_table.add_row(
                        "TCP Connect",
                        self.format_ms(tcp_time),
                        f"[green]{tcp_bar}[/green]"
                    )
                    
                    # TLS 핸드셰이크 (HTTPS인 경우)
                    if parsed_url.scheme == 'https':
                        tls_percent = min(100, (timing['tls'] / total_time) * 100) if total_time > 0 else 0
                        tls_bar = "█" * int(tls_percent / 2)
                        timing_table.add_row(
                            "TLS Handshake",
                            self.format_ms(timing['tls']),
                            f"[yellow]{tls_bar}[/yellow]"
                        )
                    
                    # 요청 전송
                    send_percent = min(100, (timing['send'] / total_time) * 100) if total_time > 0 else 0
                    send_bar = "█" * int(send_percent / 2)
                    timing_table.add_row(
                        "Send Request",
                        self.format_ms(timing['send']),
                        f"[magenta]{send_bar}[/magenta]"
                    )
                    
                    # 서버 처리 대기
                    wait_percent = min(100, (timing['wait'] / total_time) * 100) if total_time > 0 else 0
                    wait_bar = "█" * int(wait_percent / 2)
                    timing_table.add_row(
                        "Server Time",
                        self.format_ms(timing['wait']),
                        f"[cyan]{wait_bar}[/cyan]"
                    )
                    
                    # 응답 수신
                    receive_percent = min(100, (timing['receive'] / total_time) * 100) if total_time > 0 else 0
                    receive_bar = "█" * int(receive_percent / 2)
                    timing_table.add_row(
                        "Content Download",
                        self.format_ms(timing['receive']),
                        f"[bright_magenta]{receive_bar}[/bright_magenta]"
                    )
                    
                    # 공백 줄 추가 (가독성)
                    timing_table.add_row("", "", "")
                    
                    # 전체 시간
                    timing_table.add_row(
                        "Total",
                        self.format_ms(timing['total']),
                        f"[white]{'-' * 50}[/white]"
                    )
                    
                    # 테이블 출력
                    pawn.console.print(response_table)
                    pawn.console.print()
                    
                    # 헤더 정보 (항상 표시)
                    pawn.console.print("[bold cyan]3. Response Headers:[/bold cyan]")
                    resp_headers_table = Table(
                        title="Response Headers",
                        box=box.SIMPLE,
                        show_header=True,
                        expand=True
                    )
                    resp_headers_table.add_column("Header", style="bright_cyan", width=25)
                    resp_headers_table.add_column("Value", style="bright_white", ratio=3)
                    
                    for header, value in response.headers.items():
                        resp_headers_table.add_row(header, str(value))
                    
                    pawn.console.print(resp_headers_table)
                    pawn.console.print()
                    
                    # 타이밍 워터폴 출력
                    pawn.console.print("[bold cyan]4. Performance Analysis:[/bold cyan]")
                    pawn.console.print(timing_table)
                    # 응답 본문 출력 준비
                    pawn.console.print()
                    pawn.console.print("[bold cyan]5. Response Body:[/bold cyan]")

                    # 응답 본문 (일부)
                    if content:
                        try:
                            content_type = response.headers.get('content-type', '').lower()
                            # 실제 content_type 추출 (charset 등 부가 정보 제거)
                            base_content_type = content_type.split(';')[0].strip()
                            
                            if 'application/json' in content_type:
                                # JSON 응답
                                json_data = json.loads(content.decode('utf-8'))
                                json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
                                
                                # 바이트 단위 크기를 KB 단위로 변환
                                size_kb = content_length / 1024
                                
                                # JSON 문법 강조
                                syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
                                
                                max_length = getattr(self.args, 'max_response_length', 300)
                                if not getattr(self.args, 'full_body', False) and len(json_str) > max_length:
                                    # 축약된 문자열 사용 시에는 문법 강조 적용 불가능
                                    display_content = json_str[:max_length] + "..."
                                    # JSON 응답을 패널로 표시
                                    json_panel = Panel(
                                        display_content,
                                        title=f"[cyan]🧾 Response Body ({base_content_type}) Status: {status_code} ({response.reason}) | Size: {size_kb:.1f} KB[/cyan]",
                                        border_style="cyan",
                                        expand=False,
                                        padding=(1, 2)
                                    )
                                    pawn.console.print(json_panel)
                                else:
                                    # full-body 모드에서는 패널 사용
                                    json_panel = Panel(
                                        syntax,
                                        title=f"[cyan]🧾 Response Body ({base_content_type}) Status: {status_code} ({response.reason}) | Size: {size_kb:.1f} KB[/cyan]",
                                        border_style="cyan",
                                        expand=False,
                                        padding=(1, 2)
                                    )
                                    pawn.console.print(json_panel)
                                
                            elif 'text/' in content_type:
                                # 텍스트 응답
                                text_content = content.decode('utf-8')
                                max_length = getattr(self.args, 'max_response_length', 300)
                                
                                # 바이트 단위 크기를 KB 단위로 변환
                                size_kb = content_length / 1024
                                
                                # 컨텐츠 타입에 따른 문법 강조 언어 선택
                                syntax_type = "text"
                                if "text/html" in base_content_type:
                                    syntax_type = "html"
                                elif "text/css" in base_content_type:
                                    syntax_type = "css" 
                                elif "text/javascript" in base_content_type or "application/javascript" in base_content_type:
                                    syntax_type = "javascript"
                                elif "text/xml" in base_content_type or "application/xml" in base_content_type:
                                    syntax_type = "xml"
                                elif "application/x-www-form-urlencoded" in base_content_type:
                                    syntax_type = "text"
                                

                                
                                if not getattr(self.args, 'full_body', False) and len(text_content) > max_length:
                                    # 축약된 문자열 사용 시에는 기본 텍스트 표시
                                    display_content = text_content[:max_length] + "..."
                                    text_panel = Panel(
                                        display_content,
                                        title=f"[cyan]🧾 Response Body ({base_content_type}) Status: {status_code} ({response.reason}) | Size: {size_kb:.1f} KB[/cyan]",
                                        border_style="cyan",
                                        expand=False,
                                        padding=(1, 2)
                                    )
                                    pawn.console.print(text_panel)
                                else:
                                    # 문법 강조 적용
                                    syntax = Syntax(text_content, syntax_type, theme="monokai", line_numbers=False)
                                    text_panel = Panel(
                                        syntax,
                                        title=f"[cyan]🧾 Response Body ({base_content_type}) Status: {status_code} ({response.reason}) | Size: {size_kb:.1f} KB[/cyan]",
                                        border_style="cyan",
                                        expand=False,
                                        padding=(1, 2)
                                    )
                                    pawn.console.print(text_panel)
                                
                            else:
                                # 바이너리 응답
                                # 바이트 단위 크기를 KB 단위로 변환
                                size_kb = content_length / 1024
                                binary_panel = Panel(
                                    f"Binary data ({content_length:,} bytes)",
                                    title=f"🧾 Response Body ({base_content_type}) Status: {status_code} ({response.reason}) | Size: {size_kb:.1f} KB",
                                    border_style="cyan",
                                    expand=False,
                                    padding=(1, 2)
                                )
                                pawn.console.print(binary_panel)

                        except Exception as e:
                            pawn.console.log(f"[yellow]⚠️  Error parsing response body: {e}[/yellow]")

                    # 응답 저장
                    if self.args.output:
                        self._save_response_content(content)

                    return True

            except urllib.error.HTTPError as e:
                status_color = "red" if e.code >= 400 else "yellow"
                pawn.console.log(f"[{status_color}]HTTP 오류: {e.code} {e.reason}[/{status_color}]")
                return e.code < 500  # 4xx는 성공으로 간주 (클라이언트 오류)

        except urllib.error.URLError as e:
            self.log_error(f"URL 오류: {e.reason}")
            return False
        except socket.timeout:
            self.log_error("HTTP 요청 타임아웃")
            return False
        except Exception as e:
            self.log_error(f"HTTP 검사 중 오류 발생: {e}")
            return False



    def format_ms(self, seconds):
        """초를 밀리초로 변환하여 포맷팅"""
        if seconds == 0:
            return "0.0ms"
        return f"{seconds * 1000:.1f}ms"
    
    def _save_response_content(self, content):
        """응답 내용을 파일로 저장"""
        try:
            # 출력 디렉토리 생성
            output_path = self.args.output
            if os.path.dirname(output_path):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # 파일 저장
            try:
                with open(output_path, 'wb') as f:
                    f.write(content)

                # 성공 메시지를 패널로 표시
                success_panel = Panel(
                    f"Response saved to: {output_path}",
                    title="[green]✅ File Saved[/green]",
                    border_style="green",
                    padding=(1, 1)
                )
                pawn.console.print(success_panel)

            except Exception as e:
                error_panel = Panel(
                    f"Error: {str(e)}",
                    title="[red]❌ Save Failed[/red]",
                    border_style="red",
                    padding=(1, 1)
                )
                pawn.console.print(error_panel)
        except Exception as e:
            self.log_error(f"파일 저장 중 오류 발생: {e}")


def main():
    """메인 함수"""
    # 명령어 전처리
    cli = InspectCLI()

    # sys.argv 전처리
    if len(sys.argv) > 1:
        processed_argv = cli.preprocess_command(sys.argv[1:])
        sys.argv = [sys.argv[0]] + processed_argv

    return cli.main()


if __name__ == '__main__':
    sys.exit(main())
