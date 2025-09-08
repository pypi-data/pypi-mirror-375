"""
PawnStack CLI 기본 클래스

모든 CLI 명령어의 기본 클래스 및 공통 기능
"""

import time
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from argparse import ArgumentParser, Namespace

from pawnstack.config.global_config import pawn
from pawnstack.cli.banner import print_completion_banner, print_error_banner
from pawnstack.cli.dependencies import DependencyChecker


class BaseCLI(ABC):
    """CLI 명령어 기본 클래스"""

    def __init__(self, args: Optional[Namespace] = None):
        self.args = args or Namespace()
        self.start_time = time.time()
        self.command_name = self.__class__.__name__.lower().replace('cli', '')

    @abstractmethod
    def get_arguments(self, parser: ArgumentParser):
        """명령어별 인수 정의"""
        pass

    @abstractmethod
    def run(self) -> int:
        """명령어 실행 (동기)"""
        pass

    async def run_async(self) -> int:
        """명령어 실행 (비동기) - 필요시 오버라이드"""
        return self.run()

    def main(self) -> int:
        """메인 실행 함수"""
        try:
            pawn.console.log(f"🚀 Starting {self.command_name} command")

            # 비동기 함수인지 확인
            if asyncio.iscoroutinefunction(self.run_async) and self.run_async != BaseCLI.run_async:
                # 커스텀 비동기 구현이 있는 경우
                result = asyncio.run(self.run_async())
            else:
                # 동기 실행
                result = self.run()

            duration = time.time() - self.start_time

            if result == 0:
                print_completion_banner(self.command_name, duration)
            else:
                print_error_banner(self.command_name, f"Command returned exit code {result}")

            return result

        except KeyboardInterrupt:
            pawn.console.log(f"[yellow]⚠️  {self.command_name} command interrupted by user")
            return 130
        except Exception as e:
            duration = time.time() - self.start_time
            print_error_banner(self.command_name, str(e))

            if pawn.get('PAWN_DEBUG'):
                pawn.console.print_exception(show_locals=True, width=160)

            return 1

    def validate_args(self) -> bool:
        """인수 검증"""
        return True

    def setup_logging(self):
        """로깅 설정"""
        if hasattr(self.args, 'debug') and self.args.debug:
            pawn.set(PAWN_DEBUG=True)

        if hasattr(self.args, 'verbose') and self.args.verbose:
            pawn.set(PAWN_VERBOSE=self.args.verbose)

    def log_info(self, message: str):
        """정보 로그"""
        pawn.console.log(f"ℹ️  {message}")

    def log_success(self, message: str):
        """성공 로그"""
        pawn.console.log(f"[green]✅ {message}[/green]")

    def log_warning(self, message: str):
        """경고 로그"""
        pawn.console.log(f"[yellow]⚠️  {message}[/yellow]")

    def log_error(self, message: str):
        """오류 로그"""
        pawn.console.log(f"[red]❌ {message}[/red]")

    def log_debug(self, message: str):
        """디버그 로그"""
        if pawn.get('PAWN_DEBUG'):
            pawn.console.log(f"[dim]🐛 {message}[/dim]")


class AsyncBaseCLI(BaseCLI):
    """비동기 CLI 명령어 기본 클래스"""

    @abstractmethod
    async def run_async(self) -> int:
        """비동기 명령어 실행"""
        pass

    def run(self) -> int:
        """동기 실행 (비동기 래퍼)"""
        return asyncio.run(self.run_async())


class HTTPBaseCLI(BaseCLI):
    """HTTP 관련 CLI 명령어 기본 클래스"""

    def get_common_http_arguments(self, parser: ArgumentParser):
        """HTTP 공통 인수 추가"""
        parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='Request timeout in seconds (default: 30)'
        )

        parser.add_argument(
            '--retry',
            type=int,
            default=3,
            help='Number of retries (default: 3)'
        )

        parser.add_argument(
            '--headers',
            type=str,
            action='append',
            help='HTTP headers (format: "Key: Value")'
        )

        parser.add_argument(
            '--user-agent',
            type=str,
            default='PawnStack-CLI/1.0.0',
            help='User-Agent header'
        )

        parser.add_argument(
            '--no-ssl-verify',
            action='store_true',
            help='Disable SSL certificate verification'
        )

    def parse_headers(self) -> Dict[str, str]:
        """헤더 파싱"""
        headers = {}

        if hasattr(self.args, 'headers') and self.args.headers:
            for header in self.args.headers:
                if ':' in header:
                    key, value = header.split(':', 1)
                    headers[key.strip()] = value.strip()

        if hasattr(self.args, 'user_agent'):
            headers['User-Agent'] = self.args.user_agent

        return headers


class MonitoringBaseCLI(AsyncBaseCLI):
    """모니터링 관련 CLI 명령어 기본 클래스"""

    def get_common_monitoring_arguments(self, parser: ArgumentParser):
        """모니터링 공통 인수 추가"""
        parser.add_argument(
            '--interval',
            type=int,
            default=5,
            help='Monitoring interval in seconds (default: 5)'
        )

        parser.add_argument(
            '--duration',
            type=int,
            help='Monitoring duration in seconds (default: infinite)'
        )

        parser.add_argument(
            '--threshold',
            type=float,
            help='Alert threshold'
        )

        parser.add_argument(
            '--output-file',
            type=str,
            help='Output file for monitoring data'
        )

    async def monitor_loop(self, monitor_func, interval: int = 5, duration: Optional[int] = None):
        """모니터링 루프"""
        start_time = time.time()

        try:
            while True:
                await monitor_func()

                if duration and (time.time() - start_time) >= duration:
                    break

                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            self.log_info("Monitoring stopped by user")


class FileBaseCLI(BaseCLI):
    """파일 관련 CLI 명령어 기본 클래스"""

    def get_common_file_arguments(self, parser: ArgumentParser):
        """파일 공통 인수 추가"""
        parser.add_argument(
            '--input', '-i',
            type=str,
            help='Input file path'
        )

        parser.add_argument(
            '--output', '-o',
            type=str,
            help='Output file path'
        )

        parser.add_argument(
            '--format',
            choices=['json', 'yaml', 'csv', 'txt'],
            default='json',
            help='Output format (default: json)'
        )

        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing files'
        )

    def check_file_exists(self, file_path: str) -> bool:
        """파일 존재 확인"""
        from pathlib import Path
        return Path(file_path).exists()

    def ensure_output_dir(self, file_path: str):
        """출력 디렉토리 생성"""
        from pathlib import Path
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)


def create_cli_function(cli_class):
    """CLI 클래스를 함수로 변환하는 데코레이터"""
    def wrapper():
        cli = cli_class()
        return cli.main()

    # 함수 메타데이터 복사
    wrapper.__name__ = f"{cli_class.__name__.lower()}_main"
    wrapper.__doc__ = cli_class.__doc__

    return wrapper


def register_cli_command(name: str, description: str, epilog: str = ""):
    """CLI 명령어 등록 데코레이터"""
    def decorator(cls):
        cls.__command_name__ = name
        cls.__description__ = description
        cls.__epilog__ = epilog
        return cls

    return decorator


# 의존성 검사 시스템은 pawnstack.cli.dependencies 모듈로 이동됨


class BlockchainBaseCLI(AsyncBaseCLI):
    """블록체인 관련 CLI 명령어 기본 클래스"""

    REQUIRED_EXTRAS = ['blockchain']

    def __init__(self, args: Optional[Namespace] = None):
        super().__init__(args)
        self.network_configs = {
            'mainnet': {
                'rpc_url': 'https://ctz.solidwallet.io/api/v3',
                'nid': '0x1'
            },
            'testnet': {
                'rpc_url': 'https://test-ctz.solidwallet.io/api/v3',
                'nid': '0x2'
            },
            'local': {
                'rpc_url': 'http://localhost:9000/api/v3',
                'nid': '0x3'
            }
        }

    def get_common_blockchain_arguments(self, parser: ArgumentParser):
        """블록체인 공통 인수 추가"""
        parser.add_argument(
            '--network',
            choices=['mainnet', 'testnet', 'local'],
            default='mainnet',
            help='블록체인 네트워크 선택 (default: mainnet)'
        )

        parser.add_argument(
            '--rpc-url',
            type=str,
            help='RPC 엔드포인트 URL (네트워크 기본값 오버라이드)'
        )

        parser.add_argument(
            '--keystore',
            type=str,
            help='키스토어 파일 경로'
        )

        parser.add_argument(
            '--password',
            type=str,
            help='키스토어 비밀번호 (환경변수 KEYSTORE_PASSWORD 사용 권장)'
        )

        parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='RPC 요청 타임아웃 (초, default: 30)'
        )

        parser.add_argument(
            '--retry',
            type=int,
            default=3,
            help='RPC 요청 재시도 횟수 (default: 3)'
        )

    def get_rpc_url(self) -> str:
        """RPC URL 반환"""
        if hasattr(self.args, 'rpc_url') and self.args.rpc_url:
            return self.args.rpc_url

        network = getattr(self.args, 'network', 'mainnet')
        return self.network_configs[network]['rpc_url']

    def get_network_id(self) -> str:
        """네트워크 ID 반환"""
        network = getattr(self.args, 'network', 'mainnet')
        return self.network_configs[network]['nid']

    def validate_keystore(self) -> bool:
        """키스토어 파일 검증"""
        if not hasattr(self.args, 'keystore') or not self.args.keystore:
            return True  # 키스토어가 필수가 아닌 경우

        from pathlib import Path
        keystore_path = Path(self.args.keystore)

        if not keystore_path.exists():
            self.log_error(f"키스토어 파일을 찾을 수 없습니다: {self.args.keystore}")
            return False

        try:
            import json
            with open(keystore_path, 'r') as f:
                keystore_data = json.load(f)

            # 기본적인 키스토어 구조 검증
            required_fields = ['version', 'id', 'crypto']
            for field in required_fields:
                if field not in keystore_data:
                    self.log_error(f"유효하지 않은 키스토어 파일: {field} 필드 누락")
                    return False

            return True

        except json.JSONDecodeError:
            self.log_error("키스토어 파일이 유효한 JSON 형식이 아닙니다")
            return False
        except Exception as e:
            self.log_error(f"키스토어 파일 검증 중 오류 발생: {e}")
            return False

    def check_dependencies(self) -> bool:
        """블록체인 의존성 검사"""
        return DependencyChecker.check_dependencies(self.REQUIRED_EXTRAS)

    async def run_async(self) -> int:
        """비동기 실행 (의존성 검사 포함)"""
        if not self.check_dependencies():
            return 1

        if not self.validate_keystore():
            return 1

        return await super().run_async()


class CloudBaseCLI(AsyncBaseCLI):
    """클라우드 관련 CLI 명령어 기본 클래스"""

    REQUIRED_EXTRAS = ['aws']

    def __init__(self, args: Optional[Namespace] = None):
        super().__init__(args)
        self.aws_regions = [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-central-1', 'eu-north-1',
            'ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3',
            'ap-southeast-1', 'ap-southeast-2', 'ap-southeast-3',
            'ap-south-1', 'ap-east-1', 'sa-east-1', 'ca-central-1',
            'me-south-1', 'af-south-1'
        ]
        self._aws_session = None
        self._aws_clients = {}
        self._credentials_cache = {}

    def get_common_cloud_arguments(self, parser: ArgumentParser):
        """클라우드 공통 인수 추가"""
        parser.add_argument(
            '--profile',
            type=str,
            help='AWS 프로필 이름 (기본값: default)'
        )

        parser.add_argument(
            '--region',
            type=str,
            choices=self.aws_regions,
            help='AWS 리전 (예: ap-northeast-2)'
        )

        parser.add_argument(
            '--access-key-id',
            type=str,
            help='AWS Access Key ID (환경변수 AWS_ACCESS_KEY_ID 사용 권장)'
        )

        parser.add_argument(
            '--secret-access-key',
            type=str,
            help='AWS Secret Access Key (환경변수 AWS_SECRET_ACCESS_KEY 사용 권장)'
        )

        parser.add_argument(
            '--session-token',
            type=str,
            help='AWS Session Token (임시 자격 증명용)'
        )

        parser.add_argument(
            '--endpoint-url',
            type=str,
            help='커스텀 엔드포인트 URL (LocalStack 등)'
        )

        parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='AWS API 요청 타임아웃 (초, default: 30)'
        )

        parser.add_argument(
            '--retry-attempts',
            type=int,
            default=3,
            help='AWS API 요청 재시도 횟수 (default: 3)'
        )

        parser.add_argument(
            '--output-format',
            choices=['json', 'yaml', 'table', 'csv'],
            default='table',
            help='출력 형식 (default: table)'
        )

        parser.add_argument(
            '--no-ssl-verify',
            action='store_true',
            help='SSL 인증서 검증 비활성화'
        )

    def get_aws_config(self) -> Dict[str, Any]:
        """AWS 설정 반환"""
        import os

        config = {}

        # 프로필 설정
        if hasattr(self.args, 'profile') and self.args.profile:
            config['profile_name'] = self.args.profile

        # 리전 설정 (우선순위: 인수 > 환경변수 > 기본값)
        region = None
        if hasattr(self.args, 'region') and self.args.region:
            region = self.args.region
        elif os.getenv('AWS_DEFAULT_REGION'):
            region = os.getenv('AWS_DEFAULT_REGION')
        elif os.getenv('AWS_REGION'):
            region = os.getenv('AWS_REGION')

        if region:
            config['region_name'] = region

        # 자격 증명 설정 (환경변수 우선)
        access_key = (
            getattr(self.args, 'access_key_id', None) or
            os.getenv('AWS_ACCESS_KEY_ID')
        )
        secret_key = (
            getattr(self.args, 'secret_access_key', None) or
            os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        session_token = (
            getattr(self.args, 'session_token', None) or
            os.getenv('AWS_SESSION_TOKEN')
        )

        if access_key:
            config['aws_access_key_id'] = access_key
        if secret_key:
            config['aws_secret_access_key'] = secret_key
        if session_token:
            config['aws_session_token'] = session_token

        return config

    def get_boto3_config(self) -> Dict[str, Any]:
        """Boto3 클라이언트 설정 반환"""
        from botocore.config import Config

        # 재시도 설정
        retry_config = {
            'max_attempts': getattr(self.args, 'retry_attempts', 3),
            'mode': 'adaptive'
        }

        # 타임아웃 설정
        timeout = getattr(self.args, 'timeout', 30)

        # SSL 검증 설정
        use_ssl = not getattr(self.args, 'no_ssl_verify', False)

        config = Config(
            retries=retry_config,
            read_timeout=timeout,
            connect_timeout=timeout,
            use_ssl=use_ssl
        )

        client_config = {'config': config}

        # 엔드포인트 URL 설정 (LocalStack 등)
        if hasattr(self.args, 'endpoint_url') and self.args.endpoint_url:
            client_config['endpoint_url'] = self.args.endpoint_url

        return client_config

    async def get_aws_session(self):
        """AWS 세션 반환 (캐시됨)"""
        if self._aws_session is None:
            try:
                import aioboto3

                aws_config = self.get_aws_config()
                self._aws_session = aioboto3.Session(**aws_config)

                self.log_debug("AWS 세션 생성 완료")

            except ImportError:
                self.log_error("aioboto3 패키지가 설치되지 않았습니다")
                raise
            except Exception as e:
                self.log_error(f"AWS 세션 생성 실패: {e}")
                raise

        return self._aws_session

    async def get_aws_client(self, service_name: str):
        """AWS 클라이언트 반환 (캐시됨)"""
        if service_name not in self._aws_clients:
            try:
                session = await self.get_aws_session()
                boto3_config = self.get_boto3_config()

                self._aws_clients[service_name] = session.client(
                    service_name,
                    **boto3_config
                )

                self.log_debug(f"AWS {service_name} 클라이언트 생성 완료")

            except Exception as e:
                self.log_error(f"AWS {service_name} 클라이언트 생성 실패: {e}")
                raise

        return self._aws_clients[service_name]

    async def close_aws_clients(self):
        """AWS 클라이언트 연결 종료"""
        for service_name, client in self._aws_clients.items():
            try:
                if hasattr(client, 'close'):
                    await client.close()
                self.log_debug(f"AWS {service_name} 클라이언트 연결 종료")
            except Exception as e:
                self.log_warning(f"AWS {service_name} 클라이언트 종료 중 오류: {e}")

        self._aws_clients.clear()
        self._aws_session = None

    async def validate_aws_credentials(self) -> bool:
        """AWS 자격 증명 검증"""
        try:
            # STS를 사용하여 자격 증명 검증
            sts_client = await self.get_aws_client('sts')

            async with sts_client as sts:
                identity = await sts.get_caller_identity()

                # 자격 증명 정보 캐시 (보안상 민감한 정보는 제외)
                self._credentials_cache = {
                    'account_id': identity.get('Account'),
                    'user_id': identity.get('UserId'),
                    'arn': identity.get('Arn')
                }

                self.log_debug(f"AWS 자격 증명 검증 완료: {identity.get('Arn')}")
                return True

        except Exception as e:
            error_msg = str(e)

            if 'NoCredentialsError' in error_msg or 'Unable to locate credentials' in error_msg:
                self.log_error("AWS 자격 증명을 찾을 수 없습니다")
                self.log_info("다음 방법 중 하나로 자격 증명을 설정하세요:")
                self.log_info("  1. AWS CLI: aws configure")
                self.log_info("  2. 환경 변수: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
                self.log_info("  3. IAM 역할 (EC2 인스턴스)")
                self.log_info("  4. --profile 옵션으로 프로필 지정")
            elif 'InvalidUserID.NotFound' in error_msg:
                self.log_error("유효하지 않은 AWS 자격 증명입니다")
            elif 'SignatureDoesNotMatch' in error_msg:
                self.log_error("AWS 자격 증명 서명이 일치하지 않습니다")
            elif 'TokenRefreshRequired' in error_msg:
                self.log_error("AWS 토큰이 만료되었습니다. 새로 로그인하세요")
            else:
                self.log_error(f"AWS 자격 증명 검증 실패: {error_msg}")

            return False

    def get_caller_identity(self) -> Dict[str, str]:
        """캐시된 AWS 자격 증명 정보 반환"""
        return self._credentials_cache.copy()

    async def get_available_regions(self, service_name: str = 'ec2') -> List[str]:
        """지정된 서비스에서 사용 가능한 리전 목록 반환"""
        try:
            ec2_client = await self.get_aws_client('ec2')

            async with ec2_client as ec2:
                response = await ec2.describe_regions()
                regions = [region['RegionName'] for region in response['Regions']]
                return sorted(regions)

        except Exception as e:
            self.log_warning(f"사용 가능한 리전 조회 실패: {e}")
            return self.aws_regions  # 기본 리전 목록 반환

    async def get_account_info(self) -> Dict[str, Any]:
        """AWS 계정 정보 반환"""
        try:
            # 자격 증명 정보
            identity = self.get_caller_identity()

            # 계정 별칭 조회
            iam_client = await self.get_aws_client('iam')

            async with iam_client as iam:
                try:
                    aliases_response = await iam.list_account_aliases()
                    aliases = aliases_response.get('AccountAliases', [])
                    account_alias = aliases[0] if aliases else None
                except Exception:
                    account_alias = None

            # 현재 리전 정보
            session = await self.get_aws_session()
            current_region = session.region_name

            return {
                'account_id': identity.get('account_id'),
                'account_alias': account_alias,
                'user_arn': identity.get('arn'),
                'user_id': identity.get('user_id'),
                'current_region': current_region,
                'profile': getattr(self.args, 'profile', 'default')
            }

        except Exception as e:
            self.log_error(f"AWS 계정 정보 조회 실패: {e}")
            return {}

    def format_output(self, data: Any, format_type: str = None) -> str:
        """데이터를 지정된 형식으로 포맷팅"""
        if format_type is None:
            format_type = getattr(self.args, 'output_format', 'table')

        if format_type == 'json':
            import json
            from datetime import datetime

            def json_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

            return json.dumps(data, indent=2, default=json_serializer, ensure_ascii=False)

        elif format_type == 'yaml':
            try:
                import yaml
                return yaml.dump(data, default_flow_style=False, allow_unicode=True)
            except ImportError:
                self.log_warning("PyYAML이 설치되지 않았습니다. JSON 형식으로 출력합니다.")
                return self.format_output(data, 'json')

        elif format_type == 'csv':
            if isinstance(data, list) and data and isinstance(data[0], dict):
                import csv
                import io

                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
                return output.getvalue()
            else:
                self.log_warning("CSV 형식은 딕셔너리 리스트만 지원합니다. JSON 형식으로 출력합니다.")
                return self.format_output(data, 'json')

        elif format_type == 'table':
            return self._format_as_table(data)

        else:
            self.log_warning(f"지원하지 않는 출력 형식: {format_type}. JSON 형식으로 출력합니다.")
            return self.format_output(data, 'json')

    def _format_as_table(self, data: Any) -> str:
        """데이터를 Rich 테이블 형식으로 포맷팅"""
        from rich.table import Table
        from rich.console import Console
        import io

        console = Console(file=io.StringIO(), width=120)

        if isinstance(data, list) and data:
            if isinstance(data[0], dict):
                # 딕셔너리 리스트를 테이블로 변환
                table = Table(show_header=True, header_style="bold magenta")

                # 헤더 추가
                headers = list(data[0].keys())
                for header in headers:
                    table.add_column(header, style="dim")

                # 데이터 행 추가
                for item in data:
                    row = [str(item.get(header, '')) for header in headers]
                    table.add_row(*row)

                console.print(table)
            else:
                # 단순 리스트
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Index", style="dim")
                table.add_column("Value")

                for i, item in enumerate(data):
                    table.add_row(str(i), str(item))

                console.print(table)

        elif isinstance(data, dict):
            # 딕셔너리를 키-값 테이블로 변환
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Key", style="dim")
            table.add_column("Value")

            for key, value in data.items():
                table.add_row(str(key), str(value))

            console.print(table)

        else:
            # 기타 데이터 타입
            console.print(str(data))

        return console.file.getvalue()

    def check_dependencies(self) -> bool:
        """클라우드 의존성 검사"""
        return DependencyChecker.check_dependencies(self.REQUIRED_EXTRAS)

    async def run_async(self) -> int:
        """비동기 실행 (의존성 검사 포함)"""
        try:
            if not self.check_dependencies():
                return 1

            # AWS 자격 증명 검증은 선택적 (명령어에 따라 다름)
            if hasattr(self.args, 'validate_credentials') and self.args.validate_credentials:
                if not await self.validate_aws_credentials():
                    return 1

            return await super().run_async()

        finally:
            # 리소스 정리
            await self.close_aws_clients()


class ContainerBaseCLI(AsyncBaseCLI):
    """컨테이너 관련 CLI 명령어 기본 클래스"""

    REQUIRED_EXTRAS = ['docker']

    def __init__(self, args: Optional[Namespace] = None):
        super().__init__(args)
        self._docker_client = None
        self._compose_config = None

    def get_common_container_arguments(self, parser: ArgumentParser):
        """컨테이너 공통 인수 추가"""
        parser.add_argument(
            '--docker-host',
            type=str,
            help='Docker 데몬 호스트 (예: unix:///var/run/docker.sock, tcp://localhost:2376)'
        )

        parser.add_argument(
            '--compose-file', '-f',
            type=str,
            default='docker-compose.yml',
            help='Docker Compose 파일 경로 (default: docker-compose.yml)'
        )

        parser.add_argument(
            '--project-name', '-p',
            type=str,
            help='Docker Compose 프로젝트 이름'
        )

        parser.add_argument(
            '--env-file',
            type=str,
            help='환경 변수 파일 경로'
        )

        parser.add_argument(
            '--timeout',
            type=int,
            default=60,
            help='Docker 작업 타임아웃 (초, default: 60)'
        )

        parser.add_argument(
            '--tls',
            action='store_true',
            help='Docker TLS 연결 사용'
        )

        parser.add_argument(
            '--tls-verify',
            action='store_true',
            help='Docker TLS 인증서 검증'
        )

        parser.add_argument(
            '--cert-path',
            type=str,
            help='Docker TLS 인증서 경로'
        )

    def get_docker_config(self) -> Dict[str, Any]:
        """Docker 설정 반환"""
        config = {}

        # Docker 호스트 설정
        if hasattr(self.args, 'docker_host') and self.args.docker_host:
            config['base_url'] = self.args.docker_host
        else:
            # 기본 Docker 소켓 경로
            import os
            if os.name == 'nt':  # Windows
                config['base_url'] = 'npipe:////./pipe/docker_engine'
            else:  # Unix/Linux/macOS
                config['base_url'] = 'unix:///var/run/docker.sock'

        # 타임아웃 설정
        if hasattr(self.args, 'timeout'):
            config['timeout'] = self.args.timeout
        else:
            config['timeout'] = 60

        # TLS 설정
        if hasattr(self.args, 'tls') and self.args.tls:
            config['tls'] = True

            if hasattr(self.args, 'tls_verify') and self.args.tls_verify:
                config['tls_verify'] = True

            if hasattr(self.args, 'cert_path') and self.args.cert_path:
                config['cert_path'] = self.args.cert_path

        return config

    async def get_docker_client(self):
        """Docker 클라이언트 반환 (연결 관리)"""
        if self._docker_client is None:
            try:
                import aiodocker
                config = self.get_docker_config()
                self._docker_client = aiodocker.Docker(**config)

                # 연결 테스트
                await self._docker_client.version()
                self.log_debug("Docker 클라이언트 연결 성공")

            except ImportError:
                self.log_error("aiodocker 패키지가 설치되지 않았습니다")
                raise
            except Exception as e:
                self.log_error(f"Docker 클라이언트 연결 실패: {e}")
                raise

        return self._docker_client

    async def close_docker_client(self):
        """Docker 클라이언트 연결 종료"""
        if self._docker_client:
            try:
                await self._docker_client.close()
                self.log_debug("Docker 클라이언트 연결 종료")
            except Exception as e:
                self.log_warning(f"Docker 클라이언트 종료 중 오류: {e}")
            finally:
                self._docker_client = None

    def load_compose_config(self) -> Dict[str, Any]:
        """Docker Compose 설정 로드"""
        if self._compose_config is not None:
            return self._compose_config

        from pathlib import Path

        compose_file = getattr(self.args, 'compose_file', 'docker-compose.yml')
        compose_path = Path(compose_file)

        if not compose_path.exists():
            self.log_warning(f"Docker Compose 파일을 찾을 수 없습니다: {compose_file}")
            return {}

        try:
            import yaml
            with open(compose_path, 'r', encoding='utf-8') as f:
                self._compose_config = yaml.safe_load(f) or {}

            self.log_debug(f"Docker Compose 설정 로드 완료: {compose_file}")
            return self._compose_config

        except yaml.YAMLError as e:
            self.log_error(f"Docker Compose 파일 파싱 오류: {e}")
            return {}
        except Exception as e:
            self.log_error(f"Docker Compose 파일 로드 중 오류: {e}")
            return {}

    def get_compose_services(self) -> List[str]:
        """Docker Compose 서비스 목록 반환"""
        compose_config = self.load_compose_config()
        services = compose_config.get('services', {})
        return list(services.keys())

    def get_project_name(self) -> str:
        """Docker Compose 프로젝트 이름 반환"""
        if hasattr(self.args, 'project_name') and self.args.project_name:
            return self.args.project_name

        # 현재 디렉토리 이름을 기본 프로젝트 이름으로 사용
        from pathlib import Path
        return Path.cwd().name.lower().replace('_', '').replace('-', '')

    def load_env_file(self) -> Dict[str, str]:
        """환경 변수 파일 로드"""
        env_vars = {}

        if hasattr(self.args, 'env_file') and self.args.env_file:
            from pathlib import Path
            env_path = Path(self.args.env_file)

            if env_path.exists():
                try:
                    with open(env_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                env_vars[key.strip()] = value.strip()

                    self.log_debug(f"환경 변수 파일 로드 완료: {self.args.env_file}")

                except Exception as e:
                    self.log_warning(f"환경 변수 파일 로드 실패: {e}")

        return env_vars

    async def validate_docker_connection(self) -> bool:
        """Docker 연결 검증"""
        try:
            docker = await self.get_docker_client()
            version_info = await docker.version()

            self.log_debug(f"Docker 버전: {version_info.get('Version', 'Unknown')}")
            self.log_debug(f"Docker API 버전: {version_info.get('ApiVersion', 'Unknown')}")

            return True

        except Exception as e:
            self.log_error(f"Docker 연결 실패: {e}")
            self.log_info("Docker 데몬이 실행 중인지 확인하세요")
            return False

    def validate_compose_file(self) -> bool:
        """Docker Compose 파일 검증"""
        if not hasattr(self.args, 'compose_file') or not self.args.compose_file:
            return True  # Compose 파일이 필수가 아닌 경우

        from pathlib import Path
        compose_path = Path(self.args.compose_file)

        if not compose_path.exists():
            self.log_error(f"Docker Compose 파일을 찾을 수 없습니다: {self.args.compose_file}")
            return False

        try:
            compose_config = self.load_compose_config()

            # 기본적인 Compose 파일 구조 검증
            if not isinstance(compose_config, dict):
                self.log_error("유효하지 않은 Docker Compose 파일 형식")
                return False

            if 'services' not in compose_config:
                self.log_error("Docker Compose 파일에 services 섹션이 없습니다")
                return False

            services = compose_config['services']
            if not isinstance(services, dict) or not services:
                self.log_error("services 섹션이 비어있거나 유효하지 않습니다")
                return False

            # 각 서비스의 기본 구조 검증
            for service_name, service_config in services.items():
                if not isinstance(service_config, dict):
                    self.log_error(f"서비스 '{service_name}' 설정이 유효하지 않습니다")
                    return False

                # image 또는 build 중 하나는 있어야 함
                if 'image' not in service_config and 'build' not in service_config:
                    self.log_error(f"서비스 '{service_name}'에 image 또는 build 설정이 없습니다")
                    return False

            self.log_debug(f"Docker Compose 파일 검증 완료: {len(services)}개 서비스")
            return True

        except Exception as e:
            self.log_error(f"Docker Compose 파일 검증 중 오류 발생: {e}")
            return False

    def check_dependencies(self) -> bool:
        """컨테이너 의존성 검사"""
        return DependencyChecker.check_dependencies(self.REQUIRED_EXTRAS)

    async def container_exists(self, container_name: str) -> bool:
        """컨테이너 존재 여부 확인"""
        try:
            docker = await self.get_docker_client()
            containers = await docker.containers.list(all=True)

            for container in containers:
                names = container._container.get('Names', [])
                # Docker는 컨테이너 이름 앞에 '/'를 붙임
                if f"/{container_name}" in names or container_name in names:
                    return True

            return False

        except Exception as e:
            self.log_error(f"컨테이너 존재 확인 중 오류: {e}")
            return False

    async def get_container_status(self, container_name: str) -> Optional[str]:
        """컨테이너 상태 반환"""
        try:
            docker = await self.get_docker_client()
            containers = await docker.containers.list(all=True)

            for container in containers:
                names = container._container.get('Names', [])
                if f"/{container_name}" in names or container_name in names:
                    return container._container.get('State', 'unknown')

            return None

        except Exception as e:
            self.log_error(f"컨테이너 상태 확인 중 오류: {e}")
            return None

    async def run_async(self) -> int:
        """비동기 실행 (의존성 검사 포함)"""
        try:
            if not self.check_dependencies():
                return 1

            if not self.validate_compose_file():
                return 1

            # Docker 연결 검증은 선택적 (명령어에 따라 다름)
            if hasattr(self.args, 'validate_docker') and self.args.validate_docker:
                if not await self.validate_docker_connection():
                    return 1

            return await super().run_async()

        finally:
            # 리소스 정리
            await self.close_docker_client()
