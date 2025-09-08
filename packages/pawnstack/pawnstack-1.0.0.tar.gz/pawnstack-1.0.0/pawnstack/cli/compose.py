"""
PawnStack Docker Compose 도구

Docker Compose 프로젝트 관리 도구
"""

import asyncio
import json
import subprocess
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from argparse import ArgumentParser
from pathlib import Path

from pawnstack import __version__
from pawnstack.config.global_config import pawn
from pawnstack.cli.base import ContainerBaseCLI
from pawnstack.cli.banner import generate_banner

# 모듈 메타데이터
__description__ = 'Command Line Interface for managing Docker Compose projects'

__epilog__ = (
    "This script provides various commands for Docker Compose project management.\n\n"
    "Usage examples:\n"
    "  1. Start services:\n\tpawns compose up\n\n"
    "  2. Stop services:\n\tpawns compose down\n\n"
    "  3. View service status:\n\tpawns compose ps\n\n"
    "  4. Scale services:\n\tpawns compose scale web=3\n\n"
    "  5. View logs:\n\tpawns compose logs -f web\n\n"
    "For more details, use the -h or --help flag."
)


@dataclass
class ComposeConfig:
    """Docker Compose 설정"""
    command: str = "ps"
    services: List[str] = None
    detach: bool = True
    build: bool = False
    force_recreate: bool = False
    remove_orphans: bool = False
    scale: Dict[str, int] = None
    follow_logs: bool = False
    tail: int = 50
    
    def __post_init__(self):
        if self.services is None:
            self.services = []
        if self.scale is None:
            self.scale = {}


class ComposeCLI(ContainerBaseCLI):
    """Docker Compose CLI"""
    
    def __init__(self, args=None):
        super().__init__(args)
    
    def get_arguments(self, parser: ArgumentParser):
        """인수 정의"""
        # 컨테이너 공통 인수 추가
        self.get_common_container_arguments(parser)
        
        parser.add_argument('command', help='Command to execute', 
                          choices=['up', 'down', 'ps', 'logs', 'build', 'pull', 'restart', 'stop', 'start', 'scale', 'exec', 'config'], 
                          nargs='?', default='ps')
        
        parser.add_argument('services', nargs='*', help='Service names to operate on')
        
        # up/down 옵션
        parser.add_argument('-d', '--detach', action='store_true', help='Detached mode', default=True)
        parser.add_argument('--build', action='store_true', help='Build images before starting')
        parser.add_argument('--force-recreate', action='store_true', help='Recreate containers even if config unchanged')
        parser.add_argument('--remove-orphans', action='store_true', help='Remove containers for services not defined in compose file')
        parser.add_argument('--no-deps', action='store_true', help='Don\'t start linked services')
        
        # 로그 옵션
        parser.add_argument('-f', '--follow', action='store_true', help='Follow log output')
        parser.add_argument('--tail', type=int, default=50, help='Number of lines to show from end of logs')
        parser.add_argument('--since', type=str, help='Show logs since timestamp')
        
        # scale 옵션
        parser.add_argument('--scale', type=str, action='append', help='Scale SERVICE to NUM instances (format: SERVICE=NUM)')
        
        # exec 옵션
        parser.add_argument('--exec-service', type=str, help='Service name for exec command')
        parser.add_argument('--exec-command', type=str, default='/bin/bash', help='Command to execute in service')
        parser.add_argument('--interactive', '-it', action='store_true', help='Interactive mode')
        
        # 일반 옵션
        parser.add_argument('--parallel', type=int, help='Control the number of parallel operations')
        parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                          help='Logging level (default: INFO)', default="INFO")
    
    def setup_config(self):
        """설정 초기화"""
        args = self.args
        app_name = 'compose'
        
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
            app_name="Docker Compose",
            author="PawnStack Team",
            version=__version__,
            font="graffiti"
        )
        print(banner)
    
    def create_config(self) -> ComposeConfig:
        """설정 객체 생성"""
        scale_dict = {}
        if hasattr(self.args, 'scale') and self.args.scale:
            for scale_item in self.args.scale:
                if '=' in scale_item:
                    service, count = scale_item.split('=', 1)
                    try:
                        scale_dict[service.strip()] = int(count.strip())
                    except ValueError:
                        self.log_warning(f"Invalid scale format: {scale_item}")
        
        return ComposeConfig(
            command=getattr(self.args, 'command', 'ps'),
            services=getattr(self.args, 'services', []),
            detach=getattr(self.args, 'detach', True),
            build=getattr(self.args, 'build', False),
            force_recreate=getattr(self.args, 'force_recreate', False),
            remove_orphans=getattr(self.args, 'remove_orphans', False),
            scale=scale_dict,
            follow_logs=getattr(self.args, 'follow', False),
            tail=getattr(self.args, 'tail', 50)
        )
    
    def check_compose_available(self) -> bool:
        """Docker Compose 사용 가능 여부 확인"""
        try:
            # docker compose 명령어 확인 (새 버전)
            result = subprocess.run(['docker', 'compose', 'version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True
            
            # docker-compose 명령어 확인 (레거시)
            result = subprocess.run(['docker-compose', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_compose_command(self) -> List[str]:
        """Docker Compose 명령어 반환"""
        # 새 버전 우선 사용
        try:
            result = subprocess.run(['docker', 'compose', 'version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return ['docker', 'compose']
        except:
            pass
        
        # 레거시 버전 사용
        return ['docker-compose']
    
    async def run_compose_command(self, cmd: List[str], stream_output: bool = False) -> Dict[str, Any]:
        """Docker Compose 명령어 실행"""
        try:
            if stream_output:
                # 실시간 출력 스트리밍
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                async def stream_reader(stream, prefix=""):
                    while True:
                        line = await stream.readline()
                        if not line:
                            break
                        pawn.console.print(f"{prefix}{line.decode('utf-8').rstrip()}")
                
                # stdout와 stderr를 동시에 스트리밍
                await asyncio.gather(
                    stream_reader(process.stdout),
                    stream_reader(process.stderr, "[red]")
                )
                
                returncode = await process.wait()
                
                return {
                    "success": returncode == 0,
                    "stdout": "",
                    "stderr": "",
                    "returncode": returncode
                }
            else:
                # 일반 실행
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                return {
                    "success": process.returncode == 0,
                    "stdout": stdout.decode('utf-8').strip(),
                    "stderr": stderr.decode('utf-8').strip(),
                    "returncode": process.returncode
                }
                
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    async def compose_up(self, config: ComposeConfig):
        """서비스 시작"""
        pawn.console.log("🚀 Starting Docker Compose services...")
        
        cmd = self.get_compose_command()
        
        # 프로젝트 이름 및 파일 옵션
        if hasattr(self.args, 'compose_file') and self.args.compose_file:
            cmd.extend(['-f', self.args.compose_file])
        
        if hasattr(self.args, 'project_name') and self.args.project_name:
            cmd.extend(['-p', self.args.project_name])
        
        cmd.append('up')
        
        # 옵션 추가
        if config.detach:
            cmd.append('-d')
        
        if config.build:
            cmd.append('--build')
        
        if config.force_recreate:
            cmd.append('--force-recreate')
        
        if config.remove_orphans:
            cmd.append('--remove-orphans')
        
        if hasattr(self.args, 'no_deps') and self.args.no_deps:
            cmd.append('--no-deps')
        
        # 서비스 지정
        if config.services:
            cmd.extend(config.services)
        
        pawn.console.log(f"🔧 Command: {' '.join(cmd)}")
        
        result = await self.run_compose_command(cmd, stream_output=not config.detach)
        
        if result["success"]:
            self.log_success("Services started successfully")
        else:
            self.log_error(f"Failed to start services: {result['stderr']}")
    
    async def compose_down(self, config: ComposeConfig):
        """서비스 중지 및 제거"""
        pawn.console.log("🛑 Stopping Docker Compose services...")
        
        cmd = self.get_compose_command()
        
        # 프로젝트 이름 및 파일 옵션
        if hasattr(self.args, 'compose_file') and self.args.compose_file:
            cmd.extend(['-f', self.args.compose_file])
        
        if hasattr(self.args, 'project_name') and self.args.project_name:
            cmd.extend(['-p', self.args.project_name])
        
        cmd.append('down')
        
        if config.remove_orphans:
            cmd.append('--remove-orphans')
        
        result = await self.run_compose_command(cmd)
        
        if result["success"]:
            self.log_success("Services stopped successfully")
            if result["stdout"]:
                pawn.console.print(result["stdout"])
        else:
            self.log_error(f"Failed to stop services: {result['stderr']}")
    
    async def compose_ps(self, config: ComposeConfig):
        """서비스 상태 조회"""
        pawn.console.log("📋 Listing Docker Compose services...")
        
        cmd = self.get_compose_command()
        
        # 프로젝트 이름 및 파일 옵션
        if hasattr(self.args, 'compose_file') and self.args.compose_file:
            cmd.extend(['-f', self.args.compose_file])
        
        if hasattr(self.args, 'project_name') and self.args.project_name:
            cmd.extend(['-p', self.args.project_name])
        
        cmd.extend(['ps', '--format', 'table'])
        
        result = await self.run_compose_command(cmd)
        
        if result["success"]:
            if result["stdout"]:
                pawn.console.print(result["stdout"])
            else:
                pawn.console.log("[yellow]No services found[/yellow]")
        else:
            self.log_error(f"Failed to list services: {result['stderr']}")
    
    async def compose_logs(self, config: ComposeConfig):
        """서비스 로그 조회"""
        pawn.console.log("📋 Showing Docker Compose logs...")
        
        cmd = self.get_compose_command()
        
        # 프로젝트 이름 및 파일 옵션
        if hasattr(self.args, 'compose_file') and self.args.compose_file:
            cmd.extend(['-f', self.args.compose_file])
        
        if hasattr(self.args, 'project_name') and self.args.project_name:
            cmd.extend(['-p', self.args.project_name])
        
        cmd.append('logs')
        
        # 로그 옵션
        if config.follow_logs:
            cmd.append('-f')
        
        cmd.extend(['--tail', str(config.tail)])
        
        if hasattr(self.args, 'since') and self.args.since:
            cmd.extend(['--since', self.args.since])
        
        # 서비스 지정
        if config.services:
            cmd.extend(config.services)
        
        try:
            if config.follow_logs:
                pawn.console.log("[cyan]--- Following logs (Press Ctrl+C to stop) ---[/cyan]")
                await self.run_compose_command(cmd, stream_output=True)
            else:
                result = await self.run_compose_command(cmd)
                if result["success"]:
                    if result["stdout"]:
                        pawn.console.print(result["stdout"])
                    else:
                        pawn.console.log("[yellow]No logs found[/yellow]")
                else:
                    self.log_error(f"Failed to get logs: {result['stderr']}")
        
        except KeyboardInterrupt:
            pawn.console.log("\n[yellow]Log streaming stopped by user[/yellow]")
    
    async def compose_build(self, config: ComposeConfig):
        """서비스 빌드"""
        pawn.console.log("🔨 Building Docker Compose services...")
        
        cmd = self.get_compose_command()
        
        # 프로젝트 이름 및 파일 옵션
        if hasattr(self.args, 'compose_file') and self.args.compose_file:
            cmd.extend(['-f', self.args.compose_file])
        
        if hasattr(self.args, 'project_name') and self.args.project_name:
            cmd.extend(['-p', self.args.project_name])
        
        cmd.append('build')
        
        # 병렬 처리
        if hasattr(self.args, 'parallel') and self.args.parallel:
            cmd.extend(['--parallel', str(self.args.parallel)])
        
        # 서비스 지정
        if config.services:
            cmd.extend(config.services)
        
        result = await self.run_compose_command(cmd, stream_output=True)
        
        if result["success"]:
            self.log_success("Build completed successfully")
        else:
            self.log_error("Build failed")
    
    async def compose_pull(self, config: ComposeConfig):
        """서비스 이미지 풀"""
        pawn.console.log("📥 Pulling Docker Compose service images...")
        
        cmd = self.get_compose_command()
        
        # 프로젝트 이름 및 파일 옵션
        if hasattr(self.args, 'compose_file') and self.args.compose_file:
            cmd.extend(['-f', self.args.compose_file])
        
        if hasattr(self.args, 'project_name') and self.args.project_name:
            cmd.extend(['-p', self.args.project_name])
        
        cmd.append('pull')
        
        # 서비스 지정
        if config.services:
            cmd.extend(config.services)
        
        result = await self.run_compose_command(cmd, stream_output=True)
        
        if result["success"]:
            self.log_success("Pull completed successfully")
        else:
            self.log_error("Pull failed")
    
    async def compose_restart(self, config: ComposeConfig):
        """서비스 재시작"""
        pawn.console.log("🔄 Restarting Docker Compose services...")
        
        cmd = self.get_compose_command()
        
        # 프로젝트 이름 및 파일 옵션
        if hasattr(self.args, 'compose_file') and self.args.compose_file:
            cmd.extend(['-f', self.args.compose_file])
        
        if hasattr(self.args, 'project_name') and self.args.project_name:
            cmd.extend(['-p', self.args.project_name])
        
        cmd.append('restart')
        
        # 서비스 지정
        if config.services:
            cmd.extend(config.services)
        
        result = await self.run_compose_command(cmd)
        
        if result["success"]:
            self.log_success("Services restarted successfully")
        else:
            self.log_error(f"Failed to restart services: {result['stderr']}")
    
    async def compose_stop(self, config: ComposeConfig):
        """서비스 중지"""
        pawn.console.log("⏹️  Stopping Docker Compose services...")
        
        cmd = self.get_compose_command()
        
        # 프로젝트 이름 및 파일 옵션
        if hasattr(self.args, 'compose_file') and self.args.compose_file:
            cmd.extend(['-f', self.args.compose_file])
        
        if hasattr(self.args, 'project_name') and self.args.project_name:
            cmd.extend(['-p', self.args.project_name])
        
        cmd.append('stop')
        
        # 서비스 지정
        if config.services:
            cmd.extend(config.services)
        
        result = await self.run_compose_command(cmd)
        
        if result["success"]:
            self.log_success("Services stopped successfully")
        else:
            self.log_error(f"Failed to stop services: {result['stderr']}")
    
    async def compose_start(self, config: ComposeConfig):
        """서비스 시작"""
        pawn.console.log("▶️  Starting Docker Compose services...")
        
        cmd = self.get_compose_command()
        
        # 프로젝트 이름 및 파일 옵션
        if hasattr(self.args, 'compose_file') and self.args.compose_file:
            cmd.extend(['-f', self.args.compose_file])
        
        if hasattr(self.args, 'project_name') and self.args.project_name:
            cmd.extend(['-p', self.args.project_name])
        
        cmd.append('start')
        
        # 서비스 지정
        if config.services:
            cmd.extend(config.services)
        
        result = await self.run_compose_command(cmd)
        
        if result["success"]:
            self.log_success("Services started successfully")
        else:
            self.log_error(f"Failed to start services: {result['stderr']}")
    
    async def compose_scale(self, config: ComposeConfig):
        """서비스 스케일링"""
        if not config.scale:
            self.log_error("Scale configuration is required. Use --scale SERVICE=NUM")
            return
        
        pawn.console.log("📈 Scaling Docker Compose services...")
        
        cmd = self.get_compose_command()
        
        # 프로젝트 이름 및 파일 옵션
        if hasattr(self.args, 'compose_file') and self.args.compose_file:
            cmd.extend(['-f', self.args.compose_file])
        
        if hasattr(self.args, 'project_name') and self.args.project_name:
            cmd.extend(['-p', self.args.project_name])
        
        cmd.append('up')
        cmd.append('-d')  # 스케일링은 detached 모드에서
        
        # 스케일 설정 추가
        for service, count in config.scale.items():
            cmd.extend(['--scale', f"{service}={count}"])
        
        pawn.console.log(f"🔧 Scaling: {', '.join([f'{s}={c}' for s, c in config.scale.items()])}")
        
        result = await self.run_compose_command(cmd)
        
        if result["success"]:
            self.log_success("Services scaled successfully")
        else:
            self.log_error(f"Failed to scale services: {result['stderr']}")
    
    async def compose_exec(self, config: ComposeConfig):
        """서비스에서 명령어 실행"""
        exec_service = getattr(self.args, 'exec_service', None)
        if not exec_service:
            self.log_error("Service name is required for exec command. Use --exec-service SERVICE")
            return
        
        exec_command = getattr(self.args, 'exec_command', '/bin/bash')
        pawn.console.log(f"🔧 Executing '{exec_command}' in service: {exec_service}")
        
        cmd = self.get_compose_command()
        
        # 프로젝트 이름 및 파일 옵션
        if hasattr(self.args, 'compose_file') and self.args.compose_file:
            cmd.extend(['-f', self.args.compose_file])
        
        if hasattr(self.args, 'project_name') and self.args.project_name:
            cmd.extend(['-p', self.args.project_name])
        
        cmd.append('exec')
        
        # 인터랙티브 모드
        if hasattr(self.args, 'interactive') and self.args.interactive:
            cmd.extend(['-it'])
        
        cmd.append(exec_service)
        cmd.extend(exec_command.split())
        
        if hasattr(self.args, 'interactive') and self.args.interactive:
            pawn.console.log("[yellow]Interactive mode - switching to direct subprocess execution[/yellow]")
            # 인터랙티브 모드는 직접 subprocess로 실행
            try:
                subprocess.run(cmd)
            except KeyboardInterrupt:
                pawn.console.log("\n[yellow]Command interrupted by user[/yellow]")
        else:
            result = await self.run_compose_command(cmd, stream_output=True)
            if not result["success"]:
                self.log_error(f"Failed to execute command: {result['stderr']}")
    
    async def compose_config(self, config: ComposeConfig):
        """Compose 설정 검증 및 출력"""
        pawn.console.log("🔍 Validating Docker Compose configuration...")
        
        cmd = self.get_compose_command()
        
        # 프로젝트 이름 및 파일 옵션
        if hasattr(self.args, 'compose_file') and self.args.compose_file:
            cmd.extend(['-f', self.args.compose_file])
        
        if hasattr(self.args, 'project_name') and self.args.project_name:
            cmd.extend(['-p', self.args.project_name])
        
        cmd.append('config')
        
        result = await self.run_compose_command(cmd)
        
        if result["success"]:
            self.log_success("Configuration is valid")
            if result["stdout"]:
                pawn.console.print("[cyan]--- Resolved Configuration ---[/cyan]")
                pawn.console.print(result["stdout"])
        else:
            self.log_error(f"Configuration validation failed: {result['stderr']}")
    
    async def run_async(self) -> int:
        """Docker Compose CLI 실행 (비동기)"""
        self.setup_config()
        self.print_banner()
        
        # Docker Compose 사용 가능 여부 확인
        if not self.check_compose_available():
            self.log_error("Docker Compose is not available. Please install Docker Compose.")
            return 1
        
        # Compose 파일 검증
        if not self.validate_compose_file():
            return 1
        
        config = self.create_config()
        
        try:
            if config.command == "up":
                await self.compose_up(config)
            elif config.command == "down":
                await self.compose_down(config)
            elif config.command == "ps":
                await self.compose_ps(config)
            elif config.command == "logs":
                await self.compose_logs(config)
            elif config.command == "build":
                await self.compose_build(config)
            elif config.command == "pull":
                await self.compose_pull(config)
            elif config.command == "restart":
                await self.compose_restart(config)
            elif config.command == "stop":
                await self.compose_stop(config)
            elif config.command == "start":
                await self.compose_start(config)
            elif config.command == "scale":
                await self.compose_scale(config)
            elif config.command == "exec":
                await self.compose_exec(config)
            elif config.command == "config":
                await self.compose_config(config)
            else:
                self.log_error(f"Unknown command: {config.command}")
                return 1
            
            return 0
            
        except Exception as e:
            self.log_error(f"Command execution failed: {e}")
            return 1


def get_arguments(parser: ArgumentParser):
    """인수 정의 (레거시 호환)"""
    cli = ComposeCLI()
    cli.get_arguments(parser)


def main():
    """메인 함수 (레거시 호환)"""
    cli = ComposeCLI()
    return cli.main()


if __name__ == '__main__':
    import sys
    sys.exit(main())