"""시스템 관련 CLI 명령어"""

from __future__ import annotations

import asyncio
import time
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

import psutil

app = typer.Typer(help="시스템 리소스 모니터링 도구")
console = Console()


@app.command()
def info() -> None:
    """시스템 정보 출력"""
    
    # CPU 정보
    cpu_count = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # 메모리 정보
    memory = psutil.virtual_memory()
    
    # 디스크 정보
    disk = psutil.disk_usage('/')
    
    # 네트워크 정보
    network = psutil.net_io_counters()
    
    # 부팅 시간
    boot_time = psutil.boot_time()
    boot_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(boot_time))
    
    table = Table(title="시스템 정보")
    table.add_column("항목", style="cyan")
    table.add_column("값", style="green")
    
    # CPU
    table.add_row("CPU 코어 수", str(cpu_count))
    table.add_row("CPU 사용률", f"{cpu_percent}%")
    
    # 메모리
    table.add_row("총 메모리", f"{memory.total / (1024**3):.1f} GB")
    table.add_row("사용 메모리", f"{memory.used / (1024**3):.1f} GB")
    table.add_row("메모리 사용률", f"{memory.percent}%")
    
    # 디스크
    table.add_row("총 디스크", f"{disk.total / (1024**3):.1f} GB")
    table.add_row("사용 디스크", f"{disk.used / (1024**3):.1f} GB")
    table.add_row("디스크 사용률", f"{(disk.used / disk.total) * 100:.1f}%")
    
    # 네트워크
    table.add_row("네트워크 송신", f"{network.bytes_sent / (1024**2):.1f} MB")
    table.add_row("네트워크 수신", f"{network.bytes_recv / (1024**2):.1f} MB")
    
    # 기타
    table.add_row("부팅 시간", boot_time_str)
    
    console.print(table)


@app.command()
def monitor(
    interval: float = typer.Option(1.0, "--interval", "-i", help="모니터링 간격 (초)"),
    duration: Optional[float] = typer.Option(None, "--duration", "-d", help="모니터링 지속 시간 (초)"),
) -> None:
    """실시간 시스템 리소스 모니터링"""
    
    def create_table() -> Table:
        # 현재 시스템 정보 수집
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 네트워크 정보
        try:
            network = psutil.net_io_counters()
            network_sent = network.bytes_sent / (1024**2)  # MB
            network_recv = network.bytes_recv / (1024**2)  # MB
        except:
            network_sent = network_recv = 0
        
        # 프로세스 수
        process_count = len(psutil.pids())
        
        table = Table(title="실시간 시스템 모니터링")
        table.add_column("리소스", style="cyan")
        table.add_column("사용량", style="green")
        table.add_column("상태", style="yellow")
        
        # CPU 상태 결정
        cpu_status = "🟢 정상" if cpu_percent < 70 else "🟡 주의" if cpu_percent < 90 else "🔴 위험"
        table.add_row("CPU", f"{cpu_percent:.1f}%", cpu_status)
        
        # 메모리 상태 결정
        memory_status = "🟢 정상" if memory.percent < 70 else "🟡 주의" if memory.percent < 90 else "🔴 위험"
        table.add_row(
            "메모리", 
            f"{memory.percent:.1f}% ({memory.used / (1024**3):.1f}/{memory.total / (1024**3):.1f} GB)",
            memory_status
        )
        
        # 디스크 상태 결정
        disk_percent = (disk.used / disk.total) * 100
        disk_status = "🟢 정상" if disk_percent < 80 else "🟡 주의" if disk_percent < 95 else "🔴 위험"
        table.add_row(
            "디스크",
            f"{disk_percent:.1f}% ({disk.used / (1024**3):.1f}/{disk.total / (1024**3):.1f} GB)",
            disk_status
        )
        
        # 네트워크
        table.add_row("네트워크 송신", f"{network_sent:.1f} MB", "📤")
        table.add_row("네트워크 수신", f"{network_recv:.1f} MB", "📥")
        
        # 프로세스
        table.add_row("실행 중인 프로세스", str(process_count), "⚙️")
        
        return table
    
    start_time = time.time()
    
    with Live(create_table(), refresh_per_second=2) as live:
        try:
            while True:
                live.update(create_table())
                
                # 지속 시간 체크
                if duration and (time.time() - start_time) >= duration:
                    break
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]모니터링이 중단되었습니다.[/yellow]")


@app.command()
def processes(
    top: int = typer.Option(10, "--top", "-t", help="상위 프로세스 개수"),
    sort_by: str = typer.Option("cpu", "--sort", "-s", help="정렬 기준 (cpu, memory, pid, name)"),
) -> None:
    """실행 중인 프로세스 목록"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("프로세스 정보 수집 중...", total=None)
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        progress.remove_task(task)
    
    # 정렬
    if sort_by == "cpu":
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
    elif sort_by == "memory":
        processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
    elif sort_by == "pid":
        processes.sort(key=lambda x: x['pid'])
    elif sort_by == "name":
        processes.sort(key=lambda x: x['name'] or "")
    
    # 상위 프로세스만 선택
    top_processes = processes[:top]
    
    table = Table(title=f"상위 {top}개 프로세스 ({sort_by} 기준 정렬)")
    table.add_column("PID", style="cyan")
    table.add_column("프로세스명", style="green")
    table.add_column("CPU %", style="yellow")
    table.add_column("메모리 %", style="red")
    
    for proc in top_processes:
        table.add_row(
            str(proc['pid']),
            proc['name'] or "N/A",
            f"{proc['cpu_percent'] or 0:.1f}",
            f"{proc['memory_percent'] or 0:.1f}",
        )
    
    console.print(table)


@app.command()
def disk() -> None:
    """디스크 사용량 정보"""
    
    table = Table(title="디스크 사용량")
    table.add_column("마운트 포인트", style="cyan")
    table.add_column("파일시스템", style="green")
    table.add_column("총 용량", style="blue")
    table.add_column("사용량", style="yellow")
    table.add_column("사용률", style="red")
    
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            
            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            percent = (usage.used / usage.total) * 100
            
            # 사용률에 따른 색상
            if percent < 70:
                percent_str = f"[green]{percent:.1f}%[/green]"
            elif percent < 90:
                percent_str = f"[yellow]{percent:.1f}%[/yellow]"
            else:
                percent_str = f"[red]{percent:.1f}%[/red]"
            
            table.add_row(
                partition.mountpoint,
                partition.fstype,
                f"{total_gb:.1f} GB",
                f"{used_gb:.1f} GB",
                percent_str,
            )
            
        except PermissionError:
            table.add_row(
                partition.mountpoint,
                partition.fstype,
                "권한 없음",
                "권한 없음",
                "권한 없음",
            )
    
    console.print(table)