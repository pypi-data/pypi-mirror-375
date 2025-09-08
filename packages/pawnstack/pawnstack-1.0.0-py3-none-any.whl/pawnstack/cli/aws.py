#!/usr/bin/env python3
"""
AWS CLI 명령어

AWS 메타데이터 조회 및 Route53 관리 기능을 제공합니다.
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from argparse import ArgumentParser

from pawnstack.cli.base import CloudBaseCLI, register_cli_command
from pawnstack.config.global_config import pawn


@register_cli_command(
    name="aws",
    description="AWS 메타데이터 조회 및 Route53 관리",
    epilog="""
사용 예제:
  1. AWS 메타데이터 조회:
     pawns aws metadata --output-format json

  2. AWS 계정 정보 조회:
     pawns aws info --profile production

  3. Route53 호스팅 영역 목록:
     pawns aws route53 ls --profile production

  4. Route53 호스팅 영역 백업:
     pawns aws route53 backup /hostedzone/Z123456789 backup.json

  5. Route53 호스팅 영역 복원:
     pawns aws route53 restore backup.json example.com

  6. 모든 Route53 호스팅 영역 백업:
     pawns aws route53 backup all
"""
)
class AWSCLI(CloudBaseCLI):
    """AWS CLI 명령어 클래스"""

    def __init__(self, args=None):
        super().__init__(args)
        self.metadata_ip = "169.254.169.254"
        self.metadata_timeout = 2

    def get_arguments(self, parser: ArgumentParser):
        """AWS CLI 인수 정의"""
        # 공통 클라우드 인수 추가
        self.get_common_cloud_arguments(parser)

        # 서브커맨드 정의
        subparsers = parser.add_subparsers(dest='subcommand', help='AWS 서브커맨드')

        # metadata 서브커맨드
        metadata_parser = subparsers.add_parser(
            'metadata',
            help='EC2 메타데이터 조회'
        )
        metadata_parser.add_argument(
            '--metadata-ip', '-i',
            type=str,
            default="169.254.169.254",
            help='메타데이터 서비스 IP 주소 (default: 169.254.169.254)'
        )
        metadata_parser.add_argument(
            '--metadata-timeout', '-t',
            type=float,
            default=2,
            help='메타데이터 요청 타임아웃 (초, default: 2)'
        )
        metadata_parser.add_argument(
            '--output-file', '-o',
            type=str,
            help='출력 파일 경로'
        )

        # info 서브커맨드
        info_parser = subparsers.add_parser(
            'info',
            help='AWS 계정 및 자격 증명 정보 조회'
        )
        info_parser.add_argument(
            '--validate-credentials',
            action='store_true',
            help='자격 증명 검증 수행'
        )

        # route53 서브커맨드
        route53_parser = subparsers.add_parser(
            'route53',
            help='Route53 관리'
        )
        route53_subparsers = route53_parser.add_subparsers(
            dest='route53_command',
            help='Route53 명령어'
        )

        # route53 ls
        ls_parser = route53_subparsers.add_parser(
            'ls',
            help='호스팅 영역 목록 조회'
        )
        ls_parser.add_argument(
            '--include-records',
            action='store_true',
            help='레코드 세트 정보 포함'
        )

        # route53 backup
        backup_parser = route53_subparsers.add_parser(
            'backup',
            help='호스팅 영역 백업'
        )
        backup_parser.add_argument(
            'zone_id',
            help='호스팅 영역 ID 또는 "all"'
        )
        backup_parser.add_argument(
            'backup_file',
            nargs='?',
            help='백업 파일 경로 (JSON 형식)'
        )

        # route53 restore
        restore_parser = route53_subparsers.add_parser(
            'restore',
            help='호스팅 영역 복원'
        )
        restore_parser.add_argument(
            'backup_file',
            help='백업 파일 경로'
        )
        restore_parser.add_argument(
            'new_zone_name',
            help='새 호스팅 영역 이름'
        )
        restore_parser.add_argument(
            '--dry-run',
            action='store_true',
            help='실제 실행하지 않고 계획만 표시'
        )

    async def run_async(self) -> int:
        """AWS CLI 비동기 실행"""
        try:
            # 서브커맨드에 따른 실행
            if not hasattr(self.args, 'subcommand') or not self.args.subcommand:
                return await self._show_help()

            if self.args.subcommand == 'metadata':
                return await self._handle_metadata()
            elif self.args.subcommand == 'info':
                return await self._handle_info()
            elif self.args.subcommand == 'route53':
                return await self._handle_route53()
            else:
                self.log_error(f"알 수 없는 서브커맨드: {self.args.subcommand}")
                return 1

        except Exception as e:
            self.log_error(f"AWS CLI 실행 중 오류 발생: {e}")
            if pawn.get('PAWN_DEBUG'):
                pawn.console.print_exception(show_locals=True)
            return 1

    async def _show_help(self) -> int:
        """도움말 표시"""
        pawn.console.log("AWS CLI 사용법:")
        pawn.console.log("  pawns aws metadata    # EC2 메타데이터 조회")
        pawn.console.log("  pawns aws info         # AWS 계정 정보 조회")
        pawn.console.log("  pawns aws route53 ls   # Route53 호스팅 영역 목록")
        pawn.console.log("")
        pawn.console.log("자세한 사용법은 --help 옵션을 사용하세요.")
        return 0

    async def _handle_metadata(self) -> int:
        """EC2 메타데이터 처리"""
        try:
            metadata = await self._get_ec2_metadata()

            if not metadata:
                self.log_warning("메타데이터를 가져올 수 없습니다. EC2 인스턴스에서 실행 중인지 확인하세요.")
                return 1

            # 출력 형식에 따른 처리
            output_format = getattr(self.args, 'output_format', 'table')
            formatted_output = self.format_output(metadata, output_format)

            # 파일 출력
            if hasattr(self.args, 'output_file') and self.args.output_file:
                await self._write_output_file(self.args.output_file, metadata)
                self.log_success(f"메타데이터를 {self.args.output_file}에 저장했습니다")

            # 콘솔 출력
            if output_format == 'table':
                pawn.console.print(formatted_output)
            else:
                print(formatted_output)

            return 0

        except Exception as e:
            self.log_error(f"메타데이터 조회 실패: {e}")
            return 1

    async def _handle_info(self) -> int:
        """AWS 계정 정보 처리"""
        try:
            # 자격 증명 검증
            if getattr(self.args, 'validate_credentials', False):
                if not await self.validate_aws_credentials():
                    return 1

            # 계정 정보 조회
            account_info = await self.get_account_info()

            if not account_info:
                self.log_error("AWS 계정 정보를 조회할 수 없습니다")
                return 1

            # 추가 정보 수집
            try:
                # 사용 가능한 리전 조회
                regions = await self.get_available_regions()
                account_info['available_regions_count'] = len(regions)

                # 현재 사용자 정보
                identity = self.get_caller_identity()
                if identity:
                    account_info.update(identity)

            except Exception as e:
                self.log_warning(f"추가 정보 조회 실패: {e}")

            # 출력
            formatted_output = self.format_output(account_info)
            pawn.console.print(formatted_output)

            return 0

        except Exception as e:
            self.log_error(f"AWS 계정 정보 조회 실패: {e}")
            return 1

    async def _handle_route53(self) -> int:
        """Route53 관리 처리"""
        if not hasattr(self.args, 'route53_command') or not self.args.route53_command:
            self.log_error("Route53 명령어를 지정해주세요 (ls, backup, restore)")
            return 1

        # 자격 증명 검증
        if not await self.validate_aws_credentials():
            return 1

        try:
            if self.args.route53_command == 'ls':
                return await self._route53_list()
            elif self.args.route53_command == 'backup':
                return await self._route53_backup()
            elif self.args.route53_command == 'restore':
                return await self._route53_restore()
            else:
                self.log_error(f"알 수 없는 Route53 명령어: {self.args.route53_command}")
                return 1

        except Exception as e:
            self.log_error(f"Route53 작업 실패: {e}")
            return 1

    async def _get_ec2_metadata(self) -> Optional[Dict[str, Any]]:
        """EC2 메타데이터 조회"""
        try:
            import aiohttp

            metadata_ip = getattr(self.args, 'metadata_ip', self.metadata_ip)
            timeout = getattr(self.args, 'metadata_timeout', self.metadata_timeout)

            base_url = f"http://{metadata_ip}/latest/meta-data/"

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                metadata = {}

                # 기본 메타데이터 항목들
                metadata_items = [
                    'instance-id',
                    'instance-type',
                    'local-hostname',
                    'local-ipv4',
                    'public-hostname',
                    'public-ipv4',
                    'ami-id',
                    'security-groups',
                    'placement/availability-zone',
                    'placement/region'
                ]

                for item in metadata_items:
                    try:
                        async with session.get(f"{base_url}{item}") as response:
                            if response.status == 200:
                                value = await response.text()
                                # 중첩된 키 처리
                                if '/' in item:
                                    keys = item.split('/')
                                    current = metadata
                                    for key in keys[:-1]:
                                        if key not in current:
                                            current[key] = {}
                                        current = current[key]
                                    current[keys[-1]] = value
                                else:
                                    metadata[item] = value
                    except Exception:
                        # 개별 항목 실패는 무시
                        pass

                # IAM 역할 정보 (있는 경우)
                try:
                    async with session.get(f"{base_url}iam/security-credentials/") as response:
                        if response.status == 200:
                            role_name = await response.text()
                            if role_name:
                                async with session.get(f"{base_url}iam/security-credentials/{role_name}") as role_response:
                                    if role_response.status == 200:
                                        role_data = await role_response.json()
                                        metadata['iam'] = {
                                            'role_name': role_name,
                                            'credentials': {
                                                'access_key_id': role_data.get('AccessKeyId', ''),
                                                'expiration': role_data.get('Expiration', ''),
                                                'type': role_data.get('Type', '')
                                            }
                                        }
                except Exception:
                    pass

                return metadata if metadata else None

        except ImportError:
            self.log_error("aiohttp 패키지가 필요합니다: pip install aiohttp")
            return None
        except Exception as e:
            self.log_debug(f"메타데이터 조회 실패: {e}")
            return None

    async def _route53_list(self) -> int:
        """Route53 호스팅 영역 목록 조회"""
        try:
            route53_client = await self.get_aws_client('route53')

            async with route53_client as route53:
                # 호스팅 영역 목록 조회
                response = await route53.list_hosted_zones()
                zones = response.get('HostedZones', [])

                if not zones:
                    self.log_info("호스팅 영역이 없습니다")
                    return 0

                # 레코드 정보 포함 여부
                include_records = getattr(self.args, 'include_records', False)

                zone_data = []
                for zone in zones:
                    zone_info = {
                        'name': zone['Name'],
                        'id': zone['Id'],
                        'comment': zone.get('Config', {}).get('Comment', ''),
                        'private': zone.get('Config', {}).get('PrivateZone', False),
                        'record_count': zone.get('ResourceRecordSetCount', 0)
                    }

                    if include_records:
                        try:
                            records_response = await route53.list_resource_record_sets(
                                HostedZoneId=zone['Id']
                            )
                            records = records_response.get('ResourceRecordSets', [])

                            # 레코드 타입별 개수 계산
                            record_types = {}
                            for record in records:
                                record_type = record['Type']
                                record_types[record_type] = record_types.get(record_type, 0) + 1

                            zone_info['record_types'] = record_types

                        except Exception as e:
                            self.log_warning(f"영역 {zone['Name']} 레코드 조회 실패: {e}")

                    zone_data.append(zone_info)

                # 출력
                formatted_output = self.format_output(zone_data)
                pawn.console.print(formatted_output)

                return 0

        except Exception as e:
            self.log_error(f"Route53 호스팅 영역 목록 조회 실패: {e}")
            return 1

    async def _route53_backup(self) -> int:
        """Route53 호스팅 영역 백업"""
        try:
            zone_id = self.args.zone_id
            backup_file = getattr(self.args, 'backup_file', None)

            route53_client = await self.get_aws_client('route53')

            if zone_id.lower() == 'all':
                return await self._backup_all_zones(route53_client)
            else:
                return await self._backup_single_zone(route53_client, zone_id, backup_file)

        except Exception as e:
            self.log_error(f"Route53 백업 실패: {e}")
            return 1

    async def _backup_single_zone(self, route53_client, zone_id: str, backup_file: Optional[str]) -> int:
        """단일 호스팅 영역 백업"""
        try:
            async with route53_client as route53:
                # 호스팅 영역 정보 조회
                zone_response = await route53.get_hosted_zone(Id=zone_id)
                zone = zone_response['HostedZone']

                # 레코드 세트 조회
                records_response = await route53.list_resource_record_sets(HostedZoneId=zone_id)
                records = records_response['ResourceRecordSets']

                # 백업 데이터 구성
                backup_data = {
                    'backup_timestamp': datetime.now().isoformat(),
                    'hosted_zone': zone,
                    'resource_record_sets': records
                }

                # 백업 파일명 생성
                if not backup_file:
                    zone_name = zone['Name'].rstrip('.')
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    backup_file = f"route53_backup_{zone_name}_{timestamp}.json"

                # 파일 저장
                await self._write_output_file(backup_file, backup_data)

                self.log_success(f"호스팅 영역 '{zone['Name']}'을 {backup_file}에 백업했습니다")
                self.log_info(f"레코드 수: {len(records)}")

                return 0

        except Exception as e:
            self.log_error(f"호스팅 영역 백업 실패: {e}")
            return 1

    async def _backup_all_zones(self, route53_client) -> int:
        """모든 호스팅 영역 백업"""
        try:
            async with route53_client as route53:
                # 모든 호스팅 영역 조회
                response = await route53.list_hosted_zones()
                zones = response.get('HostedZones', [])

                if not zones:
                    self.log_info("백업할 호스팅 영역이 없습니다")
                    return 0

                # 백업 디렉토리 생성
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_dir = Path(f"route53_backup_{timestamp}")
                backup_dir.mkdir(exist_ok=True)

                success_count = 0
                total_records = 0

                for zone in zones:
                    try:
                        zone_id = zone['Id']
                        zone_name = zone['Name'].rstrip('.')

                        # 레코드 세트 조회
                        records_response = await route53.list_resource_record_sets(HostedZoneId=zone_id)
                        records = records_response['ResourceRecordSets']

                        # 백업 데이터 구성
                        backup_data = {
                            'backup_timestamp': datetime.now().isoformat(),
                            'hosted_zone': zone,
                            'resource_record_sets': records
                        }

                        # 파일 저장
                        backup_file = backup_dir / f"{zone_name}.json"
                        await self._write_output_file(str(backup_file), backup_data)

                        success_count += 1
                        total_records += len(records)

                        self.log_info(f"✓ {zone_name} ({len(records)} 레코드)")

                    except Exception as e:
                        self.log_error(f"✗ {zone.get('Name', 'Unknown')} 백업 실패: {e}")

                self.log_success(f"전체 백업 완료: {success_count}/{len(zones)} 영역, {total_records} 레코드")
                self.log_info(f"백업 위치: {backup_dir.absolute()}")

                return 0 if success_count > 0 else 1

        except Exception as e:
            self.log_error(f"전체 백업 실패: {e}")
            return 1

    async def _route53_restore(self) -> int:
        """Route53 호스팅 영역 복원"""
        try:
            backup_file = self.args.backup_file
            new_zone_name = self.args.new_zone_name
            dry_run = getattr(self.args, 'dry_run', False)

            # 백업 파일 로드
            backup_data = await self._load_backup_file(backup_file)
            if not backup_data:
                return 1

            route53_client = await self.get_aws_client('route53')

            async with route53_client as route53:
                if dry_run:
                    return await self._preview_restore(backup_data, new_zone_name)
                else:
                    return await self._execute_restore(route53, backup_data, new_zone_name)

        except Exception as e:
            self.log_error(f"Route53 복원 실패: {e}")
            return 1

    async def _load_backup_file(self, backup_file: str) -> Optional[Dict[str, Any]]:
        """백업 파일 로드"""
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                self.log_error(f"백업 파일을 찾을 수 없습니다: {backup_file}")
                return None

            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)

            # 백업 파일 구조 검증
            required_keys = ['hosted_zone', 'resource_record_sets']
            for key in required_keys:
                if key not in backup_data:
                    self.log_error(f"유효하지 않은 백업 파일: {key} 키가 없습니다")
                    return None

            return backup_data

        except json.JSONDecodeError as e:
            self.log_error(f"백업 파일 JSON 파싱 오류: {e}")
            return None
        except Exception as e:
            self.log_error(f"백업 파일 로드 실패: {e}")
            return None

    async def _preview_restore(self, backup_data: Dict[str, Any], new_zone_name: str) -> int:
        """복원 미리보기"""
        try:
            hosted_zone = backup_data['hosted_zone']
            records = backup_data['resource_record_sets']

            pawn.console.log(f"[bold]복원 계획 미리보기[/bold]")
            pawn.console.log(f"원본 영역: {hosted_zone['Name']}")
            pawn.console.log(f"새 영역: {new_zone_name}")
            pawn.console.log(f"총 레코드 수: {len(records)}")
            pawn.console.log("")

            # 레코드 타입별 통계
            record_types = {}
            skipped_records = []

            for record in records:
                record_type = record['Type']
                record_types[record_type] = record_types.get(record_type, 0) + 1

                # SOA, NS 레코드는 건너뜀
                if record_type in ['SOA', 'NS']:
                    skipped_records.append(record)

            pawn.console.log("레코드 타입별 통계:")
            for record_type, count in sorted(record_types.items()):
                status = "(건너뜀)" if record_type in ['SOA', 'NS'] else ""
                pawn.console.log(f"  {record_type}: {count} {status}")

            pawn.console.log("")
            pawn.console.log(f"실제 복원될 레코드: {len(records) - len(skipped_records)}")
            pawn.console.log("실제 복원을 수행하려면 --dry-run 옵션을 제거하세요.")

            return 0

        except Exception as e:
            self.log_error(f"복원 미리보기 실패: {e}")
            return 1

    async def _execute_restore(self, route53, backup_data: Dict[str, Any], new_zone_name: str) -> int:
        """복원 실행"""
        try:
            hosted_zone = backup_data['hosted_zone']
            records = backup_data['resource_record_sets']

            # 새 호스팅 영역 생성
            caller_reference = f"{new_zone_name}-{datetime.now().isoformat()}"

            create_response = await route53.create_hosted_zone(
                Name=new_zone_name,
                CallerReference=caller_reference,
                HostedZoneConfig={
                    'Comment': hosted_zone.get('Config', {}).get('Comment', f'Restored from {hosted_zone["Name"]}'),
                    'PrivateZone': hosted_zone.get('Config', {}).get('PrivateZone', False)
                }
            )

            new_zone = create_response['HostedZone']
            new_zone_id = new_zone['Id']

            self.log_success(f"새 호스팅 영역 생성 완료: {new_zone_id}")

            # 레코드 복원
            restored_count = 0
            skipped_count = 0

            for record in records:
                try:
                    # SOA, NS 레코드는 건너뜀 (자동 생성됨)
                    if record['Type'] in ['SOA', 'NS']:
                        skipped_count += 1
                        continue

                    # 레코드 생성
                    await route53.change_resource_record_sets(
                        HostedZoneId=new_zone_id,
                        ChangeBatch={
                            'Changes': [{
                                'Action': 'CREATE',
                                'ResourceRecordSet': record
                            }]
                        }
                    )

                    restored_count += 1

                except Exception as e:
                    self.log_warning(f"레코드 복원 실패 ({record.get('Name', 'Unknown')} {record.get('Type', 'Unknown')}): {e}")

            self.log_success(f"복원 완료: {restored_count} 레코드 생성, {skipped_count} 레코드 건너뜀")
            self.log_info(f"새 호스팅 영역 ID: {new_zone_id}")

            return 0

        except Exception as e:
            self.log_error(f"복원 실행 실패: {e}")
            return 1

    async def _write_output_file(self, file_path: str, data: Any):
        """출력 파일 저장"""
        try:
            output_path = Path(file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=self._json_serializer, ensure_ascii=False)

        except Exception as e:
            self.log_error(f"파일 저장 실패: {e}")
            raise

    def _json_serializer(self, obj):
        """JSON 직렬화 헬퍼"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def main():
    """AWS CLI 메인 함수"""
    cli = AWSCLI()
    return cli.main()


if __name__ == "__main__":
    exit(main())
