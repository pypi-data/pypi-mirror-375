#!/usr/bin/env python3
"""
S3 CLI 명령어

AWS S3 버킷 및 객체 관리 기능을 제공합니다.
"""

import os
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from argparse import ArgumentParser
from datetime import datetime

from pawnstack.cli.base import CloudBaseCLI, register_cli_command
from pawnstack.config.global_config import pawn


@register_cli_command(
    name="s3",
    description="AWS S3 버킷 및 객체 관리",
    epilog="""
사용 예제:
  1. 로컬 디렉토리를 S3에 동기화:
     pawns s3 sync ./data s3://my-bucket/data/

  2. S3에서 로컬로 동기화:
     pawns s3 sync s3://my-bucket/data/ ./data

  3. 파일 복사:
     pawns s3 cp ./file.txt s3://my-bucket/path/file.txt
     pawns s3 cp s3://my-bucket/path/file.txt ./file.txt

  4. S3 버킷 목록:
     pawns s3 ls

  5. S3 객체 목록:
     pawns s3 ls s3://my-bucket/path/

  6. S3 객체 삭제:
     pawns s3 rm s3://my-bucket/path/file.txt
     pawns s3 rm s3://my-bucket/path/ --recursive

  7. 버킷 정보 조회:
     pawns s3 info s3://my-bucket
"""
)
class S3CLI(CloudBaseCLI):
    """S3 CLI 명령어 클래스"""

    def __init__(self, args=None):
        super().__init__(args)
        self._s3_client = None
        self._s3_resource = None

    def get_arguments(self, parser: ArgumentParser):
        """S3 CLI 인수 정의"""
        # 공통 클라우드 인수 추가
        self.get_common_cloud_arguments(parser)

        # S3 특화 공통 인수
        parser.add_argument(
            '--max-workers',
            type=int,
            default=10,
            help='최대 동시 작업 수 (default: 10)'
        )

        parser.add_argument(
            '--chunk-size',
            type=int,
            default=8388608,  # 8MB
            help='업로드/다운로드 청크 크기 (바이트, default: 8MB)'
        )

        parser.add_argument(
            '--storage-class',
            choices=['STANDARD', 'REDUCED_REDUNDANCY', 'STANDARD_IA', 'ONEZONE_IA', 'INTELLIGENT_TIERING', 'GLACIER', 'DEEP_ARCHIVE'],
            default='STANDARD',
            help='S3 스토리지 클래스 (default: STANDARD)'
        )

        # 서브커맨드 정의
        subparsers = parser.add_subparsers(dest='subcommand', help='S3 서브커맨드')

        # sync 서브커맨드
        sync_parser = subparsers.add_parser('sync', help='디렉토리 동기화')
        sync_parser.add_argument('source', help='소스 경로 (로컬 또는 S3)')
        sync_parser.add_argument('destination', help='대상 경로 (로컬 또는 S3)')
        sync_parser.add_argument('--delete', action='store_true', help='소스에 없는 파일 삭제')
        sync_parser.add_argument('--dry-run', action='store_true', help='실제 실행하지 않고 계획만 표시')
        sync_parser.add_argument('--exclude', action='append', help='제외할 패턴')
        sync_parser.add_argument('--include', action='append', help='포함할 패턴')

        # cp 서브커맨드
        cp_parser = subparsers.add_parser('cp', help='파일/디렉토리 복사')
        cp_parser.add_argument('source', help='소스 경로 (로컬 또는 S3)')
        cp_parser.add_argument('destination', help='대상 경로 (로컬 또는 S3)')
        cp_parser.add_argument('--recursive', '-r', action='store_true', help='재귀적 복사')
        cp_parser.add_argument('--dry-run', action='store_true', help='실제 실행하지 않고 계획만 표시')
        cp_parser.add_argument('--metadata', action='append', help='메타데이터 (key=value 형식)')

        # ls 서브커맨드
        ls_parser = subparsers.add_parser('ls', help='버킷/객체 목록')
        ls_parser.add_argument('path', nargs='?', help='S3 경로 (생략시 버킷 목록)')
        ls_parser.add_argument('--recursive', '-r', action='store_true', help='재귀적 목록')
        ls_parser.add_argument('--human-readable', action='store_true', help='사람이 읽기 쉬운 크기 표시')
        ls_parser.add_argument('--summarize', action='store_true', help='요약 정보 표시')

        # rm 서브커맨드
        rm_parser = subparsers.add_parser('rm', help='객체 삭제')
        rm_parser.add_argument('path', help='S3 경로')
        rm_parser.add_argument('--recursive', '-r', action='store_true', help='재귀적 삭제')
        rm_parser.add_argument('--dry-run', action='store_true', help='실제 실행하지 않고 계획만 표시')
        rm_parser.add_argument('--include', action='append', help='포함할 패턴')
        rm_parser.add_argument('--exclude', action='append', help='제외할 패턴')

        # info 서브커맨드
        info_parser = subparsers.add_parser('info', help='버킷/객체 정보')
        info_parser.add_argument('path', help='S3 경로')
        info_parser.add_argument('--include-metadata', action='store_true', help='메타데이터 포함')
        info_parser.add_argument('--include-acl', action='store_true', help='ACL 정보 포함')

    async def run_async(self) -> int:
        """S3 CLI 비동기 실행"""
        try:
            # 서브커맨드에 따른 실행
            if not hasattr(self.args, 'subcommand') or not self.args.subcommand:
                return await self._show_help()

            # AWS 자격 증명 검증
            if not await self.validate_aws_credentials():
                return 1

            if self.args.subcommand == 'sync':
                return await self._handle_sync()
            elif self.args.subcommand == 'cp':
                return await self._handle_copy()
            elif self.args.subcommand == 'ls':
                return await self._handle_list()
            elif self.args.subcommand == 'rm':
                return await self._handle_remove()
            elif self.args.subcommand == 'info':
                return await self._handle_info()
            else:
                self.log_error(f"알 수 없는 서브커맨드: {self.args.subcommand}")
                return 1

        except Exception as e:
            self.log_error(f"S3 CLI 실행 중 오류 발생: {e}")
            if pawn.get('PAWN_DEBUG'):
                pawn.console.print_exception(show_locals=True)
            return 1
        finally:
            await self._cleanup_clients()

    async def _show_help(self) -> int:
        """도움말 표시"""
        pawn.console.log("S3 CLI 사용법:")
        pawn.console.log("  pawns s3 ls                    # 버킷 목록")
        pawn.console.log("  pawns s3 ls s3://bucket/       # 객체 목록")
        pawn.console.log("  pawns s3 cp file.txt s3://bucket/  # 파일 업로드")
        pawn.console.log("  pawns s3 sync ./dir s3://bucket/   # 디렉토리 동기화")
        pawn.console.log("")
        pawn.console.log("자세한 사용법은 --help 옵션을 사용하세요.")
        return 0

    async def _get_s3_client(self):
        """S3 클라이언트 반환"""
        if self._s3_client is None:
            self._s3_client = await self.get_aws_client('s3')
        return self._s3_client

    async def _get_s3_resource(self):
        """S3 리소스 반환"""
        if self._s3_resource is None:
            session = await self.get_aws_session()
            boto3_config = self.get_boto3_config()
            self._s3_resource = session.resource('s3', **boto3_config)
        return self._s3_resource

    async def _cleanup_clients(self):
        """클라이언트 정리"""
        if self._s3_resource:
            try:
                await self._s3_resource.close()
            except Exception:
                pass
            self._s3_resource = None

        await self.close_aws_clients()

    def _parse_s3_path(self, path: str) -> tuple[Optional[str], Optional[str]]:
        """S3 경로 파싱"""
        if path.startswith('s3://'):
            path_parts = path[5:].split('/', 1)
            bucket = path_parts[0]
            key = path_parts[1] if len(path_parts) > 1 else ''
            return bucket, key
        return None, path

    def _is_s3_path(self, path: str) -> bool:
        """S3 경로 여부 확인"""
        return path.startswith('s3://')

    def _format_size(self, size_bytes: int) -> str:
        """파일 크기 포맷팅"""
        if not getattr(self.args, 'human_readable', False):
            return str(size_bytes)

        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    async def _handle_sync(self) -> int:
        """동기화 처리"""
        try:
            source = self.args.source
            destination = self.args.destination

            source_is_s3 = self._is_s3_path(source)
            dest_is_s3 = self._is_s3_path(destination)

            if source_is_s3 and dest_is_s3:
                self.log_error("S3 간 동기화는 현재 지원되지 않습니다")
                return 1
            elif not source_is_s3 and not dest_is_s3:
                self.log_error("로컬 간 동기화는 지원되지 않습니다. rsync를 사용하세요")
                return 1
            elif source_is_s3:
                return await self._sync_from_s3(source, destination)
            else:
                return await self._sync_to_s3(source, destination)

        except Exception as e:
            self.log_error(f"동기화 실패: {e}")
            return 1

    async def _sync_to_s3(self, local_path: str, s3_path: str) -> int:
        """로컬에서 S3로 동기화"""
        try:
            bucket, prefix = self._parse_s3_path(s3_path)
            if not bucket:
                self.log_error("유효하지 않은 S3 경로입니다")
                return 1

            local_dir = Path(local_path)
            if not local_dir.exists():
                self.log_error(f"로컬 경로를 찾을 수 없습니다: {local_path}")
                return 1

            s3_client = await self._get_s3_client()

            # 로컬 파일 목록
            local_files = []
            if local_dir.is_file():
                local_files = [local_dir]
            else:
                local_files = list(local_dir.rglob('*'))
                local_files = [f for f in local_files if f.is_file()]

            # 필터링 적용
            local_files = self._apply_filters(local_files, local_dir)

            # S3 객체 목록 (비교용)
            s3_objects = {}
            if not getattr(self.args, 'dry_run', False):
                try:
                    async with s3_client as s3:
                        paginator = s3.get_paginator('list_objects_v2')
                        async for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                            for obj in page.get('Contents', []):
                                s3_objects[obj['Key']] = obj
                except Exception:
                    # 버킷이 비어있거나 접근 권한이 없는 경우
                    pass

            # 업로드할 파일 결정
            upload_tasks = []
            total_size = 0

            for local_file in local_files:
                relative_path = local_file.relative_to(local_dir)
                s3_key = f"{prefix.rstrip('/')}/{relative_path}".lstrip('/')

                # 파일 크기 및 수정 시간 확인
                file_stat = local_file.stat()
                file_size = file_stat.st_size
                file_mtime = datetime.fromtimestamp(file_stat.st_mtime)

                should_upload = True

                # S3에 이미 존재하는지 확인
                if s3_key in s3_objects:
                    s3_obj = s3_objects[s3_key]
                    s3_size = s3_obj['Size']
                    s3_mtime = s3_obj['LastModified'].replace(tzinfo=None)

                    # 크기와 수정 시간이 같으면 건너뜀
                    if file_size == s3_size and file_mtime <= s3_mtime:
                        should_upload = False

                if should_upload:
                    upload_tasks.append((local_file, s3_key, file_size))
                    total_size += file_size

            if not upload_tasks:
                self.log_info("업로드할 파일이 없습니다 (모든 파일이 최신 상태)")
                return 0

            # Dry run 모드
            if getattr(self.args, 'dry_run', False):
                self.log_info(f"업로드 예정: {len(upload_tasks)} 파일 ({self._format_size(total_size)})")
                for local_file, s3_key, file_size in upload_tasks:
                    pawn.console.log(f"  {local_file} -> s3://{bucket}/{s3_key} ({self._format_size(file_size)})")
                return 0

            # 실제 업로드 수행
            self.log_info(f"업로드 시작: {len(upload_tasks)} 파일 ({self._format_size(total_size)})")

            uploaded_count = 0
            uploaded_size = 0

            # 병렬 업로드
            semaphore = asyncio.Semaphore(getattr(self.args, 'max_workers', 10))

            async def upload_file(local_file, s3_key, file_size):
                nonlocal uploaded_count, uploaded_size

                async with semaphore:
                    try:
                        async with s3_client as s3:
                            # 메타데이터 설정
                            extra_args = {
                                'StorageClass': getattr(self.args, 'storage_class', 'STANDARD')
                            }

                            # 파일 업로드
                            await s3.upload_file(
                                str(local_file),
                                bucket,
                                s3_key,
                                ExtraArgs=extra_args
                            )

                            uploaded_count += 1
                            uploaded_size += file_size

                            self.log_info(f"✓ {local_file.name} ({self._format_size(file_size)})")

                    except Exception as e:
                        self.log_error(f"✗ {local_file.name}: {e}")

            # 업로드 작업 실행
            tasks = [upload_file(local_file, s3_key, file_size) for local_file, s3_key, file_size in upload_tasks]
            await asyncio.gather(*tasks, return_exceptions=True)

            # 삭제 처리 (--delete 옵션)
            if getattr(self.args, 'delete', False):
                await self._delete_extra_s3_objects(s3_client, bucket, prefix, local_files, local_dir)

            self.log_success(f"동기화 완료: {uploaded_count}/{len(upload_tasks)} 파일 업로드 ({self._format_size(uploaded_size)})")
            return 0

        except Exception as e:
            self.log_error(f"S3 업로드 동기화 실패: {e}")
            return 1

    async def _sync_from_s3(self, s3_path: str, local_path: str) -> int:
        """S3에서 로컬로 동기화"""
        try:
            bucket, prefix = self._parse_s3_path(s3_path)
            if not bucket:
                self.log_error("유효하지 않은 S3 경로입니다")
                return 1

            local_dir = Path(local_path)
            local_dir.mkdir(parents=True, exist_ok=True)

            s3_client = await self._get_s3_client()

            # S3 객체 목록
            s3_objects = []
            async with s3_client as s3:
                paginator = s3.get_paginator('list_objects_v2')
                async for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                    for obj in page.get('Contents', []):
                        if not obj['Key'].endswith('/'):  # 디렉토리 제외
                            s3_objects.append(obj)

            if not s3_objects:
                self.log_info("다운로드할 객체가 없습니다")
                return 0

            # 다운로드할 파일 결정
            download_tasks = []
            total_size = 0

            for s3_obj in s3_objects:
                s3_key = s3_obj['Key']

                # 로컬 파일 경로 계산
                if prefix:
                    relative_key = s3_key[len(prefix):].lstrip('/')
                else:
                    relative_key = s3_key

                local_file = local_dir / relative_key

                should_download = True

                # 로컬 파일이 이미 존재하는지 확인
                if local_file.exists():
                    local_stat = local_file.stat()
                    local_size = local_stat.st_size
                    local_mtime = datetime.fromtimestamp(local_stat.st_mtime)

                    s3_size = s3_obj['Size']
                    s3_mtime = s3_obj['LastModified'].replace(tzinfo=None)

                    # 크기와 수정 시간이 같으면 건너뜀
                    if local_size == s3_size and local_mtime >= s3_mtime:
                        should_download = False

                if should_download:
                    download_tasks.append((s3_key, local_file, s3_obj['Size']))
                    total_size += s3_obj['Size']

            if not download_tasks:
                self.log_info("다운로드할 파일이 없습니다 (모든 파일이 최신 상태)")
                return 0

            # Dry run 모드
            if getattr(self.args, 'dry_run', False):
                self.log_info(f"다운로드 예정: {len(download_tasks)} 파일 ({self._format_size(total_size)})")
                for s3_key, local_file, file_size in download_tasks:
                    pawn.console.log(f"  s3://{bucket}/{s3_key} -> {local_file} ({self._format_size(file_size)})")
                return 0

            # 실제 다운로드 수행
            self.log_info(f"다운로드 시작: {len(download_tasks)} 파일 ({self._format_size(total_size)})")

            downloaded_count = 0
            downloaded_size = 0

            # 병렬 다운로드
            semaphore = asyncio.Semaphore(getattr(self.args, 'max_workers', 10))

            async def download_file(s3_key, local_file, file_size):
                nonlocal downloaded_count, downloaded_size

                async with semaphore:
                    try:
                        # 디렉토리 생성
                        local_file.parent.mkdir(parents=True, exist_ok=True)

                        async with s3_client as s3:
                            await s3.download_file(bucket, s3_key, str(local_file))

                            downloaded_count += 1
                            downloaded_size += file_size

                            self.log_info(f"✓ {local_file.name} ({self._format_size(file_size)})")

                    except Exception as e:
                        self.log_error(f"✗ {s3_key}: {e}")

            # 다운로드 작업 실행
            tasks = [download_file(s3_key, local_file, file_size) for s3_key, local_file, file_size in download_tasks]
            await asyncio.gather(*tasks, return_exceptions=True)

            self.log_success(f"동기화 완료: {downloaded_count}/{len(download_tasks)} 파일 다운로드 ({self._format_size(downloaded_size)})")
            return 0

        except Exception as e:
            self.log_error(f"S3 다운로드 동기화 실패: {e}")
            return 1

    def _apply_filters(self, files: List[Path], base_dir: Path) -> List[Path]:
        """파일 필터링 적용"""
        import fnmatch

        include_patterns = getattr(self.args, 'include', [])
        exclude_patterns = getattr(self.args, 'exclude', [])

        if not include_patterns and not exclude_patterns:
            return files

        filtered_files = []

        for file_path in files:
            relative_path = str(file_path.relative_to(base_dir))

            # Include 패턴 확인 (지정된 경우)
            if include_patterns:
                included = any(fnmatch.fnmatch(relative_path, pattern) for pattern in include_patterns)
                if not included:
                    continue

            # Exclude 패턴 확인
            if exclude_patterns:
                excluded = any(fnmatch.fnmatch(relative_path, pattern) for pattern in exclude_patterns)
                if excluded:
                    continue

            filtered_files.append(file_path)

        return filtered_files

    async def _delete_extra_s3_objects(self, s3_client, bucket: str, prefix: str, local_files: List[Path], local_dir: Path):
        """로컬에 없는 S3 객체 삭제"""
        try:
            # 로컬 파일 경로 집합 생성
            local_keys = set()
            for local_file in local_files:
                relative_path = local_file.relative_to(local_dir)
                s3_key = f"{prefix.rstrip('/')}/{relative_path}".lstrip('/')
                local_keys.add(s3_key)

            # S3 객체 목록 조회
            delete_keys = []
            async with s3_client as s3:
                paginator = s3.get_paginator('list_objects_v2')
                async for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                    for obj in page.get('Contents', []):
                        s3_key = obj['Key']
                        if s3_key not in local_keys:
                            delete_keys.append(s3_key)

            if delete_keys:
                self.log_info(f"삭제할 객체: {len(delete_keys)}개")

                # 배치 삭제
                for i in range(0, len(delete_keys), 1000):  # S3 배치 삭제 제한
                    batch_keys = delete_keys[i:i+1000]
                    delete_objects = [{'Key': key} for key in batch_keys]

                    async with s3_client as s3:
                        await s3.delete_objects(
                            Bucket=bucket,
                            Delete={'Objects': delete_objects}
                        )

                    for key in batch_keys:
                        self.log_info(f"✗ 삭제: {key}")

                self.log_success(f"{len(delete_keys)}개 객체 삭제 완료")

        except Exception as e:
            self.log_error(f"S3 객체 삭제 실패: {e}")

    async def _handle_copy(self) -> int:
        """복사 처리"""
        try:
            source = self.args.source
            destination = self.args.destination

            source_is_s3 = self._is_s3_path(source)
            dest_is_s3 = self._is_s3_path(destination)

            if source_is_s3 and dest_is_s3:
                return await self._copy_s3_to_s3(source, destination)
            elif source_is_s3:
                return await self._copy_s3_to_local(source, destination)
            elif dest_is_s3:
                return await self._copy_local_to_s3(source, destination)
            else:
                self.log_error("로컬 간 복사는 지원되지 않습니다")
                return 1

        except Exception as e:
            self.log_error(f"복사 실패: {e}")
            return 1

    async def _copy_local_to_s3(self, local_path: str, s3_path: str) -> int:
        """로컬에서 S3로 복사"""
        try:
            bucket, key = self._parse_s3_path(s3_path)
            if not bucket:
                self.log_error("유효하지 않은 S3 경로입니다")
                return 1

            local_file = Path(local_path)
            if not local_file.exists():
                self.log_error(f"로컬 파일을 찾을 수 없습니다: {local_path}")
                return 1

            s3_client = await self._get_s3_client()

            if local_file.is_file():
                # 단일 파일 복사
                if getattr(self.args, 'dry_run', False):
                    self.log_info(f"복사 예정: {local_file} -> s3://{bucket}/{key}")
                    return 0

                async with s3_client as s3:
                    extra_args = {'StorageClass': getattr(self.args, 'storage_class', 'STANDARD')}

                    # 메타데이터 추가
                    if hasattr(self.args, 'metadata') and self.args.metadata:
                        metadata = {}
                        for meta in self.args.metadata:
                            if '=' in meta:
                                k, v = meta.split('=', 1)
                                metadata[k] = v
                        if metadata:
                            extra_args['Metadata'] = metadata

                    await s3.upload_file(str(local_file), bucket, key, ExtraArgs=extra_args)

                file_size = local_file.stat().st_size
                self.log_success(f"파일 업로드 완료: {local_file} -> s3://{bucket}/{key} ({self._format_size(file_size)})")

            elif local_file.is_dir() and getattr(self.args, 'recursive', False):
                # 디렉토리 복사
                files = list(local_file.rglob('*'))
                files = [f for f in files if f.is_file()]

                if getattr(self.args, 'dry_run', False):
                    self.log_info(f"복사 예정: {len(files)} 파일")
                    return 0

                uploaded_count = 0
                total_size = 0

                for file_path in files:
                    try:
                        relative_path = file_path.relative_to(local_file)
                        s3_key = f"{key.rstrip('/')}/{relative_path}".lstrip('/')

                        async with s3_client as s3:
                            await s3.upload_file(str(file_path), bucket, s3_key)

                        file_size = file_path.stat().st_size
                        total_size += file_size
                        uploaded_count += 1

                        self.log_info(f"✓ {file_path.name} ({self._format_size(file_size)})")

                    except Exception as e:
                        self.log_error(f"✗ {file_path.name}: {e}")

                self.log_success(f"디렉토리 업로드 완료: {uploaded_count} 파일 ({self._format_size(total_size)})")

            else:
                self.log_error("디렉토리 복사는 --recursive 옵션이 필요합니다")
                return 1

            return 0

        except Exception as e:
            self.log_error(f"로컬에서 S3로 복사 실패: {e}")
            return 1

    async def _copy_s3_to_local(self, s3_path: str, local_path: str) -> int:
        """S3에서 로컬로 복사"""
        try:
            bucket, key = self._parse_s3_path(s3_path)
            if not bucket:
                self.log_error("유효하지 않은 S3 경로입니다")
                return 1

            s3_client = await self._get_s3_client()

            # S3 객체 존재 확인
            try:
                async with s3_client as s3:
                    await s3.head_object(Bucket=bucket, Key=key)
                    is_single_object = True
            except Exception:
                is_single_object = False

            if is_single_object:
                # 단일 객체 다운로드
                local_file = Path(local_path)

                if getattr(self.args, 'dry_run', False):
                    self.log_info(f"다운로드 예정: s3://{bucket}/{key} -> {local_file}")
                    return 0

                local_file.parent.mkdir(parents=True, exist_ok=True)

                async with s3_client as s3:
                    await s3.download_file(bucket, key, str(local_file))

                file_size = local_file.stat().st_size
                self.log_success(f"파일 다운로드 완료: s3://{bucket}/{key} -> {local_file} ({self._format_size(file_size)})")

            else:
                # 다중 객체 다운로드 (prefix 기반)
                if not getattr(self.args, 'recursive', False):
                    self.log_error("다중 객체 다운로드는 --recursive 옵션이 필요합니다")
                    return 1

                local_dir = Path(local_path)
                local_dir.mkdir(parents=True, exist_ok=True)

                # S3 객체 목록 조회
                objects = []
                async with s3_client as s3:
                    paginator = s3.get_paginator('list_objects_v2')
                    async for page in paginator.paginate(Bucket=bucket, Prefix=key):
                        for obj in page.get('Contents', []):
                            if not obj['Key'].endswith('/'):
                                objects.append(obj)

                if not objects:
                    self.log_error(f"S3 경로에서 객체를 찾을 수 없습니다: s3://{bucket}/{key}")
                    return 1

                if getattr(self.args, 'dry_run', False):
                    self.log_info(f"다운로드 예정: {len(objects)} 객체")
                    return 0

                downloaded_count = 0
                total_size = 0

                for obj in objects:
                    try:
                        obj_key = obj['Key']
                        relative_key = obj_key[len(key):].lstrip('/')
                        local_file = local_dir / relative_key

                        local_file.parent.mkdir(parents=True, exist_ok=True)

                        async with s3_client as s3:
                            await s3.download_file(bucket, obj_key, str(local_file))

                        file_size = obj['Size']
                        total_size += file_size
                        downloaded_count += 1

                        self.log_info(f"✓ {local_file.name} ({self._format_size(file_size)})")

                    except Exception as e:
                        self.log_error(f"✗ {obj_key}: {e}")

                self.log_success(f"다운로드 완료: {downloaded_count} 파일 ({self._format_size(total_size)})")

            return 0

        except Exception as e:
            self.log_error(f"S3에서 로컬로 복사 실패: {e}")
            return 1

    async def _copy_s3_to_s3(self, source_s3: str, dest_s3: str) -> int:
        """S3 간 복사"""
        try:
            source_bucket, source_key = self._parse_s3_path(source_s3)
            dest_bucket, dest_key = self._parse_s3_path(dest_s3)

            if not source_bucket or not dest_bucket:
                self.log_error("유효하지 않은 S3 경로입니다")
                return 1

            s3_client = await self._get_s3_client()

            if getattr(self.args, 'dry_run', False):
                self.log_info(f"복사 예정: {source_s3} -> {dest_s3}")
                return 0

            async with s3_client as s3:
                copy_source = {'Bucket': source_bucket, 'Key': source_key}
                await s3.copy_object(CopySource=copy_source, Bucket=dest_bucket, Key=dest_key)

            self.log_success(f"S3 객체 복사 완료: {source_s3} -> {dest_s3}")
            return 0

        except Exception as e:
            self.log_error(f"S3 간 복사 실패: {e}")
            return 1

    async def _handle_list(self) -> int:
        """목록 조회 처리"""
        try:
            path = getattr(self.args, 'path', None)

            if not path:
                # 버킷 목록
                return await self._list_buckets()
            else:
                # 객체 목록
                bucket, prefix = self._parse_s3_path(path)
                if not bucket:
                    self.log_error("유효하지 않은 S3 경로입니다")
                    return 1
                return await self._list_objects(bucket, prefix)

        except Exception as e:
            self.log_error(f"목록 조회 실패: {e}")
            return 1

    async def _list_buckets(self) -> int:
        """버킷 목록 조회"""
        try:
            s3_client = await self._get_s3_client()

            async with s3_client as s3:
                response = await s3.list_buckets()
                buckets = response.get('Buckets', [])

            if not buckets:
                self.log_info("버킷이 없습니다")
                return 0

            # 버킷 정보 수집
            bucket_data = []
            for bucket in buckets:
                bucket_info = {
                    'name': bucket['Name'],
                    'creation_date': bucket['CreationDate'].strftime('%Y-%m-%d %H:%M:%S')
                }

                # 요약 정보 포함
                if getattr(self.args, 'summarize', False):
                    try:
                        async with s3_client as s3:
                            # 객체 수 및 크기 계산
                            paginator = s3.get_paginator('list_objects_v2')
                            object_count = 0
                            total_size = 0

                            async for page in paginator.paginate(Bucket=bucket['Name']):
                                objects = page.get('Contents', [])
                                object_count += len(objects)
                                total_size += sum(obj['Size'] for obj in objects)

                            bucket_info['object_count'] = object_count
                            bucket_info['total_size'] = self._format_size(total_size)

                    except Exception as e:
                        bucket_info['error'] = str(e)

                bucket_data.append(bucket_info)

            # 출력
            formatted_output = self.format_output(bucket_data)
            pawn.console.print(formatted_output)

            return 0

        except Exception as e:
            self.log_error(f"버킷 목록 조회 실패: {e}")
            return 1

    async def _list_objects(self, bucket: str, prefix: str = '') -> int:
        """객체 목록 조회"""
        try:
            s3_client = await self._get_s3_client()

            objects = []
            total_size = 0

            async with s3_client as s3:
                if getattr(self.args, 'recursive', False):
                    # 재귀적 목록
                    paginator = s3.get_paginator('list_objects_v2')
                    async for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                        for obj in page.get('Contents', []):
                            objects.append(obj)
                            total_size += obj['Size']
                else:
                    # 현재 레벨만
                    paginator = s3.get_paginator('list_objects_v2')
                    async for page in paginator.paginate(Bucket=bucket, Prefix=prefix, Delimiter='/'):
                        # 디렉토리
                        for common_prefix in page.get('CommonPrefixes', []):
                            objects.append({
                                'Key': common_prefix['Prefix'],
                                'Size': 0,
                                'LastModified': None,
                                'IsDirectory': True
                            })

                        # 파일
                        for obj in page.get('Contents', []):
                            if obj['Key'] != prefix:  # prefix 자체는 제외
                                objects.append(obj)
                                total_size += obj['Size']

            if not objects:
                self.log_info("객체가 없습니다")
                return 0

            # 객체 정보 포맷팅
            object_data = []
            for obj in objects:
                is_dir = obj.get('IsDirectory', False)

                obj_info = {
                    'key': obj['Key'],
                    'size': self._format_size(obj['Size']) if not is_dir else '<DIR>',
                    'last_modified': obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S') if obj['LastModified'] else '',
                    'type': 'Directory' if is_dir else 'File'
                }

                object_data.append(obj_info)

            # 출력
            formatted_output = self.format_output(object_data)
            pawn.console.print(formatted_output)

            # 요약 정보
            if getattr(self.args, 'summarize', False):
                file_count = len([obj for obj in objects if not obj.get('IsDirectory', False)])
                dir_count = len([obj for obj in objects if obj.get('IsDirectory', False)])

                pawn.console.log("")
                pawn.console.log(f"총 {file_count} 파일, {dir_count} 디렉토리")
                pawn.console.log(f"총 크기: {self._format_size(total_size)}")

            return 0

        except Exception as e:
            self.log_error(f"객체 목록 조회 실패: {e}")
            return 1

    async def _handle_remove(self) -> int:
        """삭제 처리"""
        try:
            path = self.args.path
            bucket, prefix = self._parse_s3_path(path)

            if not bucket:
                self.log_error("유효하지 않은 S3 경로입니다")
                return 1

            s3_client = await self._get_s3_client()

            # 삭제할 객체 목록 수집
            delete_objects = []

            if getattr(self.args, 'recursive', False):
                # 재귀적 삭제
                async with s3_client as s3:
                    paginator = s3.get_paginator('list_objects_v2')
                    async for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                        for obj in page.get('Contents', []):
                            delete_objects.append(obj['Key'])
            else:
                # 단일 객체 삭제
                try:
                    async with s3_client as s3:
                        await s3.head_object(Bucket=bucket, Key=prefix)
                        delete_objects.append(prefix)
                except Exception:
                    self.log_error(f"객체를 찾을 수 없습니다: s3://{bucket}/{prefix}")
                    return 1

            # 필터링 적용
            if hasattr(self.args, 'include') or hasattr(self.args, 'exclude'):
                import fnmatch

                include_patterns = getattr(self.args, 'include', [])
                exclude_patterns = getattr(self.args, 'exclude', [])

                filtered_objects = []
                for obj_key in delete_objects:
                    # Include 패턴 확인
                    if include_patterns:
                        included = any(fnmatch.fnmatch(obj_key, pattern) for pattern in include_patterns)
                        if not included:
                            continue

                    # Exclude 패턴 확인
                    if exclude_patterns:
                        excluded = any(fnmatch.fnmatch(obj_key, pattern) for pattern in exclude_patterns)
                        if excluded:
                            continue

                    filtered_objects.append(obj_key)

                delete_objects = filtered_objects

            if not delete_objects:
                self.log_info("삭제할 객체가 없습니다")
                return 0

            # Dry run 모드
            if getattr(self.args, 'dry_run', False):
                self.log_info(f"삭제 예정: {len(delete_objects)} 객체")
                for obj_key in delete_objects:
                    pawn.console.log(f"  s3://{bucket}/{obj_key}")
                return 0

            # 실제 삭제 수행
            self.log_info(f"삭제 시작: {len(delete_objects)} 객체")

            deleted_count = 0

            # 배치 삭제 (최대 1000개씩)
            for i in range(0, len(delete_objects), 1000):
                batch_objects = delete_objects[i:i+1000]
                delete_request = [{'Key': key} for key in batch_objects]

                try:
                    async with s3_client as s3:
                        response = await s3.delete_objects(
                            Bucket=bucket,
                            Delete={'Objects': delete_request}
                        )

                    # 삭제 결과 처리
                    deleted = response.get('Deleted', [])
                    errors = response.get('Errors', [])

                    for obj in deleted:
                        deleted_count += 1
                        self.log_info(f"✓ 삭제: {obj['Key']}")

                    for error in errors:
                        self.log_error(f"✗ 삭제 실패: {error['Key']} - {error['Message']}")

                except Exception as e:
                    self.log_error(f"배치 삭제 실패: {e}")

            self.log_success(f"삭제 완료: {deleted_count}/{len(delete_objects)} 객체")
            return 0

        except Exception as e:
            self.log_error(f"객체 삭제 실패: {e}")
            return 1

    async def _handle_info(self) -> int:
        """정보 조회 처리"""
        try:
            path = self.args.path
            bucket, key = self._parse_s3_path(path)

            if not bucket:
                self.log_error("유효하지 않은 S3 경로입니다")
                return 1

            s3_client = await self._get_s3_client()

            if not key:
                # 버킷 정보
                return await self._get_bucket_info(s3_client, bucket)
            else:
                # 객체 정보
                return await self._get_object_info(s3_client, bucket, key)

        except Exception as e:
            self.log_error(f"정보 조회 실패: {e}")
            return 1

    async def _get_bucket_info(self, s3_client, bucket: str) -> int:
        """버킷 정보 조회"""
        try:
            async with s3_client as s3:
                # 기본 버킷 정보
                bucket_info = {
                    'name': bucket,
                    'region': await self._get_bucket_region(s3, bucket)
                }

                # 버킷 생성 날짜
                try:
                    buckets_response = await s3.list_buckets()
                    for b in buckets_response.get('Buckets', []):
                        if b['Name'] == bucket:
                            bucket_info['creation_date'] = b['CreationDate'].strftime('%Y-%m-%d %H:%M:%S')
                            break
                except Exception:
                    pass

                # 객체 통계
                try:
                    paginator = s3.get_paginator('list_objects_v2')
                    object_count = 0
                    total_size = 0

                    async for page in paginator.paginate(Bucket=bucket):
                        objects = page.get('Contents', [])
                        object_count += len(objects)
                        total_size += sum(obj['Size'] for obj in objects)

                    bucket_info['object_count'] = object_count
                    bucket_info['total_size'] = self._format_size(total_size)

                except Exception as e:
                    bucket_info['statistics_error'] = str(e)

                # 버킷 정책 (선택적)
                if getattr(self.args, 'include_acl', False):
                    try:
                        acl_response = await s3.get_bucket_acl(Bucket=bucket)
                        bucket_info['acl'] = {
                            'owner': acl_response['Owner'],
                            'grants': acl_response['Grants']
                        }
                    except Exception as e:
                        bucket_info['acl_error'] = str(e)

            # 출력
            formatted_output = self.format_output(bucket_info)
            pawn.console.print(formatted_output)

            return 0

        except Exception as e:
            self.log_error(f"버킷 정보 조회 실패: {e}")
            return 1

    async def _get_object_info(self, s3_client, bucket: str, key: str) -> int:
        """객체 정보 조회"""
        try:
            async with s3_client as s3:
                # 객체 메타데이터
                response = await s3.head_object(Bucket=bucket, Key=key)

                object_info = {
                    'bucket': bucket,
                    'key': key,
                    'size': self._format_size(response['ContentLength']),
                    'last_modified': response['LastModified'].strftime('%Y-%m-%d %H:%M:%S'),
                    'etag': response['ETag'].strip('"'),
                    'content_type': response.get('ContentType', 'unknown'),
                    'storage_class': response.get('StorageClass', 'STANDARD')
                }

                # 메타데이터 포함
                if getattr(self.args, 'include_metadata', False):
                    metadata = response.get('Metadata', {})
                    if metadata:
                        object_info['metadata'] = metadata

                # ACL 정보 포함
                if getattr(self.args, 'include_acl', False):
                    try:
                        acl_response = await s3.get_object_acl(Bucket=bucket, Key=key)
                        object_info['acl'] = {
                            'owner': acl_response['Owner'],
                            'grants': acl_response['Grants']
                        }
                    except Exception as e:
                        object_info['acl_error'] = str(e)

            # 출력
            formatted_output = self.format_output(object_info)
            pawn.console.print(formatted_output)

            return 0

        except Exception as e:
            if 'NoSuchKey' in str(e):
                self.log_error(f"객체를 찾을 수 없습니다: s3://{bucket}/{key}")
            else:
                self.log_error(f"객체 정보 조회 실패: {e}")
            return 1

    async def _get_bucket_region(self, s3_client, bucket: str) -> str:
        """버킷 리전 조회"""
        try:
            response = await s3_client.get_bucket_location(Bucket=bucket)
            region = response.get('LocationConstraint')
            return region if region else 'us-east-1'  # None은 us-east-1을 의미
        except Exception:
            return 'unknown'


def main():
    """S3 CLI 메인 함수"""
    cli = S3CLI()
    return cli.main()


if __name__ == "__main__":
    exit(main())
