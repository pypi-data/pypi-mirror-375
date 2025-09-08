"""
Noti CLI - 다양한 알림 채널 지원 도구

레거시 pawnlib noti.py 기능을 pawnstack 아키텍처로 이식
"""

import asyncio
import json
import smtplib
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from argparse import ArgumentParser
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from pawnstack.cli.base import AsyncBaseCLI, register_cli_command
from pawnstack.config.global_config import pawn


@register_cli_command(
    name="noti",
    description="다양한 알림 채널 지원 도구",
    epilog="""
예제:
  pawns noti --slack-webhook https://hooks.slack.com/... --message "배포 완료"
  pawns noti --email user@example.com --subject "알림" --message "내용" --file report.pdf
  pawns noti --discord-webhook https://discord.com/api/webhooks/... --message "서버 재시작"
  pawns noti --template alert.json --data '{"server": "web01", "status": "down"}'
    """
)
class NotiCLI(AsyncBaseCLI):
    """알림 전송 CLI"""
    
    def __init__(self, args=None):
        super().__init__(args)
        self.notification_history = []
    
    def get_arguments(self, parser: ArgumentParser):
        """명령어 인수 정의"""
        # 기본 메시지 설정
        parser.add_argument(
            '--message', '-m',
            type=str,
            required=True,
            help='전송할 메시지 내용'
        )
        
        parser.add_argument(
            '--subject', '-s',
            type=str,
            help='메시지 제목 (이메일, 일부 채널에서 사용)'
        )
        
        parser.add_argument(
            '--priority',
            choices=['low', 'normal', 'high', 'urgent'],
            default='normal',
            help='알림 우선순위 (default: normal)'
        )
        
        # Slack 알림
        parser.add_argument(
            '--slack-webhook',
            type=str,
            help='Slack 웹훅 URL'
        )
        
        parser.add_argument(
            '--slack-channel',
            type=str,
            help='Slack 채널명 (예: #general)'
        )
        
        parser.add_argument(
            '--slack-username',
            type=str,
            default='PawnStack Bot',
            help='Slack 사용자명 (default: PawnStack Bot)'
        )
        
        parser.add_argument(
            '--slack-icon',
            type=str,
            default=':robot_face:',
            help='Slack 아이콘 (default: :robot_face:)'
        )
        
        # Discord 알림
        parser.add_argument(
            '--discord-webhook',
            type=str,
            help='Discord 웹훅 URL'
        )
        
        parser.add_argument(
            '--discord-username',
            type=str,
            default='PawnStack Bot',
            help='Discord 사용자명 (default: PawnStack Bot)'
        )
        
        # 이메일 알림
        parser.add_argument(
            '--email',
            type=str,
            action='append',
            help='이메일 주소 (여러 개 지정 가능)'
        )
        
        parser.add_argument(
            '--email-from',
            type=str,
            help='발신자 이메일 주소'
        )
        
        parser.add_argument(
            '--smtp-server',
            type=str,
            help='SMTP 서버 주소'
        )
        
        parser.add_argument(
            '--smtp-port',
            type=int,
            default=587,
            help='SMTP 포트 (default: 587)'
        )
        
        parser.add_argument(
            '--smtp-user',
            type=str,
            help='SMTP 사용자명'
        )
        
        parser.add_argument(
            '--smtp-password',
            type=str,
            help='SMTP 비밀번호'
        )
        
        parser.add_argument(
            '--smtp-tls',
            action='store_true',
            default=True,
            help='SMTP TLS 사용 (default: True)'
        )
        
        # 웹훅 알림 (일반)
        parser.add_argument(
            '--webhook',
            type=str,
            action='append',
            help='일반 웹훅 URL (여러 개 지정 가능)'
        )
        
        parser.add_argument(
            '--webhook-method',
            choices=['GET', 'POST', 'PUT'],
            default='POST',
            help='웹훅 HTTP 메서드 (default: POST)'
        )
        
        parser.add_argument(
            '--webhook-headers',
            type=str,
            action='append',
            help='웹훅 헤더 (형식: "Key: Value")'
        )
        
        # 파일 첨부
        parser.add_argument(
            '--file',
            type=str,
            action='append',
            help='첨부할 파일 경로 (여러 개 지정 가능)'
        )
        
        # 템플릿 시스템
        parser.add_argument(
            '--template',
            type=str,
            help='알림 템플릿 파일 경로'
        )
        
        parser.add_argument(
            '--data',
            type=str,
            help='템플릿 데이터 (JSON 형식)'
        )
        
        # 조건부 알림
        parser.add_argument(
            '--condition',
            type=str,
            help='알림 조건 (Python 표현식)'
        )
        
        parser.add_argument(
            '--retry',
            type=int,
            default=3,
            help='전송 실패시 재시도 횟수 (default: 3)'
        )
        
        parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='요청 타임아웃 (초, default: 30)'
        )
        
        # 출력 옵션
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='조용한 모드 (성공 메시지 숨김)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='실제 전송하지 않고 테스트만 수행'
        )
        
        parser.add_argument(
            '--save-history',
            type=str,
            help='알림 히스토리 저장 파일 경로'
        )
        
        # 설정 파일
        parser.add_argument(
            '--config',
            type=str,
            help='알림 설정 파일 경로'
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
    
    def load_template(self) -> Optional[Dict[str, Any]]:
        """템플릿 파일 로드"""
        if not hasattr(self.args, 'template') or not self.args.template:
            return None
        
        template_path = Path(self.args.template)
        
        if not template_path.exists():
            self.log_error(f"템플릿 파일을 찾을 수 없습니다: {self.args.template}")
            return None
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                if template_path.suffix.lower() == '.json':
                    template = json.load(f)
                elif template_path.suffix.lower() in ['.yml', '.yaml']:
                    import yaml
                    template = yaml.safe_load(f)
                else:
                    # 텍스트 템플릿
                    template = {'message': f.read()}
            
            self.log_debug(f"템플릿 로드 완료: {self.args.template}")
            return template
            
        except Exception as e:
            self.log_error(f"템플릿 로드 실패: {e}")
            return None
    
    def render_template(self, template: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """템플릿 렌더링"""
        try:
            import re
            
            def replace_variables(text: str, data: Dict[str, Any]) -> str:
                """변수 치환"""
                if not isinstance(text, str):
                    return text
                
                # {{variable}} 형식의 변수 치환
                pattern = r'\{\{(\w+)\}\}'
                
                def replacer(match):
                    var_name = match.group(1)
                    return str(data.get(var_name, match.group(0)))
                
                return re.sub(pattern, replacer, text)
            
            # 템플릿의 모든 문자열 값에 대해 변수 치환
            rendered = {}
            for key, value in template.items():
                if isinstance(value, str):
                    rendered[key] = replace_variables(value, data)
                elif isinstance(value, dict):
                    rendered[key] = self.render_template(value, data)
                elif isinstance(value, list):
                    rendered[key] = [
                        replace_variables(item, data) if isinstance(item, str) else item
                        for item in value
                    ]
                else:
                    rendered[key] = value
            
            return rendered
            
        except Exception as e:
            self.log_error(f"템플릿 렌더링 실패: {e}")
            return template
    
    def parse_template_data(self) -> Dict[str, Any]:
        """템플릿 데이터 파싱"""
        data = {}
        
        if hasattr(self.args, 'data') and self.args.data:
            try:
                data = json.loads(self.args.data)
            except json.JSONDecodeError as e:
                self.log_error(f"템플릿 데이터 파싱 실패: {e}")
        
        # 기본 변수 추가
        data.update({
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'hostname': self.get_hostname()
        })
        
        return data
    
    def get_hostname(self) -> str:
        """호스트명 반환"""
        try:
            import socket
            return socket.gethostname()
        except Exception:
            return 'unknown'
    
    def check_condition(self, data: Dict[str, Any]) -> bool:
        """조건 검사"""
        if not hasattr(self.args, 'condition') or not self.args.condition:
            return True
        
        try:
            # 안전한 eval을 위한 제한된 네임스페이스
            safe_dict = {
                '__builtins__': {},
                'data': data,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'True': True,
                'False': False,
                'None': None
            }
            
            result = eval(self.args.condition, safe_dict)
            return bool(result)
            
        except Exception as e:
            self.log_error(f"조건 검사 실패: {e}")
            return False
    
    def parse_webhook_headers(self) -> Dict[str, str]:
        """웹훅 헤더 파싱"""
        headers = {'Content-Type': 'application/json'}
        
        if hasattr(self.args, 'webhook_headers') and self.args.webhook_headers:
            for header in self.args.webhook_headers:
                if ':' in header:
                    key, value = header.split(':', 1)
                    headers[key.strip()] = value.strip()
        
        return headers
    
    async def send_slack_notification(self, message: str, subject: Optional[str] = None) -> bool:
        """Slack 알림 전송"""
        if not hasattr(self.args, 'slack_webhook') or not self.args.slack_webhook:
            return False
        
        try:
            import aiohttp
            
            # Slack 메시지 구성
            slack_message = {
                'text': subject or message,
                'username': self.args.slack_username,
                'icon_emoji': self.args.slack_icon
            }
            
            if hasattr(self.args, 'slack_channel') and self.args.slack_channel:
                slack_message['channel'] = self.args.slack_channel
            
            # 우선순위에 따른 색상 설정
            color_map = {
                'low': 'good',
                'normal': '#36a64f',
                'high': 'warning',
                'urgent': 'danger'
            }
            
            if subject and subject != message:
                # 제목과 내용이 다른 경우 attachment 사용
                slack_message['attachments'] = [{
                    'color': color_map.get(self.args.priority, '#36a64f'),
                    'title': subject,
                    'text': message,
                    'footer': 'PawnStack Notification',
                    'ts': int(time.time())
                }]
            
            if self.args.dry_run:
                self.log_info(f"[DRY RUN] Slack 메시지: {json.dumps(slack_message, indent=2, ensure_ascii=False)}")
                return True
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.args.slack_webhook,
                    json=slack_message,
                    timeout=aiohttp.ClientTimeout(total=self.args.timeout)
                ) as response:
                    if response.status == 200:
                        self.log_debug("Slack 알림 전송 성공")
                        return True
                    else:
                        self.log_error(f"Slack 알림 전송 실패: HTTP {response.status}")
                        return False
        
        except Exception as e:
            self.log_error(f"Slack 알림 전송 중 오류: {e}")
            return False
    
    async def send_discord_notification(self, message: str, subject: Optional[str] = None) -> bool:
        """Discord 알림 전송"""
        if not hasattr(self.args, 'discord_webhook') or not self.args.discord_webhook:
            return False
        
        try:
            import aiohttp
            
            # Discord 메시지 구성
            discord_message = {
                'content': f"**{subject}**\n{message}" if subject else message,
                'username': self.args.discord_username
            }
            
            # 우선순위에 따른 임베드 색상
            color_map = {
                'low': 0x36a64f,      # 녹색
                'normal': 0x3498db,   # 파란색
                'high': 0xf39c12,     # 주황색
                'urgent': 0xe74c3c    # 빨간색
            }
            
            if subject and subject != message:
                discord_message['embeds'] = [{
                    'title': subject,
                    'description': message,
                    'color': color_map.get(self.args.priority, 0x3498db),
                    'footer': {
                        'text': 'PawnStack Notification'
                    },
                    'timestamp': datetime.now().isoformat()
                }]
                discord_message['content'] = ''  # 임베드 사용시 content 비우기
            
            if self.args.dry_run:
                self.log_info(f"[DRY RUN] Discord 메시지: {json.dumps(discord_message, indent=2, ensure_ascii=False)}")
                return True
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.args.discord_webhook,
                    json=discord_message,
                    timeout=aiohttp.ClientTimeout(total=self.args.timeout)
                ) as response:
                    if response.status in [200, 204]:
                        self.log_debug("Discord 알림 전송 성공")
                        return True
                    else:
                        self.log_error(f"Discord 알림 전송 실패: HTTP {response.status}")
                        return False
        
        except Exception as e:
            self.log_error(f"Discord 알림 전송 중 오류: {e}")
            return False
    
    async def send_email_notification(self, message: str, subject: Optional[str] = None) -> bool:
        """이메일 알림 전송"""
        if not hasattr(self.args, 'email') or not self.args.email:
            return False
        
        try:
            # SMTP 설정
            smtp_server = self.args.smtp_server or pawn.get('SMTP_SERVER', 'localhost')
            smtp_port = self.args.smtp_port or pawn.get('SMTP_PORT', 587)
            smtp_user = self.args.smtp_user or pawn.get('SMTP_USER')
            smtp_password = self.args.smtp_password or pawn.get('SMTP_PASSWORD')
            email_from = self.args.email_from or smtp_user
            
            if not smtp_user or not smtp_password or not email_from:
                self.log_error("SMTP 인증 정보가 설정되지 않았습니다")
                return False
            
            # 이메일 메시지 구성
            msg = MIMEMultipart()
            msg['From'] = email_from
            msg['To'] = ', '.join(self.args.email)
            msg['Subject'] = subject or f"PawnStack 알림 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # 우선순위 헤더 설정
            priority_map = {
                'low': '5',
                'normal': '3',
                'high': '2',
                'urgent': '1'
            }
            msg['X-Priority'] = priority_map.get(self.args.priority, '3')
            
            # 메시지 본문
            body = f"""
{message}

---
이 메시지는 PawnStack에서 자동으로 전송되었습니다.
전송 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
호스트: {self.get_hostname()}
우선순위: {self.args.priority}
"""
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 파일 첨부
            if hasattr(self.args, 'file') and self.args.file:
                for file_path in self.args.file:
                    file_path_obj = Path(file_path)
                    if file_path_obj.exists():
                        try:
                            with open(file_path_obj, 'rb') as f:
                                part = MIMEBase('application', 'octet-stream')
                                part.set_payload(f.read())
                                encoders.encode_base64(part)
                                part.add_header(
                                    'Content-Disposition',
                                    f'attachment; filename= {file_path_obj.name}'
                                )
                                msg.attach(part)
                            
                            self.log_debug(f"파일 첨부: {file_path}")
                            
                        except Exception as e:
                            self.log_warning(f"파일 첨부 실패 ({file_path}): {e}")
                    else:
                        self.log_warning(f"첨부 파일을 찾을 수 없습니다: {file_path}")
            
            if self.args.dry_run:
                self.log_info(f"[DRY RUN] 이메일 전송 대상: {', '.join(self.args.email)}")
                self.log_info(f"[DRY RUN] 제목: {msg['Subject']}")
                self.log_info(f"[DRY RUN] 내용: {message}")
                return True
            
            # SMTP 서버 연결 및 전송
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if self.args.smtp_tls:
                    server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            self.log_debug(f"이메일 알림 전송 성공: {', '.join(self.args.email)}")
            return True
        
        except Exception as e:
            self.log_error(f"이메일 알림 전송 중 오류: {e}")
            return False
    
    async def send_webhook_notification(self, message: str, subject: Optional[str] = None) -> bool:
        """일반 웹훅 알림 전송"""
        if not hasattr(self.args, 'webhook') or not self.args.webhook:
            return False
        
        success_count = 0
        
        try:
            import aiohttp
            
            headers = self.parse_webhook_headers()
            
            # 웹훅 페이로드 구성
            payload = {
                'message': message,
                'subject': subject,
                'priority': self.args.priority,
                'timestamp': datetime.now().isoformat(),
                'hostname': self.get_hostname()
            }
            
            if self.args.dry_run:
                self.log_info(f"[DRY RUN] 웹훅 전송: {len(self.args.webhook)}개 URL")
                self.log_info(f"[DRY RUN] 페이로드: {json.dumps(payload, indent=2, ensure_ascii=False)}")
                return True
            
            async with aiohttp.ClientSession() as session:
                for webhook_url in self.args.webhook:
                    try:
                        if self.args.webhook_method == 'GET':
                            # GET 요청의 경우 쿼리 파라미터로 전송
                            params = {k: str(v) for k, v in payload.items() if v is not None}
                            async with session.get(
                                webhook_url,
                                params=params,
                                timeout=aiohttp.ClientTimeout(total=self.args.timeout)
                            ) as response:
                                if response.status < 400:
                                    success_count += 1
                                    self.log_debug(f"웹훅 전송 성공: {webhook_url}")
                                else:
                                    self.log_error(f"웹훅 전송 실패: {webhook_url} (HTTP {response.status})")
                        else:
                            # POST/PUT 요청
                            method = session.post if self.args.webhook_method == 'POST' else session.put
                            async with method(
                                webhook_url,
                                json=payload,
                                headers=headers,
                                timeout=aiohttp.ClientTimeout(total=self.args.timeout)
                            ) as response:
                                if response.status < 400:
                                    success_count += 1
                                    self.log_debug(f"웹훅 전송 성공: {webhook_url}")
                                else:
                                    self.log_error(f"웹훅 전송 실패: {webhook_url} (HTTP {response.status})")
                    
                    except Exception as e:
                        self.log_error(f"웹훅 전송 중 오류 ({webhook_url}): {e}")
            
            return success_count > 0
        
        except Exception as e:
            self.log_error(f"웹훅 알림 전송 중 오류: {e}")
            return False
    
    async def send_notification_with_retry(self, send_func, *args, **kwargs) -> bool:
        """재시도 로직이 포함된 알림 전송"""
        for attempt in range(self.args.retry + 1):
            try:
                if await send_func(*args, **kwargs):
                    return True
                
                if attempt < self.args.retry:
                    wait_time = 2 ** attempt  # 지수 백오프
                    self.log_debug(f"재시도 대기 중... ({wait_time}초)")
                    await asyncio.sleep(wait_time)
            
            except Exception as e:
                if attempt < self.args.retry:
                    wait_time = 2 ** attempt
                    self.log_warning(f"전송 실패 (시도 {attempt + 1}/{self.args.retry + 1}): {e}")
                    await asyncio.sleep(wait_time)
                else:
                    self.log_error(f"최종 전송 실패: {e}")
        
        return False
    
    def save_notification_history(self, message: str, subject: Optional[str], results: Dict[str, bool]):
        """알림 히스토리 저장"""
        if not hasattr(self.args, 'save_history') or not self.args.save_history:
            return
        
        try:
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'message': message,
                'subject': subject,
                'priority': self.args.priority,
                'hostname': self.get_hostname(),
                'results': results,
                'success': any(results.values())
            }
            
            self.notification_history.append(history_entry)
            
            # 파일에 저장
            history_path = Path(self.args.save_history)
            history_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(self.notification_history, f, indent=2, ensure_ascii=False)
            
            self.log_debug(f"알림 히스토리 저장: {self.args.save_history}")
            
        except Exception as e:
            self.log_error(f"알림 히스토리 저장 중 오류: {e}")
    
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
            
            # 템플릿 처리
            template = self.load_template()
            template_data = self.parse_template_data()
            
            message = getattr(self.args, 'message', None)
            if not message:
                self.log_error("메시지가 지정되지 않았습니다. --message 옵션을 사용하세요.")
                return 1
            
            subject = getattr(self.args, 'subject', None)
            
            if template:
                # 템플릿 렌더링
                rendered = self.render_template(template, template_data)
                message = rendered.get('message', message)
                subject = rendered.get('subject', subject)
                
                # 템플릿에서 다른 설정도 가져올 수 있음
                if 'priority' in rendered:
                    self.args.priority = rendered['priority']
            
            # 조건 검사
            if not self.check_condition(template_data):
                self.log_info("조건을 만족하지 않아 알림을 전송하지 않습니다")
                return 0
            
            self.log_info("알림 전송 시작")
            
            # 각 채널별 알림 전송
            results = {}
            
            # Slack 알림
            if hasattr(self.args, 'slack_webhook') and self.args.slack_webhook:
                results['slack'] = await self.send_notification_with_retry(
                    self.send_slack_notification, message, subject
                )
            
            # Discord 알림
            if hasattr(self.args, 'discord_webhook') and self.args.discord_webhook:
                results['discord'] = await self.send_notification_with_retry(
                    self.send_discord_notification, message, subject
                )
            
            # 이메일 알림
            if hasattr(self.args, 'email') and self.args.email:
                results['email'] = await self.send_notification_with_retry(
                    self.send_email_notification, message, subject
                )
            
            # 웹훅 알림
            if hasattr(self.args, 'webhook') and self.args.webhook:
                results['webhook'] = await self.send_notification_with_retry(
                    self.send_webhook_notification, message, subject
                )
            
            # 결과 확인
            if not results:
                self.log_error("전송할 알림 채널이 지정되지 않았습니다")
                return 1
            
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)
            
            # 히스토리 저장
            self.save_notification_history(message, subject, results)
            
            if success_count == total_count:
                if not self.args.quiet:
                    self.log_success(f"모든 알림 전송 완료 ({success_count}/{total_count})")
                return 0
            elif success_count > 0:
                self.log_warning(f"일부 알림 전송 실패 ({success_count}/{total_count})")
                return 1
            else:
                self.log_error("모든 알림 전송 실패")
                return 1
        
        except Exception as e:
            self.log_error(f"알림 전송 중 오류: {e}")
            return 1


def main():
    """CLI 진입점"""
    cli = NotiCLI()
    return cli.main()


if __name__ == "__main__":
    exit(main())