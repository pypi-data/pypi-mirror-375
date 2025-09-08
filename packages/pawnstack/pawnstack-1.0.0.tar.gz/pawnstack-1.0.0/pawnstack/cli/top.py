"""
PawnStack Top 도구

실시간 시스템 리소스 모니터링 with Rich display
"""

import os
import sys
import time
import asyncio
import psutil
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from argparse import ArgumentParser
from datetime import datetime

from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.align import Align
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

from pawnstack import __version__
from pawnstack.cli.base import AsyncBaseCLI
from pawnstack.config.global_config import pawn
from pawnstack.resource import system, network, disk
# shorten_text is defined locally in this file

# 모듈 메타데이터
__description__ = 'A simple and powerful tool for monitoring server resources in real time.'

__epilog__ = (
    "This tool is a comprehensive solution for monitoring your server's resource usage. \n\n"
    "Features include real-time tracking of network traffic, CPU, memory, and disk usage, \n"
    "making it an indispensable tool for system administrators and DevOps professionals.\n\n"
    "Here are some usage examples to get you started:\n\n"
    "  1. **Basic Monitoring:** Monitor system resources with default settings. \n"
    "     Example: `pawns top`\n\n"
    "  2. **Detailed View:** Use `-v` to increase verbosity and get more detailed logs.\n"
    "     Example: `pawns top -v`\n\n"
    "  3. **Minimal Output:** Use `-q` for quiet mode to suppress standard output.\n"
    "     Example: `pawns top -q`\n\n"
    "  4. **Custom Update Interval:** Adjust the refresh rate with `-i` to set the interval in seconds.\n"
    "     Example: `pawns top -i 5`\n\n"
    "  5. **Output Formats:** Choose between 'live' and 'line' output styles with `-t`.\n"
    "     Example: `pawns top -t live`\n\n"
    "  6. **Network-Specific Monitoring:** Focus solely on network traffic and protocols.\n"
    "     Example: `pawns top net`\n\n"
    "  7. **Advanced Filters:** Use advanced options to filter processes by PID, name, or network protocols.\n"
    "     Example: `pawns top proc --pid-filter 1234 --protocols tcp udp`\n\n"
    "  8. **Show Full Command Lines:** Display full command lines instead of just process names.\n"
    "     Example: `pawns top --show-cmdline`\n\n"
    "Key options:\n"
    "  --top-n              Specify the number of top processes to display.\n"
    "  --show-cmdline       Show full command line instead of just process name.\n"
    "  --unit               Choose the unit for network traffic (e.g., Mbps, Gbps).\n"
    "  --group-by           Group processes by PID or name.\n\n"
    "This flexibility allows you to tailor the tool to your specific needs. \n"
    "For more detailed usage, run `--help` or refer to the documentation."
)


@dataclass
class TopConfig:
    """Top 명령어 설정"""
    command: str = "resource"
    interval: float = 1.0
    print_type: str = "live"
    top_n: int = 10
    group_by: str = "pid"
    unit: str = "Mbps"
    protocols: list = None
    pid_filter: list = None
    proc_filter: list = None
    min_bytes_threshold: int = 0
    verbose: int = 1
    show_cmdline: bool = False

    def __post_init__(self):
        if self.protocols is None:
            self.protocols = ["tcp", "udp"]


@dataclass
class SystemStats:
    """시스템 통계"""
    timestamp: float
    cpu_percent: float
    cpu_freq: float
    memory_percent: float
    memory_used: float
    memory_total: float
    disk_percent: float
    disk_used: float
    disk_total: float
    net_bytes_sent: int
    net_bytes_recv: int
    net_packets_sent: int
    net_packets_recv: int
    disk_read_bytes: int
    disk_write_bytes: int
    load_average: Tuple[float, float, float]
    process_count: int
    uptime: float


class TopCLI(AsyncBaseCLI):
    """Top CLI - 실시간 시스템 모니터링"""

    def __init__(self, args=None):
        super().__init__(args)
        self.prev_stats = None
        self.prev_net_io = None
        self.prev_disk_io = None
        self.console = Console()
        self.config = None
        self.start_time = time.time()
        # History tracking for graphs
        self.cpu_history = []
        self.mem_history = []
        self.net_in_history = []
        self.net_out_history = []
        self.disk_read_history = []
        self.disk_write_history = []
        self.max_history = 60  # Keep last 60 data points

    def get_arguments(self, parser: ArgumentParser):
        """인수 정의"""
        parser.add_argument('command', help='Command to execute (resource, net, proc)',
                          type=str, nargs='?', default="resource")

        parser.add_argument('-v', '--verbose', action='count', help='Increase verbosity', default=1)
        parser.add_argument('-q', '--quiet', action='count', help='Quiet mode', default=0)
        parser.add_argument('-i', '--interval', type=float, help='Refresh interval in seconds', default=1.0)
        parser.add_argument('-t', '--print-type', type=str, help='Output type',
                          default="line", choices=["live", "layout", "line"])

        # 모니터링 옵션
        parser.add_argument('--top-n', type=int, default=15,
                          help='Number of top processes to display')
        parser.add_argument('--group-by', type=str, default="pid", choices=["pid", "name"],
                          help='Group processes by pid or name')
        parser.add_argument('--unit', type=str, default="Mbps",
                          choices=['bps', 'Kbps', 'Mbps', 'Gbps', 'Tbps', 'Pbps'],
                          help='Unit for network traffic')
        parser.add_argument('--protocols', nargs='+', default=["tcp", "udp"],
                          help='Protocols to monitor')
        parser.add_argument('--pid-filter', type=int, nargs='*',
                          help='Filter by specific process IDs')
        parser.add_argument('--proc-filter', type=str, nargs='*',
                          help='Filter processes by name')
        parser.add_argument('--min-bytes-threshold', type=int, default=0,
                          help='Minimum bytes threshold for display')
        parser.add_argument('--show-cmdline', action='store_true', default=False,
                          help='Show full command line instead of just process name')

    def create_config(self) -> TopConfig:
        """설정 객체 생성"""
        return TopConfig(
            command=getattr(self.args, 'command', 'resource'),
            interval=getattr(self.args, 'interval', 1.0),
            print_type=getattr(self.args, 'print_type', 'live'),
            top_n=getattr(self.args, 'top_n', 10),
            group_by=getattr(self.args, 'group_by', 'pid'),
            unit=getattr(self.args, 'unit', 'Mbps'),
            protocols=getattr(self.args, 'protocols', ['tcp', 'udp']),
            pid_filter=getattr(self.args, 'pid_filter', None),
            proc_filter=getattr(self.args, 'proc_filter', None),
            min_bytes_threshold=getattr(self.args, 'min_bytes_threshold', 0),
            verbose=getattr(self.args, 'verbose', 1),
            show_cmdline=getattr(self.args, 'show_cmdline', False)
        )

    def get_color_by_percent(self, percent: float) -> str:
        """퍼센트에 따른 색상 결정"""
        if percent is None:
            return "white"
        if percent < 50:
            return "green"
        elif percent < 70:
            return "yellow"
        elif percent < 85:
            return "bright_yellow"
        elif percent < 95:
            return "red"
        else:
            return "bright_red"

    def apply_value_color(self, key: str, value: str, raw_value: float, cores: int = 1) -> str:
        """값에 색상 적용 (레거시 스타일)"""
        try:
            if key == "usr":
                if raw_value > 80:
                    return f"[red]{value}[/red]"
                elif raw_value > 60:
                    return f"[yellow]{value}[/yellow]"
                else:
                    return f"[green]{value}[/green]"
            elif key == "sys":
                if raw_value > 20:
                    return f"[red]{value}[/red]"
                elif raw_value > 10:
                    return f"[yellow]{value}[/yellow]"
                else:
                    return f"[green]{value}[/green]"
            elif key == "mem":
                if raw_value > 80:
                    return f"[red]{value}[/red]"
                elif raw_value > 60:
                    return f"[yellow]{value}[/yellow]"
                else:
                    return f"[green]{value}[/green]"
            elif key == "load":
                if raw_value > cores * 2:
                    return f"[red]{value}[/red]"
                elif raw_value > cores:
                    return f"[yellow]{value}[/yellow]"
                else:
                    return f"[green]{value}[/green]"
            elif key == "io":
                if raw_value > 10:
                    return f"[red]{value}[/red]"
                elif raw_value > 5:
                    return f"[yellow]{value}[/yellow]"
                else:
                    return f"[green]{value}[/green]"
            else:
                return value
        except (ValueError, AttributeError):
            return value

    def format_bytes(self, bytes_value: int, unit: str = "MB") -> str:
        """바이트를 지정된 단위로 변환"""
        units = {
            "B": 1,
            "KB": 1024,
            "MB": 1024 * 1024,
            "GB": 1024 * 1024 * 1024,
            "TB": 1024 * 1024 * 1024 * 1024
        }

        if unit not in units:
            unit = "MB"

        value = bytes_value / units[unit]
        return f"{value:.2f} {unit}"

    def format_network_speed(self, bytes_per_sec: float) -> str:
        """네트워크 속도 포맷"""
        unit = self.config.unit if self.config else "Mbps"

        units = {
            "bps": 8,
            "Kbps": 8 / 1024,
            "Mbps": 8 / (1024 * 1024),
            "Gbps": 8 / (1024 * 1024 * 1024),
            "Tbps": 8 / (1024 * 1024 * 1024 * 1024),
            "Pbps": 8 / (1024 * 1024 * 1024 * 1024 * 1024)
        }

        multiplier = units.get(unit, units["Mbps"])
        value = bytes_per_sec * multiplier

        # 색상 적용
        if value < 10:
            color = "green"
        elif value < 100:
            color = "yellow"
        elif value < 500:
            color = "bright_yellow"
        else:
            color = "red"

        return f"[{color}]{value:.2f} {unit}[/{color}]"

    async def collect_system_stats(self) -> SystemStats:
        """시스템 통계 수집"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_freq = psutil.cpu_freq()
        memory = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')
        net_io = psutil.net_io_counters()
        disk_io = psutil.disk_io_counters()

        # Load average (Unix 시스템만)
        try:
            load_avg = os.getloadavg()
        except:
            load_avg = (0, 0, 0)

        # Uptime
        boot_time = psutil.boot_time()
        uptime = time.time() - boot_time

        return SystemStats(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            cpu_freq=cpu_freq.current if cpu_freq else 0,
            memory_percent=memory.percent,
            memory_used=memory.used,
            memory_total=memory.total,
            disk_percent=disk_usage.percent,
            disk_used=disk_usage.used,
            disk_total=disk_usage.total,
            net_bytes_sent=net_io.bytes_sent,
            net_bytes_recv=net_io.bytes_recv,
            net_packets_sent=net_io.packets_sent,
            net_packets_recv=net_io.packets_recv,
            disk_read_bytes=disk_io.read_bytes if disk_io else 0,
            disk_write_bytes=disk_io.write_bytes if disk_io else 0,
            load_average=load_avg,
            process_count=len(psutil.pids()),
            uptime=uptime
        )

    def create_header_panel(self, stats: SystemStats) -> Panel:
        """헤더 패널 생성"""
        hostname = os.uname().nodename
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uptime_hours = stats.uptime / 3600

        header_text = Text()
        header_text.append(f"🖥️  {hostname} ", style="bold cyan")
        header_text.append(f"| {current_time} ", style="white")
        header_text.append(f"| Uptime: {uptime_hours:.1f}h ", style="green")
        header_text.append(f"| Processes: {stats.process_count}", style="yellow")

        return Panel(
            Align.center(header_text),
            title="[bold white]PawnStack System Monitor[/bold white]",
            border_style="bright_blue",
            box=box.DOUBLE
        )

    def create_cpu_panel(self, stats: SystemStats, include_history: bool = False) -> Panel:
        """CPU 패널 생성"""
        table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE)
        table.add_column("Metric", style="white", width=15)
        table.add_column("Value", style="white")
        table.add_column("Graph", width=40)

        # CPU 사용률
        cpu_color = self.get_color_by_percent(stats.cpu_percent)
        cpu_bar = self.create_bar(stats.cpu_percent, 100, 40)
        table.add_row(
            "CPU Usage",
            f"[{cpu_color}]{stats.cpu_percent:.1f}%[/{cpu_color}]",
            cpu_bar
        )

        # CPU 주파수
        if stats.cpu_freq > 0:
            table.add_row(
                "CPU Frequency",
                f"{stats.cpu_freq:.0f} MHz",
                ""
            )

        # Load Average
        load_colors = []
        cpu_count = psutil.cpu_count()
        for load in stats.load_average:
            load_ratio = (load / cpu_count) * 100
            load_colors.append(self.get_color_by_percent(load_ratio))

        table.add_row(
            "Load Average",
            f"[{load_colors[0]}]{stats.load_average[0]:.2f}[/{load_colors[0]}] "
            f"[{load_colors[1]}]{stats.load_average[1]:.2f}[/{load_colors[1]}] "
            f"[{load_colors[2]}]{stats.load_average[2]:.2f}[/{load_colors[2]}]",
            ""
        )

        # CPU Cores
        table.add_row(
            "CPU Cores",
            f"{psutil.cpu_count(logical=False)} physical, {psutil.cpu_count()} logical",
            ""
        )

        # Add CPU history graph if requested
        if include_history and self.cpu_history:
            sparkline = self.create_sparkline(self.cpu_history, width=35)
            avg_cpu = sum(self.cpu_history) / len(self.cpu_history) if self.cpu_history else 0
            table.add_row(
                "CPU Trend",
                f"Avg: {avg_cpu:.1f}%",
                sparkline
            )

        return Panel(
            table,
            title="[bold cyan]🔲 CPU Information[/bold cyan]",
            border_style="cyan"
        )

    def create_memory_panel(self, stats: SystemStats, include_history: bool = False) -> Panel:
        """메모리 패널 생성"""
        table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
        table.add_column("Metric", style="white", width=15)
        table.add_column("Value", style="white")
        table.add_column("Graph", width=40)

        # 메모리 사용률
        mem_color = self.get_color_by_percent(stats.memory_percent)
        mem_bar = self.create_bar(stats.memory_percent, 100, 40)
        table.add_row(
            "Memory Usage",
            f"[{mem_color}]{stats.memory_percent:.1f}%[/{mem_color}]",
            mem_bar
        )

        # 메모리 상세
        table.add_row(
            "Used / Total",
            f"{self.format_bytes(stats.memory_used, 'GB')} / {self.format_bytes(stats.memory_total, 'GB')}",
            ""
        )

        # Swap 정보
        swap = psutil.swap_memory()
        swap_color = self.get_color_by_percent(swap.percent)
        swap_bar = self.create_bar(swap.percent, 100, 40)
        table.add_row(
            "Swap Usage",
            f"[{swap_color}]{swap.percent:.1f}%[/{swap_color}]",
            swap_bar
        )

        # Add memory history graph if requested
        if include_history and self.mem_history:
            sparkline = self.create_sparkline(self.mem_history, width=35)
            avg_mem = sum(self.mem_history) / len(self.mem_history) if self.mem_history else 0
            table.add_row(
                "Memory Trend",
                f"Avg: {avg_mem:.1f}%",
                sparkline
            )

        return Panel(
            table,
            title="[bold magenta]💾 Memory Information[/bold magenta]",
            border_style="magenta"
        )

    def create_disk_panel(self, stats: SystemStats) -> Panel:
        """디스크 패널 생성"""
        table = Table(show_header=True, header_style="bold yellow", box=box.SIMPLE)
        table.add_column("Metric", style="white", width=15)
        table.add_column("Value", style="white")
        table.add_column("Graph", width=40)

        # 디스크 사용률
        disk_color = self.get_color_by_percent(stats.disk_percent)
        disk_bar = self.create_bar(stats.disk_percent, 100, 40)
        table.add_row(
            "Disk Usage (/)",
            f"[{disk_color}]{stats.disk_percent:.1f}%[/{disk_color}]",
            disk_bar
        )

        # 디스크 상세
        table.add_row(
            "Used / Total",
            f"{self.format_bytes(stats.disk_used, 'GB')} / {self.format_bytes(stats.disk_total, 'GB')}",
            ""
        )

        # I/O 통계
        if self.prev_disk_io:
            read_speed = stats.disk_read_bytes - self.prev_disk_io[0]
            write_speed = stats.disk_write_bytes - self.prev_disk_io[1]

            table.add_row(
                "Disk I/O",
                f"R: {self.format_bytes(read_speed, 'MB')}/s  W: {self.format_bytes(write_speed, 'MB')}/s",
                ""
            )

        self.prev_disk_io = (stats.disk_read_bytes, stats.disk_write_bytes)

        return Panel(
            table,
            title="[bold yellow]💿 Disk Information[/bold yellow]",
            border_style="yellow"
        )

    def create_network_panel(self, stats: SystemStats, include_history: bool = False) -> Panel:
        """네트워크 패널 생성"""
        table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
        table.add_column("Metric", style="white", width=15)
        table.add_column("Value", style="white")

        # 네트워크 속도 계산
        if self.prev_net_io:
            time_delta = stats.timestamp - self.prev_stats.timestamp if self.prev_stats else 1
            bytes_sent_speed = (stats.net_bytes_sent - self.prev_net_io[0]) / time_delta
            bytes_recv_speed = (stats.net_bytes_recv - self.prev_net_io[1]) / time_delta
            packets_sent_speed = (stats.net_packets_sent - self.prev_net_io[2]) / time_delta
            packets_recv_speed = (stats.net_packets_recv - self.prev_net_io[3]) / time_delta

            table.add_row(
                "Upload Speed",
                self.format_network_speed(bytes_sent_speed)
            )

            table.add_row(
                "Download Speed",
                self.format_network_speed(bytes_recv_speed)
            )

            table.add_row(
                "Packets/s",
                f"↑ {packets_sent_speed:.0f} / ↓ {packets_recv_speed:.0f}"
            )

        # 총 전송량
        table.add_row(
            "Total Sent",
            self.format_bytes(stats.net_bytes_sent, 'GB')
        )

        table.add_row(
            "Total Received",
            self.format_bytes(stats.net_bytes_recv, 'GB')
        )

        self.prev_net_io = (
            stats.net_bytes_sent,
            stats.net_bytes_recv,
            stats.net_packets_sent,
            stats.net_packets_recv
        )

        # Add network history graphs if requested
        if include_history:
            if self.net_in_history:
                table.add_row(
                    "Download History",
                    "",
                    ""
                )
                sparkline = self.create_sparkline(self.net_in_history, width=40, height=1)
                table.add_row(
                    "",
                    f"Last {len(self.net_in_history)} samples",
                    sparkline
                )

            if self.net_out_history:
                table.add_row(
                    "Upload History",
                    "",
                    ""
                )
                sparkline = self.create_sparkline(self.net_out_history, width=40, height=1)
                table.add_row(
                    "",
                    f"Last {len(self.net_out_history)} samples",
                    sparkline
                )

        return Panel(
            table,
            title="[bold green]🌐 Network Information[/bold green]",
            border_style="green"
        )

    def create_process_table(self) -> Panel:
        """프로세스 테이블 생성"""
        table = Table(show_header=True, header_style="bold bright_cyan", box=box.SIMPLE)
        table.add_column("PID", style="cyan", width=8)

        # show_cmdline 옵션에 따라 컬럼 너비 조정
        name_width = 45 if self.config and self.config.show_cmdline else 40
        table.add_column("Name", style="white", width=name_width)

        table.add_column("CPU%", style="yellow", width=8)
        table.add_column("MEM%", style="magenta", width=8)
        table.add_column("RSS", style="blue", width=10)  # 실제 메모리 사용량
        table.add_column("CPU Time", style="cyan", width=10)  # CPU 시간
        table.add_column("Status", style="green", width=10)

        # 프로세스 정보 수집 - cmdline 추가
        processes = []
        info_fields = ['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'memory_info', 'cpu_times']
        if self.config and self.config.show_cmdline:
            info_fields.append('cmdline')

        for proc in psutil.process_iter(info_fields):
            try:
                pinfo = proc.info

                # 필터 적용
                if self.config and self.config.pid_filter:
                    if pinfo['pid'] not in self.config.pid_filter:
                        continue

                if self.config and self.config.proc_filter:
                    if not any(f in pinfo['name'] for f in self.config.proc_filter):
                        continue

                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # CPU 사용률 기준 정렬 (None 값 처리)
        processes.sort(key=lambda x: x.get('cpu_percent') or 0, reverse=True)

        # 상위 N개만 표시
        top_n = self.config.top_n if self.config else 15  # 기본값을 15로 증가
        for proc in processes[:top_n]:
            cpu_val = proc.get('cpu_percent') or 0
            mem_val = proc.get('memory_percent') or 0
            cpu_color = self.get_color_by_percent(cpu_val * 10)
            mem_color = self.get_color_by_percent(mem_val * 10)

            # 프로세스 이름 또는 명령줄 표시
            if self.config and self.config.show_cmdline:
                cmdline = proc.get('cmdline', [])
                if cmdline:
                    # 명령줄 인자들을 공백으로 연결
                    display_name = ' '.join(cmdline)
                else:
                    display_name = proc.get('name', '')
                name_width = 45
            else:
                display_name = proc.get('name', '')
                name_width = 40

            # 메모리 정보 (RSS - Resident Set Size)
            memory_info = proc.get('memory_info')
            if memory_info:
                rss_mb = memory_info.rss / 1024 / 1024  # bytes to MB
                rss_str = f"{rss_mb:.1f}M"
            else:
                rss_str = "N/A"

            # CPU 시간
            cpu_times = proc.get('cpu_times')
            if cpu_times:
                total_time = cpu_times.user + cpu_times.system
                hours = int(total_time // 3600)
                minutes = int((total_time % 3600) // 60)
                seconds = int(total_time % 60)
                if hours > 0:
                    cpu_time_str = f"{hours}h{minutes:02d}m"
                elif minutes > 0:
                    cpu_time_str = f"{minutes}m{seconds:02d}s"
                else:
                    cpu_time_str = f"{seconds}s"
            else:
                cpu_time_str = "N/A"

            table.add_row(
                str(proc.get('pid', '')),
                shorten_text(display_name, name_width),
                f"[{cpu_color}]{cpu_val:.1f}[/{cpu_color}]",
                f"[{mem_color}]{mem_val:.1f}[/{mem_color}]",
                rss_str,
                cpu_time_str,
                proc.get('status', '')
            )

        return Panel(
            table,
            title=f"[bold bright_cyan]📊 Top {top_n} Processes (by CPU)[/bold bright_cyan]",
            border_style="bright_cyan"
        )

    def create_bar(self, value: float, max_value: float, width: int) -> str:
        """진행 바 생성"""
        if value is None or max_value is None:
            return f"[white]{'░' * width}[/white]"
        if max_value == 0:
            ratio = 0
        else:
            ratio = min(value / max_value, 1.0)

        filled_width = int(ratio * width)
        empty_width = width - filled_width

        # 색상 결정
        color = self.get_color_by_percent(value)

        bar = f"[{color}]{'█' * filled_width}{'░' * empty_width}[/{color}]"
        return bar

    def create_sparkline(self, data: List[float], width: int = 40, height: int = 1) -> str:
        """스파크라인 히스토그램 생성"""
        if not data:
            return "No data"

        # 스파크라인 문자셋
        spark_chars = "▁▂▃▄▅▆▇█"

        # 데이터 정규화 (0-7 범위로)
        min_val = min(data)
        max_val = max(data)

        if max_val == min_val:
            normalized = [4] * len(data)  # 중간값
        else:
            normalized = [
                int((val - min_val) / (max_val - min_val) * 7)
                for val in data
            ]

        # 너비에 맞춰 데이터 샘플링
        if len(data) > width:
            # 다운샘플링
            step = len(data) / width
            sampled = []
            for i in range(width):
                idx = int(i * step)
                sampled.append(normalized[idx])
            normalized = sampled

        # 스파크라인 생성
        sparkline = ""
        for val in normalized:
            # 값에 따른 색상 적용
            percent = (val / 7) * 100
            color = self.get_color_by_percent(percent)
            sparkline += f"[{color}]{spark_chars[val]}[/{color}]"

        # 최소/최대값 표시
        return f"{sparkline} [{min_val:.1f}-{max_val:.1f}]"

    def create_ascii_graph(self, data: List[float], width: int = 60, height: int = 5, label: str = "") -> str:
        """멀티라인 ASCII 그래프 생성"""
        if not data or height < 2:
            return "No data"

        # 데이터 샘플링
        if len(data) > width:
            step = len(data) / width
            sampled = []
            for i in range(width):
                idx = int(i * step)
                sampled.append(data[idx])
            data = sampled
        elif len(data) < width:
            # 데이터가 너비보다 적으면 패딩
            data = data + [data[-1] if data else 0] * (width - len(data))

        # 최소/최대값 계산
        min_val = min(data) if data else 0
        max_val = max(data) if data else 0

        if max_val == min_val:
            max_val = min_val + 1  # 0으로 나누기 방지

        # 그래프 생성
        graph_lines = []

        # Y축 라벨과 그래프 생성
        for h in range(height, 0, -1):
            line = ""
            threshold = min_val + (max_val - min_val) * (h - 1) / (height - 1)

            # Y축 라벨
            if h == height:
                y_label = f"{max_val:6.1f}│"
            elif h == 1:
                y_label = f"{min_val:6.1f}│"
            else:
                y_label = "      │"

            line = y_label

            # 데이터 포인트 그리기
            for val in data:
                normalized_val = (val - min_val) / (max_val - min_val) * (height - 1)

                if normalized_val >= h - 1:
                    # 값에 따른 색상 적용
                    percent = (val - min_val) / (max_val - min_val) * 100
                    color = self.get_color_by_percent(percent)
                    line += f"[{color}]█[/{color}]"
                else:
                    line += " "

            graph_lines.append(line)

        # X축 그리기
        graph_lines.append("      └" + "─" * width)

        # 라벨 추가
        if label:
            graph_lines.append(f"       {label}")

        return "\n".join(graph_lines)

    def update_history(self, stats: SystemStats):
        """히스토리 데이터 업데이트"""
        # CPU 히스토리
        self.cpu_history.append(stats.cpu_percent)
        if len(self.cpu_history) > self.max_history:
            self.cpu_history.pop(0)

        # 메모리 히스토리
        self.mem_history.append(stats.memory_percent)
        if len(self.mem_history) > self.max_history:
            self.mem_history.pop(0)

        # 네트워크 히스토리 (속도 계산)
        if self.prev_net_io:
            time_delta = stats.timestamp - self.prev_stats.timestamp if self.prev_stats else 1
            if time_delta > 0:
                bytes_in_speed = (stats.net_bytes_recv - self.prev_net_io[1]) / time_delta / (1024 * 1024)  # MB/s
                bytes_out_speed = (stats.net_bytes_sent - self.prev_net_io[0]) / time_delta / (1024 * 1024)  # MB/s

                self.net_in_history.append(bytes_in_speed)
                self.net_out_history.append(bytes_out_speed)

                if len(self.net_in_history) > self.max_history:
                    self.net_in_history.pop(0)
                if len(self.net_out_history) > self.max_history:
                    self.net_out_history.pop(0)

        # 디스크 히스토리
        if self.prev_disk_io:
            time_delta = stats.timestamp - self.prev_stats.timestamp if self.prev_stats else 1
            if time_delta > 0:
                disk_read_speed = (stats.disk_read_bytes - self.prev_disk_io[0]) / time_delta / (1024 * 1024)  # MB/s
                disk_write_speed = (stats.disk_write_bytes - self.prev_disk_io[1]) / time_delta / (1024 * 1024)  # MB/s

                self.disk_read_history.append(disk_read_speed)
                self.disk_write_history.append(disk_write_speed)

                if len(self.disk_read_history) > self.max_history:
                    self.disk_read_history.pop(0)
                if len(self.disk_write_history) > self.max_history:
                    self.disk_write_history.pop(0)

    def create_resource_layout(self, stats: SystemStats, include_history: bool = False) -> Layout:
        """리소스 모니터링 레이아웃 생성"""
        layout = Layout()

        # 히스토리 포함 시 레이아웃 조정
        if include_history:
            # 메인 레이아웃 분할 (히스토리 포함)
            layout.split(
                Layout(name="header", size=4),
                Layout(name="body", size=25),  # 상단 패널 크기 축소
                Layout(name="graphs", size=10),  # 히스토그램 섹션
                Layout(name="footer", size=25)  # 프로세스 테이블 크기 증가
            )
        else:
            # 기본 레이아웃 (live 모드)
            layout.split(
                Layout(name="header", size=4),
                Layout(name="body", size=40),  # 상단 패널 크기 축소
                Layout(name="footer", size=20)  # 프로세스 테이블 크기 증가
            )

        # 바디를 좌우로 분할
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )

        # 좌측 분할
        layout["body"]["left"].split(
            Layout(name="cpu"),
            Layout(name="memory")
        )

        # 우측 분할
        layout["body"]["right"].split(
            Layout(name="disk"),
            Layout(name="network")
        )

        # 패널 할당 (히스토리 포함 여부에 따라)
        layout["header"].update(self.create_header_panel(stats))
        layout["body"]["left"]["cpu"].update(self.create_cpu_panel(stats, include_history=include_history))
        layout["body"]["left"]["memory"].update(self.create_memory_panel(stats, include_history=include_history))
        layout["body"]["right"]["disk"].update(self.create_disk_panel(stats))
        layout["body"]["right"]["network"].update(self.create_network_panel(stats, include_history=include_history))

        # 히스토리 그래프 섹션 추가 (layout 모드일 때)
        if include_history:
            layout["graphs"].update(self.create_history_panel())

        layout["footer"].update(self.create_process_table())

        return layout

    def create_history_panel(self) -> Panel:
        """히스토리 그래프 패널 생성"""
        from rich.columns import Columns
        from rich.text import Text

        graphs = []

        # CPU 히스토리 그래프
        if self.cpu_history:
            cpu_graph = self.create_ascii_graph(
                self.cpu_history,
                width=40,
                height=4,
                label="CPU Usage (%)"
            )
            cpu_panel = Panel(
                Text.from_markup(cpu_graph),
                title="[cyan]CPU[/cyan]",
                border_style="cyan",
                padding=(0, 1)
            )
            graphs.append(cpu_panel)

        # 메모리 히스토리 그래프
        if self.mem_history:
            mem_graph = self.create_ascii_graph(
                self.mem_history,
                width=40,
                height=4,
                label="Memory Usage (%)"
            )
            mem_panel = Panel(
                Text.from_markup(mem_graph),
                title="[magenta]Memory[/magenta]",
                border_style="magenta",
                padding=(0, 1)
            )
            graphs.append(mem_panel)

        # 네트워크 히스토리 그래프 (결합)
        if self.net_in_history or self.net_out_history:
            net_text = ""
            if self.net_in_history:
                net_in_spark = self.create_sparkline(self.net_in_history, width=35)
                net_text += f"↓ IN:  {net_in_spark}\n"
            if self.net_out_history:
                net_out_spark = self.create_sparkline(self.net_out_history, width=35)
                net_text += f"↑ OUT: {net_out_spark}"

            net_panel = Panel(
                Text.from_markup(net_text),
                title="[green]Network (MB/s)[/green]",
                border_style="green",
                padding=(0, 1)
            )
            graphs.append(net_panel)

        # 그래프들을 컬럼으로 배치
        if graphs:
            columns = Columns(graphs, equal=True, expand=True)
            return Panel(
                columns,
                title="[bold yellow]📈 Historical Trends (Live)[/bold yellow]",
                border_style="yellow",
                padding=(0, 1)
            )
        else:
            return Panel(
                Text.from_markup("Collecting data..."),
                title="[bold yellow]📈 Historical Trends[/bold yellow]",
                border_style="yellow"
            )

    def print_line_mode(self, stats: SystemStats):
        """라인 모드 출력 (레거시 스타일)"""
        # 시스템 정보 계산
        hostname = os.uname().nodename[:20]
        cores = psutil.cpu_count(logical=False)
        memory_gb = stats.memory_total / (1024**3)

        # 헤더를 주기적으로 출력
        if not hasattr(self, '_line_count'):
            self._line_count = 0

        if self._line_count % 20 == 0:
            # 시스템 타이틀
            title = f"🐰 {hostname} <{cores} cores, {memory_gb:.0f}GB> 🐰"
            self.console.print(f"\n{title}")

            # 컬럼 헤더
            headers = [
                "time", "net_in", "net_out", "pk_in", "pk_out",
                "load", "usr", "sys", "i/o", "disk_rd", "disk_wr", "mem_%"
            ]
            header_row = "│" + "│".join(f"{h:>9}" for h in headers) + "│"
            self.console.print(header_row, style="bold cyan", crop=False, overflow="ignore")

        # 데이터 계산
        current_time = datetime.now().strftime("%H:%M:%S")

        # 네트워크 및 디스크 속도 계산
        net_in_rate = "0.00M"
        net_out_rate = "0.00M"
        pk_in = "0"
        pk_out = "0"
        disk_rd_rate = "0.00M"
        disk_wr_rate = "0.00M"

        if self.prev_stats:
            time_delta = stats.timestamp - self.prev_stats.timestamp
            if time_delta > 0:
                # 네트워크 속도 (MB/s)
                net_in = (stats.net_bytes_recv - self.prev_stats.net_bytes_recv) / time_delta / (1024 * 1024)
                net_out = (stats.net_bytes_sent - self.prev_stats.net_bytes_sent) / time_delta / (1024 * 1024)
                net_in_rate = f"{net_in:.2f}M"
                net_out_rate = f"{net_out:.2f}M"

                # 패킷 속도
                pk_in = f"{int((stats.net_packets_recv - self.prev_stats.net_packets_recv) / time_delta)}"
                pk_out = f"{int((stats.net_packets_sent - self.prev_stats.net_packets_sent) / time_delta)}"

                # 디스크 I/O (MB/s)
                disk_rd = (stats.disk_read_bytes - self.prev_stats.disk_read_bytes) / time_delta / (1024 * 1024)
                disk_wr = (stats.disk_write_bytes - self.prev_stats.disk_write_bytes) / time_delta / (1024 * 1024)
                disk_rd_rate = f"{disk_rd:.2f}M"
                disk_wr_rate = f"{disk_wr:.2f}M"

        # CPU 정보
        cpu_times = psutil.cpu_times_percent(interval=0.1)
        usr = f"{cpu_times.user:.1f}%"
        sys = f"{cpu_times.system:.1f}%"
        iowait = f"{getattr(cpu_times, 'iowait', 0):.2f}"

        # 로드 평균
        load = f"{stats.load_average[0]:.2f}"

        # 메모리
        mem_pct = f"{stats.memory_percent:.1f}%"

        # 색상 적용
        usr_colored = self.apply_value_color("usr", usr, cpu_times.user)
        sys_colored = self.apply_value_color("sys", sys, cpu_times.system)
        mem_colored = self.apply_value_color("mem", mem_pct, stats.memory_percent)
        load_colored = self.apply_value_color("load", load, stats.load_average[0], cores)
        io_colored = self.apply_value_color("io", iowait, float(iowait))

        # 데이터 행 생성
        values = [
            current_time, net_in_rate, net_out_rate, pk_in, pk_out,
            load_colored, usr_colored, sys_colored, io_colored,
            disk_rd_rate, disk_wr_rate, mem_colored
        ]

        # 각 값을 적절한 너비로 포맷
        formatted_values = []
        for val in values:
            # 마크업이 있는 경우 처리
            if '[' in str(val) and ']' in str(val):
                # 실제 텍스트 길이 계산 (마크업 제외)
                import re
                clean_val = re.sub(r'\[.*?\]', '', str(val))
                padding = 9 - len(clean_val)
                formatted_values.append(' ' * padding + str(val))
            else:
                formatted_values.append(f"{val:>9}")

        # 행 생성 및 출력
        row_text = "│" + "│".join(formatted_values) + "│"
        self.console.print(row_text, crop=False, overflow="ignore")
        self._line_count += 1

    async def run_monitoring_loop(self):
        """모니터링 루프 실행"""
        self.config = self.create_config()

        if self.config.print_type == "live":
            # Live 모드 - 기본 대시보드
            with Live(refresh_per_second=1, screen=True) as live:
                while True:
                    try:
                        stats = await self.collect_system_stats()
                        self.update_history(stats)
                        layout = self.create_resource_layout(stats, include_history=False)
                        live.update(layout)
                        self.prev_stats = stats
                        await asyncio.sleep(self.config.interval)
                    except KeyboardInterrupt:
                        break
        elif self.config.print_type == "layout":
            # Layout 모드 - 히스토리 그래프 포함
            with Live(refresh_per_second=1, screen=True) as live:
                while True:
                    try:
                        stats = await self.collect_system_stats()
                        self.update_history(stats)
                        layout = self.create_resource_layout(stats, include_history=True)
                        live.update(layout)
                        self.prev_stats = stats
                        await asyncio.sleep(self.config.interval)
                    except KeyboardInterrupt:
                        break
        else:
            # Line 모드 - 첫 측정을 위한 초기화
            self.prev_stats = await self.collect_system_stats()
            await asyncio.sleep(0.1)  # 짧은 대기

            while True:
                try:
                    stats = await self.collect_system_stats()
                    self.print_line_mode(stats)
                    self.prev_stats = stats
                    await asyncio.sleep(self.config.interval)
                except KeyboardInterrupt:
                    break

    async def run_network_monitoring(self):
        """네트워크 전용 모니터링"""
        self.config = self.create_config()

        with Live(refresh_per_second=1, screen=True) as live:
            while True:
                try:
                    # 네트워크 정보 수집 (권한 에러 처리)
                    try:
                        net_connections = psutil.net_connections(kind='inet')
                    except (psutil.AccessDenied, PermissionError, OSError) as e:
                        # 권한이 없는 경우 현재 프로세스의 연결만 가져오기
                        net_connections = []
                        self.log_warning(f"⚠️ Limited network access (try with sudo for full access)")

                    try:
                        net_if_stats = psutil.net_if_stats()
                    except Exception:
                        net_if_stats = {}

                    try:
                        net_if_addrs = psutil.net_if_addrs()
                    except Exception:
                        net_if_addrs = {}

                    # 네트워크 테이블 생성
                    table = Table(title="[bold green]Network Connections Monitor[/bold green]",
                                show_header=True, header_style="bold green", box=box.SIMPLE)
                    table.add_column("Protocol", width=10)
                    table.add_column("Local Address", width=25)
                    table.add_column("Remote Address", width=25)
                    table.add_column("Status", width=15)
                    table.add_column("PID", width=10)

                    # 네트워크 I/O 통계 추가
                    net_io = psutil.net_io_counters()
                    if net_io:
                        # 헤더에 네트워크 통계 추가
                        stats_text = f"Total: ↑ {self.format_bytes(net_io.bytes_sent, 'GB')} ↓ {self.format_bytes(net_io.bytes_recv, 'GB')}"
                        table.caption = stats_text

                    # 연결 정보가 없는 경우 기본 네트워크 정보 표시
                    if not net_connections:
                        # 네트워크 인터페이스 정보 표시
                        for iface, addrs in net_if_addrs.items():
                            for addr in addrs:
                                if addr.family.name == 'AF_INET':  # IPv4만
                                    table.add_row(
                                        "Interface",
                                        f"{iface}: {addr.address}",
                                        "-",
                                        "ACTIVE" if iface in net_if_stats and net_if_stats[iface].isup else "DOWN",
                                        "-"
                                    )
                    else:
                        # 프로토콜 필터링
                        for conn in net_connections:
                            try:
                                protocol_name = conn.type.name.lower() if hasattr(conn.type, 'name') else str(conn.type)
                                if protocol_name not in self.config.protocols:
                                    continue

                                local_addr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "-"
                                remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "-"

                                status = conn.status if hasattr(conn, 'status') else "UNKNOWN"
                                status_color = "green" if status == "ESTABLISHED" else "yellow"

                                table.add_row(
                                    protocol_name.upper(),
                                    local_addr,
                                    remote_addr,
                                    f"[{status_color}]{status}[/{status_color}]",
                                    str(conn.pid) if conn.pid else "-"
                                )
                            except Exception:
                                continue

                    live.update(table)
                    await asyncio.sleep(self.config.interval)

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.log_error(f"Network monitoring error: {e}")
                    await asyncio.sleep(self.config.interval)

    async def run_process_monitoring(self):
        """프로세스 전용 모니터링"""
        self.config = self.create_config()

        with Live(refresh_per_second=1, screen=True) as live:
            while True:
                try:
                    # 프로세스 상세 테이블
                    table = Table(title="[bold cyan]Process Monitor[/bold cyan]",
                                show_header=True, header_style="bold cyan", box=box.ROUNDED)
                    table.add_column("PID", style="cyan", width=8)
                    table.add_column("Name", style="white", width=45)
                    table.add_column("CPU%", style="yellow", width=8)
                    table.add_column("MEM%", style="magenta", width=8)
                    table.add_column("RSS", style="blue", width=10)
                    table.add_column("CPU Time", style="cyan", width=12)
                    table.add_column("Threads", style="green", width=8)
                    table.add_column("Status", style="bright_green", width=12)
                    table.add_column("User", style="white", width=15)

                    processes = []
                    # cmdline 옵션 지원을 위해 info_fields 설정
                    info_fields = ['pid', 'name', 'cpu_percent', 'memory_percent',
                                 'num_threads', 'status', 'username', 'memory_info', 'cpu_times']
                    if self.config and self.config.show_cmdline:
                        info_fields.append('cmdline')

                    for proc in psutil.process_iter(info_fields):
                        try:
                            pinfo = proc.info

                            # 필터 적용
                            if self.config.pid_filter and pinfo['pid'] not in self.config.pid_filter:
                                continue

                            if self.config.proc_filter:
                                if not any(f in pinfo['name'] for f in self.config.proc_filter):
                                    continue

                            processes.append(pinfo)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass

                    # 정렬 기준에 따라 정렬 (None 값 처리)
                    if self.config.group_by == "name":
                        processes.sort(key=lambda x: x.get('name', ''))
                    else:
                        processes.sort(key=lambda x: x.get('cpu_percent') or 0, reverse=True)

                    # 상위 N개만 표시
                    for proc in processes[:self.config.top_n]:
                        cpu_val = proc.get('cpu_percent') or 0
                        mem_val = proc.get('memory_percent') or 0
                        cpu_color = self.get_color_by_percent(cpu_val * 10)
                        mem_color = self.get_color_by_percent(mem_val * 10)

                        # 프로세스 이름 또는 명령줄 표시
                        if self.config and self.config.show_cmdline:
                            cmdline = proc.get('cmdline', [])
                            if cmdline:
                                display_name = ' '.join(cmdline)
                            else:
                                display_name = proc.get('name', '')
                        else:
                            display_name = proc.get('name', '')

                        # 메모리 정보 (RSS)
                        memory_info = proc.get('memory_info')
                        if memory_info:
                            rss_mb = memory_info.rss / 1024 / 1024  # bytes to MB
                            rss_str = f"{rss_mb:.1f}M"
                        else:
                            rss_str = "N/A"

                        # CPU 시간
                        cpu_times = proc.get('cpu_times')
                        if cpu_times:
                            total_time = cpu_times.user + cpu_times.system
                            hours = int(total_time // 3600)
                            minutes = int((total_time % 3600) // 60)
                            seconds = int(total_time % 60)
                            if hours > 0:
                                cpu_time_str = f"{hours}h{minutes:02d}m"
                            elif minutes > 0:
                                cpu_time_str = f"{minutes}m{seconds:02d}s"
                            else:
                                cpu_time_str = f"{seconds}s"
                        else:
                            cpu_time_str = "N/A"

                        table.add_row(
                            str(proc.get('pid', '')),
                            shorten_text(display_name, 45),
                            f"[{cpu_color}]{cpu_val:.1f}[/{cpu_color}]",
                            f"[{mem_color}]{mem_val:.1f}[/{mem_color}]",
                            rss_str,
                            cpu_time_str,
                            str(proc.get('num_threads', '')),
                            proc.get('status', ''),
                            proc.get('username', '')[:15]
                        )

                    live.update(table)
                    await asyncio.sleep(self.config.interval)

                except KeyboardInterrupt:
                    break

    async def run_async(self) -> int:
        """비동기 명령어 실행"""
        try:
            self.config = self.create_config()
            command = self.config.command.lower()

            self.log_info(f"🚀 Starting {command} monitoring")
            self.log_info(f"📊 Update interval: {self.config.interval}s")
            self.log_info("Press Ctrl+C to stop")

            if command == "net":
                await self.run_network_monitoring()
            elif command == "proc":
                await self.run_process_monitoring()
            else:
                await self.run_monitoring_loop()

            return 0

        except KeyboardInterrupt:
            self.log_info("\n⏹️  Monitoring stopped by user")
            return 0
        except Exception as e:
            self.log_error(f"Monitoring error: {e}")
            if pawn.get('PAWN_DEBUG'):
                pawn.console.print_exception(show_locals=True)
            return 1


def shorten_text(text: str, max_length: int) -> str:
    """텍스트를 최대 길이로 자르기"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def get_arguments(parser: ArgumentParser):
    cli = TopCLI()
    cli.get_arguments(parser)


def main():
    """CLI 진입점"""
    cli = TopCLI()
    return cli.main()


if __name__ == "__main__":
    exit(main())
