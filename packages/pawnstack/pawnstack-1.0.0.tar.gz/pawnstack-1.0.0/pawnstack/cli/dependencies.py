"""
PawnStack CLI 의존성 관리 시스템

선택적 의존성 검사, 안내 메시지, 자동 설치 제안 기능
"""

import asyncio
import importlib
import subprocess
import sys
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass

from pawnstack.config.global_config import pawn


@dataclass
class DependencyInfo:
    """의존성 정보 클래스"""
    module_name: str
    package_name: str
    version_check: Optional[str] = None
    import_error_hint: Optional[str] = None


class DependencyChecker:
    """선택적 의존성 검사 및 안내 시스템"""

    # extras별 의존성 정의
    EXTRAS_DEPENDENCIES: Dict[str, List[DependencyInfo]] = {
        'blockchain': [
            DependencyInfo(
                module_name='eth_keyfile',
                package_name='eth-keyfile',
                version_check='__version__',
                import_error_hint='ICON 지갑 관리 및 키스토어 처리에 필요합니다'
            ),
            DependencyInfo(
                module_name='coincurve',
                package_name='coincurve',
                version_check='__version__',
                import_error_hint='타원곡선 암호화 및 서명 기능에 필요합니다'
            ),
        ],
        'aws': [
            DependencyInfo(
                module_name='boto3',
                package_name='boto3',
                version_check='__version__',
                import_error_hint='AWS 서비스 연동에 필요합니다'
            ),
            DependencyInfo(
                module_name='aioboto3',
                package_name='aioboto3',
                version_check='__version__',
                import_error_hint='비동기 AWS 작업에 필요합니다'
            ),
            DependencyInfo(
                module_name='botocore',
                package_name='botocore',
                version_check='__version__',
                import_error_hint='AWS 핵심 기능에 필요합니다'
            ),
        ],
        'cloud': [
            # cloud는 aws를 포함하므로 aws 의존성을 상속
            DependencyInfo(
                module_name='boto3',
                package_name='boto3',
                version_check='__version__',
                import_error_hint='클라우드 서비스 (AWS) 연동에 필요합니다'
            ),
            DependencyInfo(
                module_name='aioboto3',
                package_name='aioboto3',
                version_check='__version__',
                import_error_hint='비동기 클라우드 작업에 필요합니다'
            ),
        ],
        'docker': [
            DependencyInfo(
                module_name='aiodocker',
                package_name='aiodocker',
                version_check='__version__',
                import_error_hint='비동기 Docker 작업에 필요합니다'
            ),
            DependencyInfo(
                module_name='docker',
                package_name='docker',
                version_check='__version__',
                import_error_hint='Docker 컨테이너 관리에 필요합니다'
            ),
        ],
        'redis': [
            DependencyInfo(
                module_name='redis',
                package_name='redis',
                version_check='__version__',
                import_error_hint='Redis 캐시 및 메시징에 필요합니다'
            ),
            DependencyInfo(
                module_name='aioredis',
                package_name='aioredis',
                version_check='__version__',
                import_error_hint='비동기 Redis 작업에 필요합니다'
            ),
        ],
        'database': [
            DependencyInfo(
                module_name='sqlalchemy',
                package_name='sqlalchemy',
                version_check='__version__',
                import_error_hint='데이터베이스 ORM 기능에 필요합니다'
            ),
            DependencyInfo(
                module_name='asyncpg',
                package_name='asyncpg',
                version_check='__version__',
                import_error_hint='PostgreSQL 비동기 연결에 필요합니다'
            ),
        ],
        'messaging': [
            DependencyInfo(
                module_name='slack_sdk',
                package_name='slack-sdk',
                version_check='__version__',
                import_error_hint='Slack 알림 기능에 필요합니다'
            ),
            DependencyInfo(
                module_name='discord',
                package_name='discord.py',
                version_check='__version__',
                import_error_hint='Discord 알림 기능에 필요합니다'
            ),
        ],
        'monitoring': [
            DependencyInfo(
                module_name='prometheus_client',
                package_name='prometheus-client',
                version_check='__version__',
                import_error_hint='Prometheus 메트릭 수집에 필요합니다'
            ),
        ],
        'performance': [
            DependencyInfo(
                module_name='uvloop',
                package_name='uvloop',
                version_check='__version__',
                import_error_hint='고성능 비동기 이벤트 루프에 필요합니다'
            ),
            DependencyInfo(
                module_name='orjson',
                package_name='orjson',
                version_check='__version__',
                import_error_hint='고속 JSON 처리에 필요합니다'
            ),
        ]
    }

    # CLI 명령어별 필요 extras 매핑
    COMMAND_DEPENDENCIES: Dict[str, List[str]] = {
        # 블록체인 관련 명령어
        'wallet': ['blockchain'],
        'icon': ['blockchain'],
        'rpc': ['blockchain'],
        'goloop': ['blockchain'],

        # 클라우드 관련 명령어
        'aws': ['aws'],
        's3': ['aws'],

        # 컨테이너 관련 명령어
        'docker': ['docker'],
        'compose': ['docker'],

        # 모니터링 관련 명령어
        'mon': ['monitoring'],  # Prometheus 메트릭 지원
        'noti': ['messaging'],  # Slack, Discord 알림

        # 개발 도구
        'init': [],  # 기본 기능만 사용
        'inspect': [],  # 기본 기능만 사용
        'metadata': [],  # 기본 기능만 사용

        # 인프라 도구
        'snap': [],  # 기본 기능만 사용
        'tf': [],  # Terraform CLI 래퍼
        'gs': ['blockchain'],  # Genesis 파일은 블록체인 관련

        # 보안 도구
        'scan_key': [],  # 기본 기능만 사용

        # 시스템 도구 (기본 기능)
        'info': [],
        'banner': [],
        'server': [],
        'top': [],
        'net': [],
        'http': [],
        'proxy': [],
        'websocket': [],

        # 의존성 관리
        'deps': [],  # 기본 기능만 사용
    }

    @classmethod
    def get_command_dependencies(cls, command_name: str) -> List[str]:
        """명령어에 필요한 extras 반환"""
        return cls.COMMAND_DEPENDENCIES.get(command_name, [])

    @classmethod
    def check_dependencies(cls, extras: List[str], command_name: Optional[str] = None) -> bool:
        """선택적 의존성 검사"""
        missing_dependencies = []

        for extra in extras:
            if extra not in cls.EXTRAS_DEPENDENCIES:
                pawn.console.log(f"[yellow]⚠️  알 수 없는 extras: {extra}[/yellow]")
                continue

            for dep_info in cls.EXTRAS_DEPENDENCIES[extra]:
                if not cls._check_single_dependency(dep_info):
                    missing_dependencies.append((extra, dep_info))

        if missing_dependencies:
            cls._suggest_installation(missing_dependencies, command_name)
            return False

        return True

    @classmethod
    def _check_single_dependency(cls, dep_info: DependencyInfo) -> bool:
        """단일 의존성 검사"""
        try:
            module = importlib.import_module(dep_info.module_name)

            # 버전 정보 확인 및 로깅
            if dep_info.version_check:
                try:
                    version = getattr(module, dep_info.version_check, 'unknown')

                    # 디버그 모드에서 버전 정보 출력
                    if pawn.get('PAWN_DEBUG'):
                        pawn.console.log(f"[dim]✓ {dep_info.package_name} v{version} 로드됨[/dim]")

                    # 버전 호환성 검사 (향후 확장 가능)
                    if not cls._check_version_compatibility(dep_info.package_name, version):
                        pawn.console.log(f"[yellow]⚠️  {dep_info.package_name} v{version}은 호환성 경고가 있습니다[/yellow]")

                except AttributeError:
                    if pawn.get('PAWN_DEBUG'):
                        pawn.console.log(f"[dim]✓ {dep_info.package_name} 로드됨 (버전 정보 없음)[/dim]")

            return True

        except ImportError:
            return False

    @classmethod
    def _check_version_compatibility(cls, package_name: str, version: str) -> bool:
        """버전 호환성 검사"""
        # 알려진 호환성 문제가 있는 버전들
        incompatible_versions = {
            'boto3': ['1.26.0', '1.26.1'],  # 알려진 버그가 있는 버전
            'aioboto3': ['11.0.0'],         # 호환성 문제가 있는 버전
            'docker': ['6.0.0', '6.0.1'],  # API 변경으로 인한 문제
        }

        if package_name in incompatible_versions:
            if version in incompatible_versions[package_name]:
                return False

        return True

    @classmethod
    def _suggest_installation(cls, missing_dependencies: List[Tuple[str, DependencyInfo]], command_name: Optional[str] = None):
        """설치 안내 메시지"""
        extras_needed = list(set(extra for extra, _ in missing_dependencies))
        extras_str = ','.join(extras_needed)

        pawn.console.log("")
        pawn.console.log(f"[red]❌ 필수 의존성이 누락되었습니다[/red]")

        if command_name:
            pawn.console.log(f"[yellow]'{command_name}' 명령어를 사용하려면 추가 패키지가 필요합니다.[/yellow]")

        pawn.console.log("")
        pawn.console.log(f"[blue]💡 다음 명령어로 설치하세요:[/blue]")
        pawn.console.log(f"[cyan]   pip install pawnstack[{extras_str}][/cyan]")
        pawn.console.log("")
        pawn.console.log(f"[blue]또는 모든 기능을 포함하여 설치:[/blue]")
        pawn.console.log(f"[cyan]   pip install pawnstack[full][/cyan]")
        pawn.console.log("")

        pawn.console.log("[yellow]누락된 패키지 상세 정보:[/yellow]")
        for extra, dep_info in missing_dependencies:
            hint = dep_info.import_error_hint or "추가 기능에 필요합니다"
            pawn.console.log(f"  • [bold]{dep_info.package_name}[/bold] ({extra}) - {hint}")

        pawn.console.log("")

    @classmethod
    def check_command_dependencies(cls, command_name: str) -> bool:
        """명령어별 의존성 검사"""
        required_extras = cls.get_command_dependencies(command_name)

        if not required_extras:
            return True  # 추가 의존성이 필요하지 않음

        return cls.check_dependencies(required_extras, command_name)

    @classmethod
    def get_available_extras(cls) -> List[str]:
        """사용 가능한 extras 목록 반환"""
        return list(cls.EXTRAS_DEPENDENCIES.keys())

    @classmethod
    def get_installed_extras(cls) -> List[str]:
        """설치된 extras 목록 반환"""
        installed = []

        for extra in cls.EXTRAS_DEPENDENCIES:
            all_deps_available = True
            for dep_info in cls.EXTRAS_DEPENDENCIES[extra]:
                if not cls._check_single_dependency(dep_info):
                    all_deps_available = False
                    break

            if all_deps_available:
                installed.append(extra)

        return installed

    @classmethod
    def get_missing_extras(cls) -> List[str]:
        """누락된 extras 목록 반환"""
        available = set(cls.get_available_extras())
        installed = set(cls.get_installed_extras())
        return list(available - installed)

    @classmethod
    def print_dependency_status(cls):
        """의존성 상태 출력"""
        from rich.table import Table

        table = Table(title="PawnStack 의존성 상태", show_header=True, header_style="bold magenta")
        table.add_column("Extra", style="dim", width=12)
        table.add_column("상태", width=8)
        table.add_column("패키지", style="cyan")
        table.add_column("설명", style="dim")

        for extra in cls.EXTRAS_DEPENDENCIES:
            deps = cls.EXTRAS_DEPENDENCIES[extra]

            # 첫 번째 의존성으로 상태 확인
            first_dep = deps[0]
            is_available = cls._check_single_dependency(first_dep)
            status = "[green]✓ 설치됨[/green]" if is_available else "[red]✗ 누락[/red]"

            # 패키지 목록
            packages = ", ".join([dep.package_name for dep in deps])

            # 설명
            description = cls._get_extra_description(extra)

            table.add_row(extra, status, packages, description)

        pawn.console.print(table)

    @classmethod
    def _get_extra_description(cls, extra: str) -> str:
        """extras 설명 반환"""
        descriptions = {
            'blockchain': '블록체인 지갑 및 RPC 기능',
            'aws': 'AWS 클라우드 서비스 연동',
            'cloud': '클라우드 서비스 통합 (AWS 포함)',
            'docker': 'Docker 컨테이너 관리',
            'redis': 'Redis 캐시 및 메시징',
            'database': '데이터베이스 ORM 및 연결',
            'messaging': 'Slack, Discord 등 알림 서비스',
            'monitoring': 'Prometheus 메트릭 및 모니터링',
            'performance': '고성능 비동기 처리 및 JSON'
        }
        return descriptions.get(extra, '추가 기능')

    @classmethod
    def auto_install_suggestion(cls, extras: List[str], auto_confirm: bool = False) -> bool:
        """자동 설치 제안"""
        if not extras:
            return True

        extras_str = ','.join(extras)

        pawn.console.log(f"[yellow]다음 extras가 필요합니다: {extras_str}[/yellow]")

        if auto_confirm:
            response = 'y'
        else:
            try:
                response = input(f"지금 설치하시겠습니까? (y/N): ").lower().strip()
            except (EOFError, KeyboardInterrupt):
                pawn.console.log("[yellow]설치가 취소되었습니다.[/yellow]")
                return False

        if response in ['y', 'yes']:
            return cls._perform_installation(extras_str)
        else:
            pawn.console.log("[yellow]설치가 취소되었습니다.[/yellow]")
            pawn.console.log(f"[blue]수동 설치: pip install pawnstack[{extras_str}][/blue]")
            return False

    @classmethod
    def _perform_installation(cls, extras_str: str) -> bool:
        """실제 설치 수행"""
        try:
            pawn.console.log(f"[blue]설치 중: pawnstack[{extras_str}][/blue]")

            # pip 업그레이드 명령어 구성
            cmd = [
                sys.executable, '-m', 'pip', 'install', '--upgrade',
                f'pawnstack[{extras_str}]'
            ]

            # 설치 실행
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5분 타임아웃
            )

            if result.returncode == 0:
                pawn.console.log("[green]✅ 설치가 완료되었습니다![/green]")
                pawn.console.log("[yellow]변경사항을 적용하려면 애플리케이션을 다시 시작하세요.[/yellow]")
                return True
            else:
                pawn.console.log(f"[red]❌ 설치 실패:[/red]")
                pawn.console.log(f"[red]{result.stderr}[/red]")
                return False

        except subprocess.TimeoutExpired:
            pawn.console.log("[red]❌ 설치 시간이 초과되었습니다.[/red]")
            return False
        except Exception as e:
            pawn.console.log(f"[red]❌ 설치 중 오류 발생: {e}[/red]")
            return False


def require_dependencies(extras: List[str]):
    """의존성 검사 데코레이터"""
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if not DependencyChecker.check_dependencies(extras):
                return 1  # 오류 코드 반환
            return method(self, *args, **kwargs)

        # 비동기 함수 지원
        if asyncio.iscoroutinefunction(method):
            async def async_wrapper(self, *args, **kwargs):
                if not DependencyChecker.check_dependencies(extras):
                    return 1
                return await method(self, *args, **kwargs)
            return async_wrapper

        return wrapper
    return decorator


def require_command_dependencies(command_name: str):
    """명령어별 의존성 검사 데코레이터"""
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if not DependencyChecker.check_command_dependencies(command_name):
                return 1
            return method(self, *args, **kwargs)

        # 비동기 함수 지원
        if asyncio.iscoroutinefunction(method):
            async def async_wrapper(self, *args, **kwargs):
                if not DependencyChecker.check_command_dependencies(command_name):
                    return 1
                return await method(self, *args, **kwargs)
            return async_wrapper

        return wrapper
    return decorator


# 편의 함수들
def check_blockchain_dependencies() -> bool:
    """블록체인 의존성 검사"""
    return DependencyChecker.check_dependencies(['blockchain'])


def check_aws_dependencies() -> bool:
    """AWS 의존성 검사"""
    return DependencyChecker.check_dependencies(['aws'])


def check_docker_dependencies() -> bool:
    """Docker 의존성 검사"""
    return DependencyChecker.check_dependencies(['docker'])


def check_redis_dependencies() -> bool:
    """Redis 의존성 검사"""
    return DependencyChecker.check_dependencies(['redis'])


def print_installation_guide():
    """설치 가이드 출력"""
    pawn.console.log("")
    pawn.console.log("[bold blue]PawnStack 선택적 의존성 설치 가이드[/bold blue]")
    pawn.console.log("")

    pawn.console.log("[yellow]기본 설치 (핵심 기능만):[/yellow]")
    pawn.console.log("  pip install pawnstack")
    pawn.console.log("")

    pawn.console.log("[yellow]기능별 설치:[/yellow]")
    pawn.console.log("  pip install pawnstack[blockchain]  # 블록체인 기능")
    pawn.console.log("  pip install pawnstack[aws]         # AWS 클라우드 기능")
    pawn.console.log("  pip install pawnstack[docker]      # Docker 컨테이너 기능")
    pawn.console.log("  pip install pawnstack[redis]       # Redis 캐시 기능")
    pawn.console.log("")

    pawn.console.log("[yellow]조합 설치:[/yellow]")
    pawn.console.log("  pip install pawnstack[blockchain,aws]     # 블록체인 + AWS")
    pawn.console.log("  pip install pawnstack[docker,redis]       # Docker + Redis")
    pawn.console.log("")

    pawn.console.log("[yellow]전체 설치 (모든 기능):[/yellow]")
    pawn.console.log("  pip install pawnstack[full]")
    pawn.console.log("")

    pawn.console.log("[yellow]개발자 도구 포함:[/yellow]")
    pawn.console.log("  pip install pawnstack[full,dev]")
    pawn.console.log("")
