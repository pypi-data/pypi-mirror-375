"""
PawnStack Docker 도구

Docker 컨테이너 관리 도구
"""

import asyncio
import json
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from argparse import ArgumentParser

from pawnstack import __version__
from pawnstack.config.global_config import pawn
from pawnstack.cli.base import ContainerBaseCLI
from pawnstack.cli.banner import generate_banner

# 모듈 메타데이터
__description__ = 'Command Line Interface for managing Docker containers'

__epilog__ = (
    "This script provides various commands for Docker container management.\n\n"
    "Usage examples:\n"
    "  1. List containers:\n\tpawns docker ls\n\n"
    "  2. Run container:\n\tpawns docker run --name my_app --image nginx\n\n"
    "  3. Stop container:\n\tpawns docker stop --name my_app\n\n"
    "  4. Remove container:\n\tpawns docker rm --name my_app\n\n"
    "For more details, use the -h or --help flag."
)


@dataclass
class DockerConfig:
    """Docker 설정"""
    command: str = "ls"
    name: str = ""
    image: str = ""
    count: int = 1
    force: bool = False
    socket_path: str = "/var/run/docker.sock"


class DockerCLI(ContainerBaseCLI):
    """Docker CLI"""
    
    def __init__(self, args=None):
        super().__init__(args)
    
    def get_arguments(self, parser: ArgumentParser):
        """인수 정의"""
        # 컨테이너 공통 인수 추가
        self.get_common_container_arguments(parser)
        
        parser.add_argument('command', help='Command to execute', 
                          choices=['ls', 'run', 'stop', 'start', 'rm', 'logs', 'inspect', 'stats', 'exec'], 
                          nargs='?', default='ls')
        
        parser.add_argument('-n', '--name', type=str, help='Container name')
        parser.add_argument('-i', '--image', type=str, help='Docker image name')
        parser.add_argument('-c', '--count', type=int, help='Number of containers (default: 1)', default=1)
        parser.add_argument('--force', action='store_true', help='Force operation without confirmation')
        
        # 실행 옵션
        parser.add_argument('-p', '--port', type=str, action='append', help='Port mapping (e.g., 8080:80)')
        parser.add_argument('--volume', type=str, action='append', help='Volume mapping')
        parser.add_argument('-e', '--env', type=str, action='append', help='Environment variables')
        parser.add_argument('--detach', action='store_true', help='Run in detached mode', default=True)
        parser.add_argument('--restart', type=str, choices=['no', 'always', 'unless-stopped', 'on-failure'], 
                          help='Restart policy')
        parser.add_argument('--network', type=str, help='Network to connect to')
        parser.add_argument('--workdir', type=str, help='Working directory inside container')
        parser.add_argument('--user', type=str, help='Username or UID')
        
        # 로그 옵션
        parser.add_argument('--follow', '-f', action='store_true', help='Follow log output')
        parser.add_argument('--tail', type=int, default=50, help='Number of lines to show from end of logs')
        parser.add_argument('--since', type=str, help='Show logs since timestamp')
        
        # exec 옵션
        parser.add_argument('--interactive', '-it', action='store_true', help='Interactive mode')
        parser.add_argument('--exec-command', type=str, default='/bin/bash', help='Command to execute in container')
        
        # 모니터링 옵션
        parser.add_argument('--interval', type=int, default=5, help='Stats update interval (seconds)')
        parser.add_argument('--no-stream', action='store_true', help='Disable streaming stats')
        
        parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                          help='Logging level (default: INFO)', default="INFO")
    
    def setup_config(self):
        """설정 초기화"""
        args = self.args
        app_name = 'docker'
        
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
            app_name="Docker",
            author="PawnStack Team",
            version=__version__,
            font="graffiti"
        )
        print(banner)
    
    def create_config(self) -> DockerConfig:
        """설정 객체 생성"""
        return DockerConfig(
            command=getattr(self.args, 'command', 'ls'),
            name=getattr(self.args, 'name', ''),
            image=getattr(self.args, 'image', ''),
            count=getattr(self.args, 'count', 1),
            force=getattr(self.args, 'force', False),
            socket_path=getattr(self.args, 'socket', '/var/run/docker.sock')
        )
    
    async def list_containers_async(self, config: DockerConfig):
        """컨테이너 목록 조회 (비동기)"""
        pawn.console.log("🐳 Listing Docker containers...")
        
        try:
            docker = await self.get_docker_client()
            containers = await docker.containers.list(all=True)
            
            if not containers:
                pawn.console.log("[yellow]No containers found[/yellow]")
                return
            
            # 테이블 형태로 출력
            from rich.table import Table
            table = Table(title="Docker Containers")
            table.add_column("Name", style="cyan")
            table.add_column("Image", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Ports", style="blue")
            table.add_column("Created", style="dim")
            
            for container in containers:
                container_info = container._container
                names = container_info.get('Names', [])
                name = names[0].lstrip('/') if names else container_info.get('Id', '')[:12]
                image = container_info.get('Image', 'N/A')
                status = container_info.get('Status', 'N/A')
                
                # 포트 정보 처리
                ports = container_info.get('Ports', [])
                port_str = ', '.join([
                    f"{p.get('PublicPort', '')}:{p.get('PrivatePort', '')}" 
                    for p in ports if p.get('PublicPort')
                ]) or 'N/A'
                
                created = container_info.get('Created', 'N/A')
                
                table.add_row(name, image, status, port_str, str(created))
            
            pawn.console.print(table)
            
        except Exception as e:
            self.log_error(f"Failed to list containers: {e}")
    
    async def run_container_async(self, config: DockerConfig):
        """컨테이너 실행 (비동기)"""
        if not config.image:
            self.log_error("Image name is required for run command")
            return
        
        if not config.name:
            config.name = f"{config.image.replace(':', '_').replace('/', '_')}_container"
        
        pawn.console.log(f"🚀 Running container: {config.name} from image: {config.image}")
        
        try:
            docker = await self.get_docker_client()
            
            # 컨테이너 설정 구성
            container_config = {
                'Image': config.image,
                'name': config.name,
                'detach': getattr(self.args, 'detach', True)
            }
            
            # 환경 변수
            if hasattr(self.args, 'env') and self.args.env:
                container_config['environment'] = {}
                for env in self.args.env:
                    if '=' in env:
                        key, value = env.split('=', 1)
                        container_config['environment'][key] = value
            
            # 포트 매핑
            if hasattr(self.args, 'port') and self.args.port:
                container_config['ports'] = {}
                for port in self.args.port:
                    if ':' in port:
                        host_port, container_port = port.split(':', 1)
                        container_config['ports'][f"{container_port}/tcp"] = host_port
            
            # 볼륨 매핑
            if hasattr(self.args, 'volume') and self.args.volume:
                container_config['volumes'] = {}
                for volume in self.args.volume:
                    if ':' in volume:
                        host_path, container_path = volume.split(':', 1)
                        container_config['volumes'][host_path] = {'bind': container_path, 'mode': 'rw'}
            
            # 재시작 정책
            if hasattr(self.args, 'restart') and self.args.restart:
                container_config['restart_policy'] = {'Name': self.args.restart}
            
            # 네트워크
            if hasattr(self.args, 'network') and self.args.network:
                container_config['network'] = self.args.network
            
            # 작업 디렉토리
            if hasattr(self.args, 'workdir') and self.args.workdir:
                container_config['working_dir'] = self.args.workdir
            
            # 사용자
            if hasattr(self.args, 'user') and self.args.user:
                container_config['user'] = self.args.user
            
            if not config.force:
                pawn.console.log(f"🔧 Container config: {json.dumps(container_config, indent=2)}")
                confirm = input("Do you want to proceed? (y/N): ")
                if confirm.lower() != 'y':
                    pawn.console.log("Operation cancelled")
                    return
            
            # 컨테이너 생성 및 시작
            container = await docker.containers.create_or_replace(config.name, container_config)
            await container.start()
            
            self.log_success(f"Container '{config.name}' started successfully")
            
            # 컨테이너 정보 출력
            container_info = await container.show()
            container_id = container_info['Id'][:12]
            pawn.console.log(f"Container ID: {container_id}")
            
        except Exception as e:
            self.log_error(f"Failed to run container: {e}")
    
    async def stop_container_async(self, config: DockerConfig):
        """컨테이너 중지 (비동기)"""
        if not config.name:
            self.log_error("Container name is required for stop command")
            return
        
        pawn.console.log(f"🛑 Stopping container: {config.name}")
        
        try:
            docker = await self.get_docker_client()
            container = await docker.containers.get(config.name)
            await container.stop()
            
            self.log_success(f"Container '{config.name}' stopped successfully")
            
        except Exception as e:
            self.log_error(f"Failed to stop container: {e}")
    
    async def start_container_async(self, config: DockerConfig):
        """컨테이너 시작 (비동기)"""
        if not config.name:
            self.log_error("Container name is required for start command")
            return
        
        pawn.console.log(f"▶️  Starting container: {config.name}")
        
        try:
            docker = await self.get_docker_client()
            container = await docker.containers.get(config.name)
            await container.start()
            
            self.log_success(f"Container '{config.name}' started successfully")
            
        except Exception as e:
            self.log_error(f"Failed to start container: {e}")
    
    async def remove_container_async(self, config: DockerConfig):
        """컨테이너 제거 (비동기)"""
        if not config.name:
            self.log_error("Container name is required for rm command")
            return
        
        pawn.console.log(f"🗑️  Removing container: {config.name}")
        
        if not config.force:
            confirm = input(f"Are you sure you want to remove container '{config.name}'? (y/N): ")
            if confirm.lower() != 'y':
                pawn.console.log("Operation cancelled")
                return
        
        try:
            docker = await self.get_docker_client()
            container = await docker.containers.get(config.name)
            
            # 실행 중인 컨테이너는 먼저 중지
            container_info = await container.show()
            if container_info['State']['Running']:
                await container.stop()
                pawn.console.log("Container stopped before removal")
            
            await container.delete()
            self.log_success(f"Container '{config.name}' removed successfully")
            
        except Exception as e:
            self.log_error(f"Failed to remove container: {e}")
    
    async def show_logs_async(self, config: DockerConfig):
        """컨테이너 로그 조회 (비동기)"""
        if not config.name:
            self.log_error("Container name is required for logs command")
            return
        
        pawn.console.log(f"📋 Showing logs for container: {config.name}")
        
        try:
            docker = await self.get_docker_client()
            container = await docker.containers.get(config.name)
            
            # 로그 옵션 설정
            log_options = {
                'stdout': True,
                'stderr': True,
                'tail': getattr(self.args, 'tail', 50)
            }
            
            if hasattr(self.args, 'since') and self.args.since:
                log_options['since'] = self.args.since
            
            if hasattr(self.args, 'follow') and self.args.follow:
                # 실시간 로그 스트리밍
                pawn.console.log(f"[cyan]--- Following logs for {config.name} (Press Ctrl+C to stop) ---[/cyan]")
                
                async for log_line in container.log(follow=True, **log_options):
                    pawn.console.print(log_line.decode('utf-8').rstrip())
            else:
                # 정적 로그 출력
                logs = await container.log(**log_options)
                if logs:
                    pawn.console.print(f"[cyan]--- Logs for {config.name} ---[/cyan]")
                    for log_line in logs:
                        pawn.console.print(log_line.decode('utf-8').rstrip())
                else:
                    pawn.console.log("[yellow]No logs found[/yellow]")
            
        except KeyboardInterrupt:
            pawn.console.log("\n[yellow]Log streaming stopped by user[/yellow]")
        except Exception as e:
            self.log_error(f"Failed to get logs: {e}")
    
    async def inspect_container_async(self, config: DockerConfig):
        """컨테이너 정보 조회 (비동기)"""
        if not config.name:
            self.log_error("Container name is required for inspect command")
            return
        
        pawn.console.log(f"🔍 Inspecting container: {config.name}")
        
        try:
            docker = await self.get_docker_client()
            container = await docker.containers.get(config.name)
            container_info = await container.show()
            
            pawn.console.print(f"[cyan]--- Container Info for {config.name} ---[/cyan]")
            pawn.console.print(f"ID: {container_info['Id'][:12]}")
            pawn.console.print(f"Image: {container_info['Config']['Image']}")
            pawn.console.print(f"State: {container_info['State']['Status']}")
            pawn.console.print(f"Created: {container_info['Created']}")
            pawn.console.print(f"Started: {container_info['State'].get('StartedAt', 'N/A')}")
            
            # 네트워크 정보
            networks = container_info.get('NetworkSettings', {}).get('Networks', {})
            if networks:
                pawn.console.print("Networks:")
                for net_name, net_info in networks.items():
                    ip = net_info.get('IPAddress', 'N/A')
                    pawn.console.print(f"  {net_name}: {ip}")
            
            # 포트 정보
            ports = container_info.get('NetworkSettings', {}).get('Ports', {})
            if ports:
                pawn.console.print("Port Mappings:")
                for container_port, host_bindings in ports.items():
                    if host_bindings:
                        for binding in host_bindings:
                            host_port = binding.get('HostPort', 'N/A')
                            pawn.console.print(f"  {container_port} -> {host_port}")
            
            # 환경 변수 (일부만 표시)
            env_vars = container_info.get('Config', {}).get('Env', [])
            if env_vars:
                pawn.console.print("Environment Variables (first 10):")
                for env_var in env_vars[:10]:
                    pawn.console.print(f"  {env_var}")
                if len(env_vars) > 10:
                    pawn.console.print(f"  ... and {len(env_vars) - 10} more")
            
        except Exception as e:
            self.log_error(f"Failed to inspect container: {e}")
    
    async def show_stats_async(self, config: DockerConfig):
        """컨테이너 통계 조회 (비동기)"""
        if not config.name:
            self.log_error("Container name is required for stats command")
            return
        
        pawn.console.log(f"📊 Showing stats for container: {config.name}")
        
        try:
            docker = await self.get_docker_client()
            container = await docker.containers.get(config.name)
            
            if hasattr(self.args, 'no_stream') and self.args.no_stream:
                # 단일 통계 조회
                stats = await container.stats(stream=False)
                self._display_stats(config.name, stats)
            else:
                # 실시간 통계 스트리밍
                pawn.console.log(f"[cyan]--- Real-time stats for {config.name} (Press Ctrl+C to stop) ---[/cyan]")
                
                interval = getattr(self.args, 'interval', 5)
                async for stats in container.stats(stream=True):
                    self._display_stats(config.name, stats)
                    await asyncio.sleep(interval)
            
        except KeyboardInterrupt:
            pawn.console.log("\n[yellow]Stats monitoring stopped by user[/yellow]")
        except Exception as e:
            self.log_error(f"Failed to get stats: {e}")
    
    def _display_stats(self, container_name: str, stats: dict):
        """통계 정보 표시"""
        try:
            # CPU 사용률 계산
            cpu_stats = stats.get('cpu_stats', {})
            precpu_stats = stats.get('precpu_stats', {})
            
            cpu_usage = 0.0
            if cpu_stats and precpu_stats:
                cpu_delta = cpu_stats.get('cpu_usage', {}).get('total_usage', 0) - \
                           precpu_stats.get('cpu_usage', {}).get('total_usage', 0)
                system_delta = cpu_stats.get('system_cpu_usage', 0) - \
                              precpu_stats.get('system_cpu_usage', 0)
                
                if system_delta > 0:
                    cpu_usage = (cpu_delta / system_delta) * 100.0
            
            # 메모리 사용률
            memory_stats = stats.get('memory_stats', {})
            memory_usage = memory_stats.get('usage', 0)
            memory_limit = memory_stats.get('limit', 0)
            memory_percent = (memory_usage / memory_limit * 100) if memory_limit > 0 else 0
            
            # 네트워크 I/O
            networks = stats.get('networks', {})
            rx_bytes = sum(net.get('rx_bytes', 0) for net in networks.values())
            tx_bytes = sum(net.get('tx_bytes', 0) for net in networks.values())
            
            # 블록 I/O
            blkio_stats = stats.get('blkio_stats', {})
            io_service_bytes = blkio_stats.get('io_service_bytes_recursive', [])
            read_bytes = sum(item.get('value', 0) for item in io_service_bytes if item.get('op') == 'Read')
            write_bytes = sum(item.get('value', 0) for item in io_service_bytes if item.get('op') == 'Write')
            
            # 출력
            pawn.console.print(f"\n[bold cyan]{container_name}[/bold cyan]")
            pawn.console.print(f"CPU: {cpu_usage:.2f}%")
            pawn.console.print(f"Memory: {memory_usage / 1024 / 1024:.2f}MB / {memory_limit / 1024 / 1024:.2f}MB ({memory_percent:.2f}%)")
            pawn.console.print(f"Network I/O: {rx_bytes / 1024 / 1024:.2f}MB / {tx_bytes / 1024 / 1024:.2f}MB")
            pawn.console.print(f"Block I/O: {read_bytes / 1024 / 1024:.2f}MB / {write_bytes / 1024 / 1024:.2f}MB")
            
        except Exception as e:
            self.log_warning(f"Failed to parse stats: {e}")
    
    async def exec_container_async(self, config: DockerConfig):
        """컨테이너에서 명령어 실행 (비동기)"""
        if not config.name:
            self.log_error("Container name is required for exec command")
            return
        
        exec_command = getattr(self.args, 'exec_command', '/bin/bash')
        pawn.console.log(f"🔧 Executing '{exec_command}' in container: {config.name}")
        
        try:
            docker = await self.get_docker_client()
            container = await docker.containers.get(config.name)
            
            # 컨테이너가 실행 중인지 확인
            container_info = await container.show()
            if not container_info['State']['Running']:
                self.log_error("Container is not running")
                return
            
            # exec 설정
            exec_config = {
                'Cmd': exec_command.split(),
                'AttachStdout': True,
                'AttachStderr': True,
            }
            
            if hasattr(self.args, 'interactive') and self.args.interactive:
                exec_config['AttachStdin'] = True
                exec_config['Tty'] = True
            
            # exec 생성 및 시작
            exec_instance = await container.exec(exec_config)
            
            if hasattr(self.args, 'interactive') and self.args.interactive:
                pawn.console.log("[yellow]Interactive mode not fully supported in async version[/yellow]")
                pawn.console.log("[yellow]Use 'docker exec -it <container> <command>' for full interactive mode[/yellow]")
            
            # 출력 스트리밍
            async for output in exec_instance:
                pawn.console.print(output.decode('utf-8').rstrip())
            
        except Exception as e:
            self.log_error(f"Failed to execute command: {e}")
    
    async def run_async(self) -> int:
        """Docker CLI 실행 (비동기)"""
        self.setup_config()
        self.print_banner()
        
        # Docker 연결 검증
        if not await self.validate_docker_connection():
            return 1
        
        config = self.create_config()
        
        try:
            if config.command == "ls":
                await self.list_containers_async(config)
            elif config.command == "run":
                await self.run_container_async(config)
            elif config.command == "stop":
                await self.stop_container_async(config)
            elif config.command == "start":
                await self.start_container_async(config)
            elif config.command == "rm":
                await self.remove_container_async(config)
            elif config.command == "logs":
                await self.show_logs_async(config)
            elif config.command == "inspect":
                await self.inspect_container_async(config)
            elif config.command == "stats":
                await self.show_stats_async(config)
            elif config.command == "exec":
                await self.exec_container_async(config)
            else:
                self.log_error(f"Unknown command: {config.command}")
                return 1
            
            return 0
            
        except Exception as e:
            self.log_error(f"Command execution failed: {e}")
            return 1


def get_arguments(parser: ArgumentParser):
    """인수 정의 (레거시 호환)"""
    cli = DockerCLI()
    cli.get_arguments(parser)


def main():
    """메인 함수 (레거시 호환)"""
    cli = DockerCLI()
    return cli.main()


if __name__ == '__main__':
    import sys
    sys.exit(main())