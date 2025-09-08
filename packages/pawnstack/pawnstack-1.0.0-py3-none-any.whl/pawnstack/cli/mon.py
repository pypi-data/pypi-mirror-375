"""
Mon CLI - 통합 모니터링 도구

시스템 리소스, SSH 로그, 블록체인 wallet 모니터링을 통합한 도구
레거시 pawnlib mon.py 기능과 새로운 시스템 모니터링 기능을 모두 포함
"""

import asyncio
import json
import time
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from argparse import ArgumentParser
from pathlib import Path

from pawnstack.cli.base import MonitoringBaseCLI, AsyncBaseCLI, register_cli_command
from pawnstack.config.global_config import pawn
from pawnstack.resource import system, network, disk

import psutil

# 모듈 메타데이터
__description__ = "통합 모니터링 도구 (시스템, SSH, Wallet)"
__epilog__ = """
사용 예제:
  
  시스템 모니터링:
    pawns mon system --cpu-threshold 80 --memory-threshold 90
    pawns mon system --interval 5 --duration 300
    
  SSH 로그 모니터링:
    pawns mon ssh -f /var/log/secure /var/log/auth.log
    pawns mon ssh --follow --alert-webhook https://hooks.slack.com/...
    
  Wallet 모니터링:
    pawns mon wallet --url https://api.icon.network --address-filter hx1234...
    pawns mon wallet --blockheight 1000000 --bps-interval 10
"""


def str2bool(v) -> bool:
    """문자열을 불린값으로 변환"""
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    if isinstance(v, str):
        return v.lower() in ("yes", "true", "t", "1")
    return bool(v)


class SSHLogPathResolver:
    """SSH 로그 파일 경로 자동 탐지"""
    
    COMMON_LOG_PATHS = [
        "/var/log/auth.log",      # Debian/Ubuntu
        "/var/log/secure",         # CentOS/RHEL/Fedora
        "/var/log/syslog",        # General syslog
        "/var/log/messages",      # General messages
        "/var/log/sshd.log",      # OpenSSH
        "/var/log/system.log",    # macOS
    ]
    
    def get_path(self) -> str:
        """시스템에 맞는 SSH 로그 파일 경로 반환"""
        for path in self.COMMON_LOG_PATHS:
            if Path(path).exists():
                return path
        
        # macOS의 경우
        if os.name == 'posix' and Path('/private/var/log/system.log').exists():
            return '/private/var/log/system.log'
        
        # 기본값
        return "/var/log/auth.log"
    
    def get_available_paths(self) -> List[str]:
        """존재하는 모든 SSH 로그 파일 경로 반환"""
        available = []
        for path in self.COMMON_LOG_PATHS:
            if Path(path).exists():
                available.append(path)
        return available


class MonCLI(AsyncBaseCLI):
    """통합 모니터링 CLI"""
    
    def __init__(self, args=None):
        super().__init__(args)
        self.monitoring_data = []
        self.alert_history = []
        self.last_alert_time = {}
        self.ssh_patterns = {}
        self.setup_ssh_patterns()
    
    def get_arguments(self, parser: ArgumentParser):
        """명령어 인수 정의"""
        # 서브커맨드 생성 - 기본값은 system
        subparsers = parser.add_subparsers(
            dest='subcommand',
            help='모니터링 종류 (기본값: system)',
            required=False
        )
        
        # System 모니터링
        system_parser = subparsers.add_parser(
            'system',
            help='시스템 리소스 모니터링 (CPU, 메모리, 디스크, 네트워크)'
        )
        self._add_system_arguments(system_parser)
        
        # SSH 로그 모니터링
        ssh_parser = subparsers.add_parser(
            'ssh',
            help='SSH 로그 파일 모니터링 및 보안 이벤트 감지'
        )
        self._add_ssh_arguments(ssh_parser)
        
        # Wallet 모니터링
        wallet_parser = subparsers.add_parser(
            'wallet',
            help='블록체인 wallet 및 트랜잭션 모니터링'
        )
        self._add_wallet_arguments(wallet_parser)
    
    def _add_system_arguments(self, parser: ArgumentParser):
        """시스템 모니터링 인수"""
        # 기본 모니터링 옵션
        parser.add_argument(
            '--interval',
            type=int,
            default=5,
            help='모니터링 간격 (초, default: 5)'
        )
        
        parser.add_argument(
            '--duration',
            type=int,
            help='모니터링 지속 시간 (초, default: 무제한)'
        )
        
        # 임계값 설정
        parser.add_argument(
            '--cpu-threshold',
            type=float,
            default=80.0,
            help='CPU 사용률 알림 임계값 (퍼센트, default: 80)'
        )
        
        parser.add_argument(
            '--memory-threshold',
            type=float,
            default=85.0,
            help='메모리 사용률 알림 임계값 (퍼센트, default: 85)'
        )
        
        parser.add_argument(
            '--disk-threshold',
            type=float,
            default=90.0,
            help='디스크 사용률 알림 임계값 (퍼센트, default: 90)'
        )
        
        parser.add_argument(
            '--network-threshold',
            type=float,
            default=1000.0,
            help='네트워크 사용량 알림 임계값 (MB/s, default: 1000)'
        )
        
        parser.add_argument(
            '--load-threshold',
            type=float,
            help='시스템 로드 평균 알림 임계값'
        )
        
        # 출력 옵션
        parser.add_argument(
            '--output-file',
            type=str,
            help='모니터링 데이터 출력 파일'
        )
        
        # 알림 옵션
        self._add_common_alert_arguments(parser)
    
    def _add_ssh_arguments(self, parser: ArgumentParser):
        """SSH 모니터링 인수"""
        parser.add_argument(
            '-f', '--file',
            metavar='ssh_log_file',
            help='모니터링할 SSH 로그 파일',
            nargs='+',
            default=[SSHLogPathResolver().get_path()]
        )
        
        parser.add_argument(
            '--follow',
            action='store_true',
            help='로그 파일 실시간 추적 (tail -f)'
        )
        
        parser.add_argument(
            '--patterns',
            nargs='+',
            help='감지할 패턴 (정규식)'
        )
        
        parser.add_argument(
            '--ignore-patterns',
            nargs='+',
            help='무시할 패턴 (정규식)'
        )
        
        parser.add_argument(
            '--alert-on-failure',
            action='store_true',
            help='로그인 실패 시 알림'
        )
        
        parser.add_argument(
            '--alert-on-success',
            action='store_true',
            help='로그인 성공 시 알림'
        )
        
        parser.add_argument(
            '--max-failures',
            type=int,
            default=5,
            help='알림 전 최대 실패 횟수 (default: 5)'
        )
        
        parser.add_argument(
            '--time-window',
            type=int,
            default=300,
            help='실패 횟수 계산 시간 창 (초, default: 300)'
        )
        
        # 알림 옵션
        self._add_common_alert_arguments(parser)
    
    def _add_wallet_arguments(self, parser: ArgumentParser):
        """Wallet 모니터링 인수"""
        parser.add_argument(
            '--url', '--endpoint-url',
            metavar="endpoint_url",
            dest='endpoint_url',
            help='블록체인 RPC 엔드포인트 URL',
            required=True
        )
        
        parser.add_argument(
            '--address-filter',
            help='모니터링할 주소 목록 (쉼표 구분)',
            type=lambda s: [addr.strip() for addr in s.split(',')],
            default=None
        )
        
        parser.add_argument(
            '--blockheight',
            type=int,
            default=None,
            help='시작 블록 높이 (default: 최신)'
        )
        
        parser.add_argument(
            '--ignore-data-types',
            help='무시할 데이터 타입 (쉼표 구분)',
            default='base'
        )
        
        parser.add_argument(
            '--check-tx-result',
            type=str2bool,
            help='트랜잭션 결과 확인 활성화',
            default=True
        )
        
        parser.add_argument(
            '--max-tx-attempts',
            type=int,
            help='최대 트랜잭션 시도 횟수',
            default=10
        )
        
        parser.add_argument(
            '--max-retries',
            type=int,
            default=10,
            help='WebSocket 연결 최대 재시도 횟수 (1-100)'
        )
        
        parser.add_argument(
            '--bps-interval', '-i',
            type=int,
            help='BPS/TPS 계산 간격 (초, 0=비활성화)',
            default=0
        )
        
        parser.add_argument(
            '--skip-until', '-su',
            type=int,
            help='이 블록 높이까지 스킵',
            default=0
        )
        
        parser.add_argument(
            '-n', '--network-name',
            type=str,
            help='네트워크 이름',
            default=""
        )
        
        # 알림 옵션
        self._add_common_alert_arguments(parser)
    
    def _add_common_alert_arguments(self, parser: ArgumentParser):
        """공통 알림 인수"""
        parser.add_argument(
            '--alert-webhook',
            type=str,
            help='알림 웹훅 URL (Slack, Discord 등)'
        )
        
        parser.add_argument(
            '--alert-email',
            type=str,
            help='알림 이메일 주소'
        )
        
        parser.add_argument(
            '--alert-cooldown',
            type=int,
            default=300,
            help='동일 알림 재전송 방지 시간 (초, default: 300)'
        )
        
        parser.add_argument(
            '--slack-webhook-url',
            help='Slack webhook URL',
            default=None
        )
        
        parser.add_argument(
            '--send-slack',
            type=str2bool,
            help='Slack 메시지 전송 활성화',
            default=True
        )
    
    async def run_async(self) -> int:
        """비동기 명령어 실행"""
        try:
            # 서브커맨드에 따라 분기 (기본값: system)
            subcommand = getattr(self.args, 'subcommand', None)
            
            if not subcommand:
                # 서브커맨드가 없으면 기본값으로 system 사용
                subcommand = 'system'
                self.log_info("📊 기본 모니터링 모드: system")
            
            self.log_info(f"🚀 {subcommand.upper()} 모니터링 시작")
            
            if subcommand == 'system':
                return await self.run_system_monitoring()
            elif subcommand == 'ssh':
                return await self.run_ssh_monitoring()
            elif subcommand == 'wallet':
                return await self.run_wallet_monitoring()
            else:
                self.log_error(f"알 수 없는 서브커맨드: {subcommand}")
                return 1
                
        except KeyboardInterrupt:
            self.log_info("⏹️  모니터링 중지됨")
            return 0
        except Exception as e:
            self.log_error(f"모니터링 오류: {e}")
            if pawn.get('PAWN_DEBUG'):
                pawn.console.print_exception(show_locals=True)
            return 1
    
    async def run_system_monitoring(self) -> int:
        """시스템 리소스 모니터링"""
        interval = getattr(self.args, 'interval', 5)
        duration = getattr(self.args, 'duration', None)
        start_time = time.time()
        
        try:
            while True:
                # 시스템 메트릭 수집
                metrics = await self.collect_system_metrics()
                
                # 메트릭 출력
                self.display_system_metrics(metrics)
                
                # 임계값 체크 및 알림
                await self.check_system_thresholds(metrics)
                
                # 데이터 저장
                if hasattr(self.args, 'output_file') and self.args.output_file:
                    await self.save_metrics(metrics)
                
                # 종료 조건 체크
                if duration and (time.time() - start_time) >= duration:
                    self.log_info("⏱️  모니터링 시간 종료")
                    break
                
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            pass
        
        return 0
    
    async def run_ssh_monitoring(self) -> int:
        """SSH 로그 모니터링"""
        log_files = getattr(self.args, 'file', [SSHLogPathResolver().get_path()])
        follow = getattr(self.args, 'follow', False)
        
        self.log_info(f"📁 모니터링 로그 파일: {', '.join(log_files)}")
        
        # 실패 시도 추적
        self.failure_attempts = {}
        
        try:
            if follow:
                # 실시간 로그 추적
                await self.follow_ssh_logs(log_files)
            else:
                # 기존 로그 분석
                await self.analyze_ssh_logs(log_files)
                
        except KeyboardInterrupt:
            pass
        
        return 0
    
    async def run_wallet_monitoring(self) -> int:
        """Wallet 모니터링"""
        endpoint_url = getattr(self.args, 'endpoint_url', None)
        
        if not endpoint_url:
            self.log_error("엔드포인트 URL이 필요합니다")
            return 1
        
        self.log_info(f"🔗 엔드포인트: {endpoint_url}")
        
        # 주소 필터
        address_filter = getattr(self.args, 'address_filter', None)
        if address_filter:
            self.log_info(f"📍 모니터링 주소: {', '.join(address_filter)}")
        
        try:
            # WebSocket 연결 및 모니터링
            await self.monitor_blockchain_wallet(endpoint_url)
            
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.log_error(f"Wallet 모니터링 오류: {e}")
            return 1
        
        return 0
    
    # ===== 시스템 모니터링 메서드 =====
    
    async def collect_system_metrics(self) -> Dict[str, Any]:
        """시스템 메트릭 수집"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count(),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            'memory': {
                'percent': psutil.virtual_memory().percent,
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'used': psutil.virtual_memory().used
            },
            'disk': {},
            'network': {},
            'load': os.getloadavg() if hasattr(os, 'getloadavg') else None
        }
        
        # 디스크 사용량
        for partition in psutil.disk_partitions():
            if partition.mountpoint:
                usage = psutil.disk_usage(partition.mountpoint)
                metrics['disk'][partition.mountpoint] = {
                    'percent': usage.percent,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free
                }
        
        # 네트워크 통계
        net_io = psutil.net_io_counters()
        metrics['network'] = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }
        
        return metrics
    
    def display_system_metrics(self, metrics: Dict[str, Any]):
        """시스템 메트릭 출력"""
        pawn.console.log(f"[bold cyan]===== System Metrics @ {metrics['timestamp']} =====[/bold cyan]")
        pawn.console.log(f"📊 CPU: {metrics['cpu']['percent']}% ({metrics['cpu']['count']} cores)")
        pawn.console.log(f"💾 Memory: {metrics['memory']['percent']}% "
                        f"({metrics['memory']['used'] / (1024**3):.1f}GB / "
                        f"{metrics['memory']['total'] / (1024**3):.1f}GB)")
        
        for mount, disk in metrics['disk'].items():
            pawn.console.log(f"💿 Disk {mount}: {disk['percent']}% "
                            f"({disk['used'] / (1024**3):.1f}GB / "
                            f"{disk['total'] / (1024**3):.1f}GB)")
        
        if metrics['load']:
            pawn.console.log(f"⚡ Load Average: {metrics['load']}")
    
    async def check_system_thresholds(self, metrics: Dict[str, Any]):
        """시스템 임계값 체크"""
        alerts = []
        
        # CPU 임계값
        cpu_threshold = getattr(self.args, 'cpu_threshold', 80.0)
        if metrics['cpu']['percent'] > cpu_threshold:
            alerts.append(f"⚠️ CPU 사용률이 {cpu_threshold}%를 초과했습니다: {metrics['cpu']['percent']}%")
        
        # 메모리 임계값
        memory_threshold = getattr(self.args, 'memory_threshold', 85.0)
        if metrics['memory']['percent'] > memory_threshold:
            alerts.append(f"⚠️ 메모리 사용률이 {memory_threshold}%를 초과했습니다: {metrics['memory']['percent']}%")
        
        # 디스크 임계값
        disk_threshold = getattr(self.args, 'disk_threshold', 90.0)
        for mount, disk in metrics['disk'].items():
            if disk['percent'] > disk_threshold:
                alerts.append(f"⚠️ 디스크 {mount} 사용률이 {disk_threshold}%를 초과했습니다: {disk['percent']}%")
        
        # 알림 전송
        if alerts:
            await self.send_alerts(alerts)
    
    # ===== SSH 모니터링 메서드 =====
    
    def setup_ssh_patterns(self):
        """SSH 로그 패턴 설정"""
        self.ssh_patterns = {
            'auth_success': re.compile(r'Accepted \w+ for (\w+) from ([\d.]+)'),
            'auth_failure': re.compile(r'Failed password for (?:invalid user )?(\w+) from ([\d.]+)'),
            'connection_closed': re.compile(r'Connection closed by ([\d.]+)'),
            'invalid_user': re.compile(r'Invalid user (\w+) from ([\d.]+)'),
            'break_in_attempt': re.compile(r'POSSIBLE BREAK-IN ATTEMPT'),
            'too_many_auth': re.compile(r'Too many authentication failures'),
        }
    
    async def follow_ssh_logs(self, log_files: List[str]):
        """SSH 로그 실시간 추적"""
        import aiofiles
        import asyncio
        
        async def tail_file(filepath):
            """파일 tail -f 구현"""
            async with aiofiles.open(filepath, 'r') as f:
                # 파일 끝으로 이동
                await f.seek(0, 2)
                
                while True:
                    line = await f.readline()
                    if line:
                        await self.process_ssh_log_line(line, filepath)
                    else:
                        await asyncio.sleep(0.1)
        
        # 모든 로그 파일을 동시에 추적
        tasks = [tail_file(log_file) for log_file in log_files]
        await asyncio.gather(*tasks)
    
    async def analyze_ssh_logs(self, log_files: List[str]):
        """SSH 로그 분석"""
        for log_file in log_files:
            if not Path(log_file).exists():
                self.log_warning(f"로그 파일이 존재하지 않습니다: {log_file}")
                continue
            
            self.log_info(f"📖 분석 중: {log_file}")
            
            with open(log_file, 'r') as f:
                for line in f:
                    await self.process_ssh_log_line(line, log_file)
    
    async def process_ssh_log_line(self, line: str, source_file: str):
        """SSH 로그 라인 처리"""
        line = line.strip()
        if not line:
            return
        
        # 패턴 매칭
        for pattern_name, pattern in self.ssh_patterns.items():
            match = pattern.search(line)
            if match:
                await self.handle_ssh_event(pattern_name, match, line, source_file)
    
    async def handle_ssh_event(self, event_type: str, match, line: str, source_file: str):
        """SSH 이벤트 처리"""
        timestamp = datetime.now()
        
        if event_type == 'auth_failure':
            user = match.group(1)
            ip = match.group(2)
            
            # 실패 횟수 추적
            key = f"{user}@{ip}"
            if key not in self.failure_attempts:
                self.failure_attempts[key] = []
            
            self.failure_attempts[key].append(timestamp)
            
            # 시간 창 내의 실패 횟수 계산
            time_window = getattr(self.args, 'time_window', 300)
            recent_failures = [
                t for t in self.failure_attempts[key]
                if (timestamp - t).seconds <= time_window
            ]
            self.failure_attempts[key] = recent_failures
            
            # 임계값 체크
            max_failures = getattr(self.args, 'max_failures', 5)
            if len(recent_failures) >= max_failures:
                alert = f"🚨 SSH 로그인 실패 임계값 초과: {user}@{ip} ({len(recent_failures)}회/{time_window}초)"
                await self.send_alerts([alert])
                self.failure_attempts[key] = []  # 리셋
            
            if getattr(self.args, 'alert_on_failure', False):
                self.log_warning(f"❌ 로그인 실패: {user}@{ip}")
        
        elif event_type == 'auth_success':
            user = match.group(1)
            ip = match.group(2)
            
            if getattr(self.args, 'alert_on_success', False):
                self.log_success(f"✅ 로그인 성공: {user}@{ip}")
                alert = f"SSH 로그인 성공: {user}@{ip}"
                await self.send_alerts([alert])
        
        elif event_type in ['break_in_attempt', 'too_many_auth']:
            self.log_error(f"🚨 보안 경고: {event_type}")
            await self.send_alerts([f"보안 경고: {line}"])
    
    # ===== Wallet 모니터링 메서드 =====
    
    async def monitor_blockchain_wallet(self, endpoint_url: str):
        """블록체인 wallet 모니터링"""
        self.log_info("🔗 블록체인 WebSocket 연결 시작...")
        
        # WebSocket 연결 설정
        max_retries = getattr(self.args, 'max_retries', 10)
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # WebSocket 연결 및 모니터링 로직
                # 실제 구현은 블록체인 네트워크에 따라 달라짐
                await self.connect_and_monitor_websocket(endpoint_url)
                
            except Exception as e:
                retry_count += 1
                self.log_warning(f"연결 실패 ({retry_count}/{max_retries}): {e}")
                if retry_count < max_retries:
                    await asyncio.sleep(5)  # 재시도 전 대기
                else:
                    self.log_error("최대 재시도 횟수 초과")
                    raise
    
    async def connect_and_monitor_websocket(self, endpoint_url: str):
        """WebSocket 연결 및 모니터링"""
        # 이것은 예시 구현입니다. 실제 구현은 pawnstack의 blockchain 모듈을 사용해야 합니다.
        import aiohttp
        
        blockheight = getattr(self.args, 'blockheight', None)
        skip_until = getattr(self.args, 'skip_until', 0)
        address_filter = getattr(self.args, 'address_filter', None)
        
        self.log_info(f"📦 시작 블록: {blockheight or '최신'}")
        
        # 간단한 HTTP polling 예시 (실제로는 WebSocket 사용)
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    # 블록체인 상태 체크
                    async with session.get(f"{endpoint_url}/api/v3/block/last") as response:
                        if response.status == 200:
                            data = await response.json()
                            current_height = data.get('height', 0)
                            
                            if skip_until and current_height <= skip_until:
                                self.log_debug(f"블록 {current_height} 스킵")
                                continue
                            
                            # BPS 계산
                            bps_interval = getattr(self.args, 'bps_interval', 0)
                            if bps_interval > 0:
                                await self.calculate_bps_tps(current_height)
                            
                            # 주소 필터링된 트랜잭션 체크
                            if address_filter:
                                await self.check_address_transactions(
                                    session, endpoint_url, current_height, address_filter
                                )
                            
                            self.log_info(f"📦 현재 블록: {current_height}")
                    
                    await asyncio.sleep(2)  # Polling interval
                    
                except Exception as e:
                    self.log_error(f"모니터링 오류: {e}")
                    await asyncio.sleep(5)
    
    async def calculate_bps_tps(self, current_height: int):
        """BPS/TPS 계산"""
        # 구현 필요
        pass
    
    async def check_address_transactions(self, session, endpoint_url: str, 
                                        height: int, addresses: List[str]):
        """주소별 트랜잭션 체크"""
        # 구현 필요
        pass
    
    # ===== 공통 메서드 =====
    
    async def send_alerts(self, alerts: List[str]):
        """알림 전송"""
        if not alerts:
            return
        
        # 콘솔 출력
        for alert in alerts:
            self.log_warning(alert)
        
        # Webhook 알림
        webhook_url = getattr(self.args, 'alert_webhook', None) or \
                     getattr(self.args, 'slack_webhook_url', None)
        
        if webhook_url and getattr(self.args, 'send_slack', True):
            await self.send_webhook_alert(webhook_url, alerts)
        
        # 이메일 알림
        email = getattr(self.args, 'alert_email', None)
        if email:
            await self.send_email_alert(email, alerts)
    
    async def send_webhook_alert(self, webhook_url: str, alerts: List[str]):
        """Webhook 알림 전송"""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    'text': '🚨 PawnStack Monitor Alert',
                    'attachments': [
                        {
                            'color': 'warning',
                            'fields': [
                                {
                                    'title': '알림',
                                    'value': '\n'.join(alerts),
                                    'short': False
                                }
                            ],
                            'footer': 'PawnStack Monitor',
                            'ts': int(time.time())
                        }
                    ]
                }
                
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        self.log_debug("Webhook 알림 전송 성공")
                    else:
                        self.log_warning(f"Webhook 알림 전송 실패: HTTP {response.status}")
        
        except Exception as e:
            self.log_error(f"Webhook 알림 전송 오류: {e}")
    
    async def send_email_alert(self, email: str, alerts: List[str]):
        """이메일 알림 전송"""
        # 이메일 전송 로직 구현 필요
        self.log_info(f"📧 이메일 알림 전송: {email}")
        pass
    
    async def save_metrics(self, metrics: Dict[str, Any]):
        """메트릭 저장"""
        output_file = getattr(self.args, 'output_file', None)
        if not output_file:
            return
        
        try:
            self.monitoring_data.append(metrics)
            
            with open(output_file, 'w') as f:
                json.dump(self.monitoring_data, f, indent=2, ensure_ascii=False)
            
            self.log_debug(f"메트릭 저장: {output_file}")
        
        except Exception as e:
            self.log_error(f"메트릭 저장 오류: {e}")


def main():
    """CLI 진입점"""
    cli = MonCLI()
    return cli.main()


if __name__ == "__main__":
    exit(main())