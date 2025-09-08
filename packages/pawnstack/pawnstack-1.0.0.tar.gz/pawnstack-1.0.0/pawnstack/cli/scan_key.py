"""
ScanKey CLI - 키 스캔 및 보안 검사 도구

레거시 pawnlib scan_key.py 기능을 pawnstack 아키텍처로 이식
"""

import asyncio
import json
import re
import hashlib
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Tuple
from argparse import ArgumentParser
from pathlib import Path

from pawnstack.cli.base import AsyncBaseCLI, register_cli_command
from pawnstack.config.global_config import pawn


@register_cli_command(
    name="scan-key",
    description="키 스캔 및 보안 검사 도구",
    epilog="""
예제:
  pawns scan-key --path /home/user --recursive
  pawns scan-key --file config.json --check-patterns
  pawns scan-key --url https://api.example.com --check-exposed
  pawns scan-key --directory /var/log --exclude "*.log" --format json
    """
)
class ScanKeyCLI(AsyncBaseCLI):
    """키 스캔 및 보안 검사 CLI"""
    
    def __init__(self, args=None):
        super().__init__(args)
        self.scan_results = []
        self.security_issues = []
        self.scanned_files = 0
        self.total_files = 0
        
        # 민감한 키 패턴 정의
        self.key_patterns = {
            'aws_access_key': {
                'pattern': r'AKIA[0-9A-Z]{16}',
                'description': 'AWS Access Key ID',
                'severity': 'high'
            },
            'aws_secret_key': {
                'pattern': r'[A-Za-z0-9/+=]{40}',
                'description': 'AWS Secret Access Key (추정)',
                'severity': 'high',
                'context_required': True
            },
            'github_token': {
                'pattern': r'ghp_[A-Za-z0-9]{36}',
                'description': 'GitHub Personal Access Token',
                'severity': 'high'
            },
            'github_oauth': {
                'pattern': r'gho_[A-Za-z0-9]{36}',
                'description': 'GitHub OAuth Token',
                'severity': 'high'
            },
            'slack_token': {
                'pattern': r'xox[baprs]-[A-Za-z0-9-]+',
                'description': 'Slack Token',
                'severity': 'medium'
            },
            'discord_token': {
                'pattern': r'[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}',
                'description': 'Discord Bot Token',
                'severity': 'medium'
            },
            'jwt_token': {
                'pattern': r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
                'description': 'JWT Token',
                'severity': 'medium'
            },
            'api_key_generic': {
                'pattern': r'[Aa][Pp][Ii]_?[Kk][Ee][Yy].*[\'"][A-Za-z0-9]{20,}[\'"]',
                'description': '일반 API Key',
                'severity': 'medium'
            },
            'private_key': {
                'pattern': r'-----BEGIN [A-Z ]+PRIVATE KEY-----',
                'description': 'Private Key',
                'severity': 'high'
            },
            'password_field': {
                'pattern': r'[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd].*[\'"][^\'"\s]{8,}[\'"]',
                'description': '비밀번호 필드',
                'severity': 'low'
            },
            'database_url': {
                'pattern': r'[a-zA-Z][a-zA-Z0-9+.-]*://[^\s]+:[^\s]+@[^\s]+',
                'description': '데이터베이스 연결 URL',
                'severity': 'high'
            },
            'email_credentials': {
                'pattern': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}:[^\s]{6,}',
                'description': '이메일 인증 정보',
                'severity': 'medium'
            }
        }
        
        # 의심스러운 파일 확장자
        self.suspicious_extensions = {
            '.key', '.pem', '.p12', '.pfx', '.jks', '.keystore',
            '.crt', '.cer', '.der', '.csr', '.p7b', '.p7c'
        }
        
        # 제외할 디렉토리
        self.default_exclude_dirs = {
            '.git', '.svn', '.hg', '__pycache__', 'node_modules',
            '.venv', 'venv', '.env', 'build', 'dist', '.cache'
        }
    
    def get_arguments(self, parser: ArgumentParser):
        """명령어 인수 정의"""
        # 스캔 대상
        parser.add_argument(
            '--path', '-p',
            type=str,
            help='스캔할 경로 (파일 또는 디렉토리)'
        )
        
        parser.add_argument(
            '--file', '-f',
            type=str,
            action='append',
            help='스캔할 파일 (여러 개 지정 가능)'
        )
        
        parser.add_argument(
            '--directory', '-d',
            type=str,
            action='append',
            help='스캔할 디렉토리 (여러 개 지정 가능)'
        )
        
        parser.add_argument(
            '--url', '-u',
            type=str,
            action='append',
            help='스캔할 URL (여러 개 지정 가능)'
        )
        
        # 스캔 옵션
        parser.add_argument(
            '--recursive', '-r',
            action='store_true',
            help='하위 디렉토리 재귀 스캔'
        )
        
        parser.add_argument(
            '--include',
            type=str,
            action='append',
            help='포함할 파일 패턴 (예: "*.py", "*.json")'
        )
        
        parser.add_argument(
            '--exclude',
            type=str,
            action='append',
            help='제외할 파일 패턴 (예: "*.log", "test_*")'
        )
        
        parser.add_argument(
            '--max-size',
            type=int,
            default=10,  # 10MB
            help='스캔할 최대 파일 크기 (MB, default: 10)'
        )
        
        parser.add_argument(
            '--max-depth',
            type=int,
            help='최대 디렉토리 깊이'
        )
        
        # 검사 옵션
        parser.add_argument(
            '--check-patterns',
            action='store_true',
            default=True,
            help='키 패턴 검사 수행 (default: True)'
        )
        
        parser.add_argument(
            '--check-entropy',
            action='store_true',
            help='문자열 엔트로피 검사 수행'
        )
        
        parser.add_argument(
            '--check-base64',
            action='store_true',
            help='Base64 인코딩된 데이터 검사'
        )
        
        parser.add_argument(
            '--check-exposed',
            action='store_true',
            help='공개된 키 검사 (URL 대상)'
        )
        
        parser.add_argument(
            '--entropy-threshold',
            type=float,
            default=4.5,
            help='엔트로피 임계값 (default: 4.5)'
        )
        
        parser.add_argument(
            '--min-length',
            type=int,
            default=20,
            help='검사할 최소 문자열 길이 (default: 20)'
        )
        
        # 심각도 필터
        parser.add_argument(
            '--severity',
            choices=['low', 'medium', 'high', 'all'],
            default='all',
            help='표시할 최소 심각도 (default: all)'
        )
        
        # 출력 옵션
        parser.add_argument(
            '--format',
            choices=['table', 'json', 'csv', 'sarif'],
            default='table',
            help='출력 형식 (default: table)'
        )
        
        parser.add_argument(
            '--output', '-o',
            type=str,
            help='결과 저장 파일 경로'
        )
        

        
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='조용한 모드 (요약만 출력)'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='상세 출력 모드'
        )
        
        # 보안 옵션
        parser.add_argument(
            '--hash-secrets',
            action='store_true',
            help='발견된 비밀 정보를 해시로 마스킹'
        )
        
        parser.add_argument(
            '--no-content',
            action='store_true',
            help='파일 내용을 결과에 포함하지 않음'
        )
        
        # 설정 파일
        parser.add_argument(
            '--config',
            type=str,
            help='스캔 설정 파일 경로'
        )
        
        parser.add_argument(
            '--patterns-file',
            type=str,
            help='커스텀 패턴 파일 경로'
        )
    
    def load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        config = {}
        
        if hasattr(self.args, 'config') and self.args.config:
            config_path = Path(self.args.config)
            
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        if config_path.suffix.lower() == '.json':
                            config = json.load(f)
                        elif config_path.suffix.lower() in ['.yml', '.yaml']:
                            import yaml
                            config = yaml.safe_load(f)
                        else:
                            self.log_warning(f"지원하지 않는 설정 파일 형식: {config_path.suffix}")
                    
                    self.log_debug(f"설정 파일 로드 완료: {self.args.config}")
                    
                except Exception as e:
                    self.log_error(f"설정 파일 로드 실패: {e}")
        
        return config
    
    def load_custom_patterns(self) -> Dict[str, Dict[str, Any]]:
        """커스텀 패턴 파일 로드"""
        if not hasattr(self.args, 'patterns_file') or not self.args.patterns_file:
            return {}
        
        patterns_path = Path(self.args.patterns_file)
        
        if not patterns_path.exists():
            self.log_warning(f"패턴 파일을 찾을 수 없습니다: {self.args.patterns_file}")
            return {}
        
        try:
            with open(patterns_path, 'r', encoding='utf-8') as f:
                if patterns_path.suffix.lower() == '.json':
                    patterns = json.load(f)
                elif patterns_path.suffix.lower() in ['.yml', '.yaml']:
                    import yaml
                    patterns = yaml.safe_load(f)
                else:
                    self.log_warning(f"지원하지 않는 패턴 파일 형식: {patterns_path.suffix}")
                    return {}
            
            self.log_debug(f"커스텀 패턴 로드 완료: {len(patterns)}개")
            return patterns
            
        except Exception as e:
            self.log_error(f"패턴 파일 로드 실패: {e}")
            return {}
    
    def should_scan_file(self, file_path: Path) -> bool:
        """파일 스캔 여부 결정"""
        # 파일 크기 검사
        try:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.args.max_size:
                self.log_debug(f"파일 크기 초과로 스킵: {file_path} ({file_size_mb:.1f}MB)")
                return False
        except OSError:
            return False
        
        # 포함 패턴 검사
        if hasattr(self.args, 'include') and self.args.include:
            import fnmatch
            if not any(fnmatch.fnmatch(file_path.name, pattern) for pattern in self.args.include):
                return False
        
        # 제외 패턴 검사
        if hasattr(self.args, 'exclude') and self.args.exclude:
            import fnmatch
            if any(fnmatch.fnmatch(file_path.name, pattern) for pattern in self.args.exclude):
                return False
        
        # 바이너리 파일 제외 (간단한 검사)
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\x00' in chunk:  # NULL 바이트가 있으면 바이너리로 간주
                    return False
        except (OSError, PermissionError):
            return False
        
        return True
    
    def calculate_entropy(self, text: str) -> float:
        """문자열 엔트로피 계산"""
        if not text:
            return 0.0
        
        # 문자 빈도 계산
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # 엔트로피 계산
        entropy = 0.0
        text_length = len(text)
        
        for count in char_counts.values():
            probability = count / text_length
            if probability > 0:
                entropy -= probability * (probability.bit_length() - 1)
        
        return entropy
    
    def is_base64_encoded(self, text: str) -> bool:
        """Base64 인코딩 여부 확인"""
        if len(text) < 4 or len(text) % 4 != 0:
            return False
        
        try:
            # Base64 디코딩 시도
            decoded = base64.b64decode(text, validate=True)
            # 디코딩된 결과가 의미있는 데이터인지 간단히 확인
            return len(decoded) > 0 and not all(b == 0 for b in decoded)
        except Exception:
            return False
    
    def mask_secret(self, secret: str) -> str:
        """비밀 정보 마스킹"""
        if not self.args.hash_secrets:
            # 간단한 마스킹
            if len(secret) <= 8:
                return '*' * len(secret)
            else:
                return secret[:4] + '*' * (len(secret) - 8) + secret[-4:]
        else:
            # 해시 기반 마스킹
            hash_obj = hashlib.sha256(secret.encode('utf-8'))
            return f"[HASH:{hash_obj.hexdigest()[:16]}]"
    
    def scan_text_content(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """텍스트 내용 스캔"""
        findings = []
        lines = content.split('\n')
        
        # 패턴 기반 검사
        if self.args.check_patterns:
            all_patterns = self.key_patterns.copy()
            custom_patterns = self.load_custom_patterns()
            all_patterns.update(custom_patterns)
            
            for pattern_name, pattern_info in all_patterns.items():
                pattern = pattern_info['pattern']
                
                for line_num, line in enumerate(lines, 1):
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    
                    for match in matches:
                        matched_text = match.group(0)
                        
                        # 컨텍스트 검사가 필요한 경우
                        if pattern_info.get('context_required'):
                            # AWS Secret Key 같은 경우 주변 컨텍스트 확인
                            context = line.lower()
                            if not any(keyword in context for keyword in ['secret', 'key', 'password', 'token']):
                                continue
                        
                        finding = {
                            'type': 'pattern',
                            'pattern_name': pattern_name,
                            'description': pattern_info['description'],
                            'severity': pattern_info['severity'],
                            'file_path': file_path,
                            'line_number': line_num,
                            'column': match.start() + 1,
                            'matched_text': self.mask_secret(matched_text) if not self.args.no_content else '[MASKED]',
                            'line_content': line.strip() if not self.args.no_content else '[MASKED]'
                        }
                        
                        findings.append(finding)
        
        # 엔트로피 기반 검사
        if self.args.check_entropy:
            for line_num, line in enumerate(lines, 1):
                # 문자열 리터럴 추출 (따옴표로 둘러싸인 부분)
                string_patterns = [
                    r'"([^"]{' + str(self.args.min_length) + r',})"',
                    r"'([^']{" + str(self.args.min_length) + r",})'"
                ]
                
                for pattern in string_patterns:
                    matches = re.finditer(pattern, line)
                    
                    for match in matches:
                        text = match.group(1)
                        entropy = self.calculate_entropy(text)
                        
                        if entropy >= self.args.entropy_threshold:
                            finding = {
                                'type': 'entropy',
                                'description': f'높은 엔트로피 문자열 (엔트로피: {entropy:.2f})',
                                'severity': 'medium',
                                'file_path': file_path,
                                'line_number': line_num,
                                'column': match.start() + 1,
                                'matched_text': self.mask_secret(text) if not self.args.no_content else '[MASKED]',
                                'entropy': entropy,
                                'line_content': line.strip() if not self.args.no_content else '[MASKED]'
                            }
                            
                            findings.append(finding)
        
        # Base64 검사
        if self.args.check_base64:
            base64_pattern = r'[A-Za-z0-9+/]{' + str(self.args.min_length) + r',}={0,2}'
            
            for line_num, line in enumerate(lines, 1):
                matches = re.finditer(base64_pattern, line)
                
                for match in matches:
                    text = match.group(0)
                    
                    if self.is_base64_encoded(text):
                        finding = {
                            'type': 'base64',
                            'description': 'Base64 인코딩된 데이터',
                            'severity': 'low',
                            'file_path': file_path,
                            'line_number': line_num,
                            'column': match.start() + 1,
                            'matched_text': self.mask_secret(text) if not self.args.no_content else '[MASKED]',
                            'line_content': line.strip() if not self.args.no_content else '[MASKED]'
                        }
                        
                        findings.append(finding)
        
        return findings
    
    async def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """단일 파일 스캔"""
        findings = []
        
        try:
            # 파일 확장자 검사
            if file_path.suffix.lower() in self.suspicious_extensions:
                finding = {
                    'type': 'suspicious_file',
                    'description': f'의심스러운 파일 확장자: {file_path.suffix}',
                    'severity': 'medium',
                    'file_path': str(file_path),
                    'line_number': 0,
                    'column': 0
                }
                findings.append(finding)
            
            # 파일 내용 읽기
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 텍스트 내용 스캔
            text_findings = self.scan_text_content(content, str(file_path))
            findings.extend(text_findings)
            
            self.scanned_files += 1
            
            if self.args.verbose and findings:
                self.log_info(f"스캔 완료: {file_path} ({len(findings)}개 발견)")
            
        except Exception as e:
            self.log_debug(f"파일 스캔 실패: {file_path} - {e}")
        
        return findings
    
    async def scan_directory(self, directory: Path, current_depth: int = 0) -> List[Dict[str, Any]]:
        """디렉토리 스캔"""
        findings = []
        
        if hasattr(self.args, 'max_depth') and self.args.max_depth and current_depth >= self.args.max_depth:
            return findings
        
        try:
            for item in directory.iterdir():
                if item.is_file():
                    if self.should_scan_file(item):
                        self.total_files += 1
                        file_findings = await self.scan_file(item)
                        findings.extend(file_findings)
                
                elif item.is_dir() and self.args.recursive:
                    # 제외 디렉토리 검사
                    if item.name not in self.default_exclude_dirs:
                        dir_findings = await self.scan_directory(item, current_depth + 1)
                        findings.extend(dir_findings)
        
        except PermissionError:
            self.log_debug(f"디렉토리 접근 권한 없음: {directory}")
        except Exception as e:
            self.log_debug(f"디렉토리 스캔 실패: {directory} - {e}")
        
        return findings
    
    async def scan_url(self, url: str) -> List[Dict[str, Any]]:
        """URL 스캔"""
        findings = []
        
        if not self.args.check_exposed:
            return findings
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # URL 내용 스캔
                        url_findings = self.scan_text_content(content, url)
                        findings.extend(url_findings)
                        
                        # 공개된 키 특별 검사
                        if any(pattern in content.lower() for pattern in ['key', 'token', 'secret', 'password']):
                            finding = {
                                'type': 'exposed_endpoint',
                                'description': '공개된 엔드포인트에서 민감한 정보 발견 가능성',
                                'severity': 'high',
                                'file_path': url,
                                'line_number': 0,
                                'column': 0
                            }
                            findings.append(finding)
                    
                    else:
                        self.log_debug(f"URL 접근 실패: {url} (HTTP {response.status})")
        
        except Exception as e:
            self.log_debug(f"URL 스캔 실패: {url} - {e}")
        
        return findings
    
    def filter_by_severity(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """심각도별 필터링"""
        if self.args.severity == 'all':
            return findings
        
        severity_levels = {'low': 1, 'medium': 2, 'high': 3}
        min_level = severity_levels.get(self.args.severity, 1)
        
        filtered = []
        for finding in findings:
            finding_level = severity_levels.get(finding.get('severity', 'low'), 1)
            if finding_level >= min_level:
                filtered.append(finding)
        
        return filtered
    
    def display_results(self, findings: List[Dict[str, Any]]):
        """결과 출력"""
        if self.args.quiet:
            return
        
        if self.args.format == 'json':
            output = {
                'scan_summary': {
                    'total_files': self.total_files,
                    'scanned_files': self.scanned_files,
                    'findings_count': len(findings),
                    'scan_time': datetime.now().isoformat()
                },
                'findings': findings
            }
            pawn.console.print_json(data=output)
            
        elif self.args.format == 'csv':
            # CSV 헤더
            headers = ['file_path', 'line_number', 'severity', 'type', 'description']
            print(','.join(headers))
            
            # CSV 데이터
            for finding in findings:
                row = [
                    finding.get('file_path', ''),
                    str(finding.get('line_number', 0)),
                    finding.get('severity', ''),
                    finding.get('type', ''),
                    finding.get('description', '').replace(',', ';')  # CSV 호환성
                ]
                print(','.join(row))
                
        elif self.args.format == 'sarif':
            # SARIF 형식 (Static Analysis Results Interchange Format)
            sarif_output = {
                'version': '2.1.0',
                'runs': [{
                    'tool': {
                        'driver': {
                            'name': 'PawnStack ScanKey',
                            'version': '1.0.0'
                        }
                    },
                    'results': []
                }]
            }
            
            for finding in findings:
                sarif_result = {
                    'ruleId': finding.get('type', 'unknown'),
                    'message': {
                        'text': finding.get('description', '')
                    },
                    'level': {
                        'low': 'note',
                        'medium': 'warning',
                        'high': 'error'
                    }.get(finding.get('severity', 'low'), 'note'),
                    'locations': [{
                        'physicalLocation': {
                            'artifactLocation': {
                                'uri': finding.get('file_path', '')
                            },
                            'region': {
                                'startLine': finding.get('line_number', 1),
                                'startColumn': finding.get('column', 1)
                            }
                        }
                    }]
                }
                sarif_output['runs'][0]['results'].append(sarif_result)
            
            pawn.console.print_json(data=sarif_output)
            
        else:  # table 형식
            from rich.table import Table
            from rich.panel import Panel
            
            # 요약 정보
            summary_text = f"""
스캔 완료 요약:
• 총 파일 수: {self.total_files}
• 스캔된 파일: {self.scanned_files}
• 발견된 이슈: {len(findings)}
"""
            
            if findings:
                severity_counts = {}
                for finding in findings:
                    severity = finding.get('severity', 'unknown')
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                summary_text += "\n심각도별 분포:\n"
                for severity, count in sorted(severity_counts.items()):
                    summary_text += f"• {severity}: {count}개\n"
            
            summary_panel = Panel(summary_text.strip(), title="🔍 스캔 결과 요약", border_style="blue")
            pawn.console.print(summary_panel)
            
            if findings:
                # 발견된 이슈 테이블
                table = Table(title="🚨 발견된 보안 이슈")
                table.add_column("파일", style="cyan", width=30)
                table.add_column("라인", style="white", width=6)
                table.add_column("심각도", style="yellow", width=8)
                table.add_column("유형", style="green", width=15)
                table.add_column("설명", style="white")
                
                for finding in findings[:50]:  # 최대 50개만 표시
                    # 심각도별 색상
                    severity_colors = {
                        'low': 'green',
                        'medium': 'yellow',
                        'high': 'red'
                    }
                    severity_color = severity_colors.get(finding.get('severity', 'low'), 'white')
                    
                    file_path = finding.get('file_path', '')
                    if len(file_path) > 30:
                        file_path = '...' + file_path[-27:]
                    
                    table.add_row(
                        file_path,
                        str(finding.get('line_number', 0)),
                        f"[{severity_color}]{finding.get('severity', 'unknown')}[/{severity_color}]",
                        finding.get('type', 'unknown'),
                        finding.get('description', '')[:60] + ('...' if len(finding.get('description', '')) > 60 else '')
                    )
                
                pawn.console.print(table)
                
                if len(findings) > 50:
                    pawn.console.print(f"\n[yellow]⚠️  {len(findings) - 50}개의 추가 이슈가 있습니다. --output 옵션으로 전체 결과를 저장하세요.[/yellow]")
    
    def save_results(self, findings: List[Dict[str, Any]]):
        """결과 저장"""
        if not hasattr(self.args, 'output') or not self.args.output:
            return
        
        try:
            output_path = Path(self.args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            output_data = {
                'scan_summary': {
                    'total_files': self.total_files,
                    'scanned_files': self.scanned_files,
                    'findings_count': len(findings),
                    'scan_time': datetime.now().isoformat(),
                    'scan_args': vars(self.args)
                },
                'findings': findings
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                if output_path.suffix.lower() == '.json':
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                elif output_path.suffix.lower() in ['.yml', '.yaml']:
                    import yaml
                    yaml.dump(output_data, f, default_flow_style=False, allow_unicode=True)
                else:
                    # 기본적으로 JSON으로 저장
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            self.log_success(f"결과 저장 완료: {self.args.output}")
            
        except Exception as e:
            self.log_error(f"결과 저장 실패: {e}")
    
    async def run_async(self) -> int:
        """비동기 실행"""
        try:
            # 설정 로드
            config = self.load_config()
            
            # 설정 파일의 값으로 기본값 업데이트
            if config:
                for key, value in config.items():
                    if not hasattr(self.args, key) or getattr(self.args, key) is None:
                        setattr(self.args, key, value)
            
            self.log_info("키 스캔 시작")
            
            all_findings = []
            
            # 파일 스캔
            if hasattr(self.args, 'file') and self.args.file:
                for file_path in self.args.file:
                    file_path_obj = Path(file_path)
                    if file_path_obj.exists() and file_path_obj.is_file():
                        if self.should_scan_file(file_path_obj):
                            self.total_files += 1
                            findings = await self.scan_file(file_path_obj)
                            all_findings.extend(findings)
                    else:
                        self.log_warning(f"파일을 찾을 수 없습니다: {file_path}")
            
            # 디렉토리 스캔
            directories_to_scan = []
            
            if hasattr(self.args, 'directory') and self.args.directory:
                directories_to_scan.extend(self.args.directory)
            
            if hasattr(self.args, 'path') and self.args.path:
                path_obj = Path(self.args.path)
                if path_obj.exists():
                    if path_obj.is_file():
                        if self.should_scan_file(path_obj):
                            self.total_files += 1
                            findings = await self.scan_file(path_obj)
                            all_findings.extend(findings)
                    elif path_obj.is_dir():
                        directories_to_scan.append(str(path_obj))
                else:
                    self.log_warning(f"경로를 찾을 수 없습니다: {self.args.path}")
            
            # 디렉토리들 스캔
            for directory_path in directories_to_scan:
                directory_obj = Path(directory_path)
                if directory_obj.exists() and directory_obj.is_dir():
                    self.log_info(f"디렉토리 스캔: {directory_path}")
                    findings = await self.scan_directory(directory_obj)
                    all_findings.extend(findings)
                else:
                    self.log_warning(f"디렉토리를 찾을 수 없습니다: {directory_path}")
            
            # URL 스캔
            if hasattr(self.args, 'url') and self.args.url:
                for url in self.args.url:
                    self.log_info(f"URL 스캔: {url}")
                    findings = await self.scan_url(url)
                    all_findings.extend(findings)
            
            # 스캔 대상이 없는 경우
            if not all_findings and self.total_files == 0:
                self.log_error("스캔할 대상이 지정되지 않았습니다. --path, --file, --directory, 또는 --url 옵션을 사용하세요.")
                return 1
            
            # 심각도별 필터링
            filtered_findings = self.filter_by_severity(all_findings)
            
            # 결과 출력
            self.display_results(filtered_findings)
            
            # 결과 저장
            self.save_results(filtered_findings)
            
            # 종료 코드 결정
            if filtered_findings:
                high_severity_count = sum(1 for f in filtered_findings if f.get('severity') == 'high')
                if high_severity_count > 0:
                    self.log_warning(f"높은 심각도 이슈 {high_severity_count}개 발견")
                    return 1
                else:
                    self.log_info("스캔 완료 (낮은/중간 심각도 이슈만 발견)")
                    return 0
            else:
                self.log_success("스캔 완료 (이슈 없음)")
                return 0
        
        except Exception as e:
            self.log_error(f"키 스캔 중 오류: {e}")
            return 1


def main():
    """CLI 진입점"""
    cli = ScanKeyCLI()
    return cli.main()


if __name__ == "__main__":
    exit(main())