"""HTTP 관련 CLI 명령어"""

from __future__ import annotations

import asyncio
from typing import Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

from core.base import PawnStack
from config.settings import Config

app = typer.Typer(help="HTTP 클라이언트 및 모니터링 도구")
console = Console()


@app.command()
def get(
    url: str = typer.Argument(..., help="요청할 URL"),
    headers: Optional[List[str]] = typer.Option(
        None,
        "--header",
        "-H",
        help="HTTP 헤더 (key:value 형식)",
    ),
    timeout: float = typer.Option(30.0, "--timeout", "-t", help="타임아웃 (초)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="상세 출력"),
) -> None:
    """HTTP GET 요청 실행"""
    
    async def _get() -> None:
        # 헤더 파싱
        request_headers: Dict[str, str] = {}
        if headers:
            for header in headers:
                if ":" in header:
                    key, value = header.split(":", 1)
                    request_headers[key.strip()] = value.strip()
        
        # 설정 생성
        config = Config()
        config.http.timeout = timeout
        
        async with PawnStack(config) as pstack:
            try:
                response = await pstack.http.get(url, headers=request_headers)
                
                # 결과 출력
                if verbose:
                    table = Table(title=f"HTTP GET {url}")
                    table.add_column("항목", style="cyan")
                    table.add_column("값", style="green")
                    
                    table.add_row("상태 코드", str(response.status_code))
                    table.add_row("응답 시간", f"{response.elapsed:.3f}초")
                    table.add_row("Content-Type", response.headers.get("content-type", "N/A"))
                    table.add_row("Content-Length", response.headers.get("content-length", "N/A"))
                    
                    console.print(table)
                    
                    if response.text:
                        console.print(Panel(response.text[:1000], title="응답 본문 (처음 1000자)"))
                else:
                    status_style = "green" if response.is_success else "red"
                    console.print(f"[{status_style}]{response.status_code}[/{status_style}] {url} ({response.elapsed:.3f}s)")
                    
            except Exception as e:
                console.print(f"[red]오류:[/red] {e}")
                raise typer.Exit(1)
    
    asyncio.run(_get())


@app.command()
def monitor(
    url: str = typer.Argument(..., help="모니터링할 URL"),
    interval: float = typer.Option(5.0, "--interval", "-i", help="모니터링 간격 (초)"),
    count: Optional[int] = typer.Option(None, "--count", "-c", help="요청 횟수 (무제한: None)"),
    timeout: float = typer.Option(10.0, "--timeout", "-t", help="타임아웃 (초)"),
) -> None:
    """HTTP 엔드포인트 모니터링"""
    
    async def _monitor() -> None:
        config = Config()
        config.http.timeout = timeout
        
        request_count = 0
        success_count = 0
        error_count = 0
        total_time = 0.0
        
        async with PawnStack(config) as pstack:
            
            def create_table() -> Table:
                table = Table(title=f"HTTP 모니터링: {url}")
                table.add_column("항목", style="cyan")
                table.add_column("값", style="green")
                
                table.add_row("총 요청", str(request_count))
                table.add_row("성공", f"[green]{success_count}[/green]")
                table.add_row("실패", f"[red]{error_count}[/red]")
                
                if request_count > 0:
                    success_rate = (success_count / request_count) * 100
                    avg_time = total_time / request_count
                    table.add_row("성공률", f"{success_rate:.1f}%")
                    table.add_row("평균 응답시간", f"{avg_time:.3f}초")
                
                return table
            
            with Live(create_table(), refresh_per_second=1) as live:
                try:
                    while count is None or request_count < count:
                        try:
                            response = await pstack.http.get(url)
                            request_count += 1
                            total_time += response.elapsed
                            
                            if response.is_success:
                                success_count += 1
                            else:
                                error_count += 1
                                
                        except Exception:
                            request_count += 1
                            error_count += 1
                        
                        live.update(create_table())
                        
                        if count is None or request_count < count:
                            await asyncio.sleep(interval)
                            
                except KeyboardInterrupt:
                    console.print("\n[yellow]모니터링이 중단되었습니다.[/yellow]")
    
    asyncio.run(_monitor())


@app.command()
def post(
    url: str = typer.Argument(..., help="요청할 URL"),
    data: Optional[str] = typer.Option(None, "--data", "-d", help="POST 데이터 (JSON 문자열)"),
    file: Optional[typer.FileText] = typer.Option(None, "--file", "-f", help="POST 데이터 파일"),
    headers: Optional[List[str]] = typer.Option(
        None,
        "--header",
        "-H",
        help="HTTP 헤더 (key:value 형식)",
    ),
    timeout: float = typer.Option(30.0, "--timeout", "-t", help="타임아웃 (초)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="상세 출력"),
) -> None:
    """HTTP POST 요청 실행"""
    
    async def _post() -> None:
        # 데이터 준비
        post_data = None
        if data:
            try:
                import json
                post_data = json.loads(data)
            except json.JSONDecodeError:
                post_data = data
        elif file:
            post_data = file.read()
        
        # 헤더 파싱
        request_headers: Dict[str, str] = {}
        if headers:
            for header in headers:
                if ":" in header:
                    key, value = header.split(":", 1)
                    request_headers[key.strip()] = value.strip()
        
        # 설정 생성
        config = Config()
        config.http.timeout = timeout
        
        async with PawnStack(config) as pstack:
            try:
                if isinstance(post_data, dict):
                    response = await pstack.http.post(url, json=post_data, headers=request_headers)
                else:
                    response = await pstack.http.post(url, data=post_data, headers=request_headers)
                
                # 결과 출력
                if verbose:
                    table = Table(title=f"HTTP POST {url}")
                    table.add_column("항목", style="cyan")
                    table.add_column("값", style="green")
                    
                    table.add_row("상태 코드", str(response.status_code))
                    table.add_row("응답 시간", f"{response.elapsed:.3f}초")
                    table.add_row("Content-Type", response.headers.get("content-type", "N/A"))
                    
                    console.print(table)
                    
                    if response.text:
                        console.print(Panel(response.text[:1000], title="응답 본문 (처음 1000자)"))
                else:
                    status_style = "green" if response.is_success else "red"
                    console.print(f"[{status_style}]{response.status_code}[/{status_style}] {url} ({response.elapsed:.3f}s)")
                    
            except Exception as e:
                console.print(f"[red]오류:[/red] {e}")
                raise typer.Exit(1)
    
    asyncio.run(_post())