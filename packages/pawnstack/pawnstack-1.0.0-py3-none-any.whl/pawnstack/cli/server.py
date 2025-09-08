"""
PawnStack 서버 리소스 확인 도구

서버의 CPU, 메모리, 디스크, 네트워크 상태를 실시간으로 모니터링
"""

import os
import sys
import time
import asyncio
from argparse import ArgumentParser
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.console import Group

from pawnstack import __version__
from pawnstack.config.global_config import pawn
from pawnstack.cli.base import MonitoringBaseCLI
from pawnstack.resource import (
    get_hostname,
    get_mem_info,
    get_load_average,
    get_uptime,
    DiskUsage
)
from pawnstack.resource.system import get_cpu_info, get_process_count
from pawnstack.resource.network import get_network_stats
from pawnstack.resource.disk import get_color_by_threshold

# 모듈 메타데이터
__description__ = "Monitor server resources in real-time"
__epilog__ = "Display real-time information about CPU, memory, disk, and network usage"


class ServerCLI(MonitoringBaseCLI):
    """서버 리소스 모니터링 CLI"""
    
    def get_arguments(self, parser: ArgumentParser):
        """인수 정의"""
        self.get_common_monitoring_arguments(parser)
        
        parser.add_argument(
            '--cpu-only',
            action='store_true',
            help='Show CPU information only'
        )
        
        parser.add_argument(
            '--memory-only',
            action='store_true',
            help='Show memory information only'
        )
        
        parser.add_argument(
            '--disk-only',
            action='store_true',
            help='Show disk information only'
        )
        
        parser.add_argument(
            '--network-only',
            action='store_true',
            help='Show network information only'
        )
        
        parser.add_argument(
            '--no-live',
            action='store_true',
            help='Disable live updating (single snapshot)'
        )
    
    async def run_async(self) -> int:
        """서버 모니터링 실행"""
        if getattr(self.args, 'no_live', False):
            # 단일 스냅샷 모드
            await self.show_snapshot()
        else:
            # 실시간 모니터링 모드
            await self.start_live_monitoring()
        
        return 0
    
    async def show_snapshot(self):
        """단일 스냅샷 표시"""
        layout = self.create_layout()
        pawn.console.print(layout)
    
    async def start_live_monitoring(self):
        """실시간 모니터링 시작"""
        interval = getattr(self.args, 'interval', 5)
        duration = getattr(self.args, 'duration', None)
        
        self.log_info(f"Starting server monitoring (interval: {interval}s)")
        
        with Live(self.create_layout(), refresh_per_second=1/interval, screen=True) as live:
            start_time = time.time()
            
            try:
                while True:
                    live.update(self.create_layout())
                    
                    if duration and (time.time() - start_time) >= duration:
                        break
                    
                    await asyncio.sleep(interval)
                    
            except KeyboardInterrupt:
                self.log_info("Monitoring stopped by user")
    
    def create_layout(self) -> Layout:
        """레이아웃 생성"""
        layout = Layout()
        
        # 헤더
        header = Panel(
            f"[bold cyan]Server Resource Monitor[/bold cyan] - {get_hostname()} - {time.strftime('%Y-%m-%d %H:%M:%S')}",
            style="blue"
        )
        
        # 메인 컨텐츠
        content_panels = []
        
        # 특정 패널만 표시하는 옵션이 있는지 확인
        any_only_option = any([
            getattr(self.args, 'cpu_only', False),
            getattr(self.args, 'memory_only', False),
            getattr(self.args, 'disk_only', False),
            getattr(self.args, 'network_only', False)
        ])
        
        if any_only_option:
            # 특정 패널만 표시
            show_cpu = getattr(self.args, 'cpu_only', False)
            show_memory = getattr(self.args, 'memory_only', False)
            show_disk = getattr(self.args, 'disk_only', False)
            show_network = getattr(self.args, 'network_only', False)
        else:
            # 모든 패널 표시 (기본값)
            show_cpu = True
            show_memory = True
            show_disk = True
            show_network = True
        
        if show_cpu:
            content_panels.append(self.create_cpu_panel())
        
        if show_memory:
            content_panels.append(self.create_memory_panel())
        
        if show_disk:
            content_panels.append(self.create_disk_panel())
        
        if show_network:
            content_panels.append(self.create_network_panel())
        
        # 레이아웃 구성
        main_content = Group(*content_panels)
        
        layout.split_column(
            Layout(header, size=3),
            Layout(main_content)
        )
        
        return layout
    
    def create_cpu_panel(self) -> Panel:
        """CPU 패널 생성"""
        cpu_info = get_cpu_info()
        load_avg = get_load_average()
        uptime = get_uptime()
        process_count = get_process_count()
        
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        if 'error' not in cpu_info:
            table.add_row("Physical Cores", str(cpu_info.get('physical_cores', 'N/A')))
            table.add_row("Logical Cores", str(cpu_info.get('logical_cores', 'N/A')))
            
            cpu_percent = cpu_info.get('cpu_percent', 0)
            cpu_color = get_color_by_threshold(cpu_percent)
            table.add_row("CPU Usage", f"[{cpu_color}]{cpu_percent}%[/{cpu_color}]")
            
            if cpu_info.get('cpu_freq'):
                freq = cpu_info['cpu_freq']
                table.add_row("CPU Frequency", f"{freq.get('current', 0):.0f} MHz")
        
        table.add_row("Load Average", load_avg)
        table.add_row("Uptime", uptime)
        table.add_row("Processes", str(process_count))
        
        return Panel(table, title="[bold green]CPU Information[/bold green]", border_style="green")
    
    def create_memory_panel(self) -> Panel:
        """메모리 패널 생성"""
        mem_info = get_mem_info()
        
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        if 'error' not in mem_info:
            total = mem_info.get('mem_total', 0)
            used = mem_info.get('mem_used', 0)
            available = mem_info.get('mem_available', 0)
            percent = mem_info.get('mem_percent', 0)
            
            mem_color = get_color_by_threshold(percent)
            
            table.add_row("Total Memory", f"{total:.2f} GB")
            table.add_row("Used Memory", f"[{mem_color}]{used:.2f} GB[/{mem_color}]")
            table.add_row("Available Memory", f"{available:.2f} GB")
            table.add_row("Memory Usage", f"[{mem_color}]{percent:.1f}%[/{mem_color}]")
        else:
            table.add_row("Error", mem_info['error'])
        
        return Panel(table, title="[bold blue]Memory Information[/bold blue]", border_style="blue")
    
    def create_disk_panel(self) -> Panel:
        """디스크 패널 생성"""
        disk_usage = DiskUsage()
        disk_info = disk_usage.get_disk_usage("/", unit="GB")
        
        table = Table(show_header=True, box=None)
        table.add_column("Mount Point", style="cyan", no_wrap=True)
        table.add_column("Used", style="white", justify="right")
        table.add_column("Total", style="white", justify="right")
        table.add_column("Usage", style="white", justify="right")
        
        if "/" in disk_info and 'error' not in disk_info["/"]:
            info = disk_info["/"]
            color = get_color_by_threshold(info['percent'])
            
            table.add_row(
                "/",
                f"[{color}]{info['used']:.1f} GB[/{color}]",
                f"{info['total']:.1f} GB",
                f"[{color}]{info['percent']:.1f}%[/{color}]"
            )
        
        # 추가 마운트 포인트들
        all_disks = disk_usage.get_disk_usage("all", unit="GB")
        for mount_point, info in list(all_disks.items())[:3]:  # 상위 3개만 표시
            if mount_point != "/" and 'error' not in info:
                color = get_color_by_threshold(info['percent'])
                table.add_row(
                    mount_point[:20] + "..." if len(mount_point) > 20 else mount_point,
                    f"[{color}]{info['used']:.1f} GB[/{color}]",
                    f"{info['total']:.1f} GB",
                    f"[{color}]{info['percent']:.1f}%[/{color}]"
                )
        
        return Panel(table, title="[bold yellow]Disk Usage[/bold yellow]", border_style="yellow")
    
    def create_network_panel(self) -> Panel:
        """네트워크 패널 생성"""
        net_stats = get_network_stats()
        
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        if 'error' not in net_stats:
            # 바이트를 MB로 변환
            bytes_sent_mb = net_stats.get('bytes_sent', 0) / (1024**2)
            bytes_recv_mb = net_stats.get('bytes_recv', 0) / (1024**2)
            
            table.add_row("Bytes Sent", f"{bytes_sent_mb:.2f} MB")
            table.add_row("Bytes Received", f"{bytes_recv_mb:.2f} MB")
            table.add_row("Packets Sent", str(net_stats.get('packets_sent', 0)))
            table.add_row("Packets Received", str(net_stats.get('packets_recv', 0)))
            
            if net_stats.get('errin', 0) > 0 or net_stats.get('errout', 0) > 0:
                table.add_row("Errors In", f"[red]{net_stats.get('errin', 0)}[/red]")
                table.add_row("Errors Out", f"[red]{net_stats.get('errout', 0)}[/red]")
        else:
            table.add_row("Error", net_stats['error'])
        
        return Panel(table, title="[bold magenta]Network Statistics[/bold magenta]", border_style="magenta")


def get_arguments(parser: ArgumentParser):
    """인수 정의 (레거시 호환)"""
    cli = ServerCLI()
    cli.get_arguments(parser)


def main():
    """메인 함수 (레거시 호환)"""
    cli = ServerCLI()
    return cli.main()


if __name__ == '__main__':
    sys.exit(main())