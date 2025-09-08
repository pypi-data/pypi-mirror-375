"""
HTTP 모니터링 모듈

HTTP/HTTPS 엔드포인트의 상태, 응답 시간, 가용성을 모니터링합니다.
Rich 기반 실시간 대시보드를 제공합니다.
"""

import asyncio
import time
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from collections import deque

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.layout import Layout
from rich.text import Text

from pawnstack.http_client.client import HttpClient, HttpResponse
from pawnstack.type_utils.validators import is_valid_url


@dataclass
class HTTPMonitorConfig:
    """HTTP 모니터링 설정"""
    url: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    data: Union[str, Dict[str, Any]] = field(default_factory=dict)
    timeout: float = 10.0
    interval: float = 1.0
    success_criteria: List[str] = field(default_factory=lambda: ["status_code==200"])
    logical_operator: str = "and"
    name: Optional[str] = None
    verify_ssl: bool = True
    max_history: int = 100

    def __post_init__(self):
        """초기화 후 처리"""
        if not self.name:
            self.name = self.url

        if not is_valid_url(self.url):
            raise ValueError(f"Invalid URL: {self.url}")


@dataclass
class MonitorResult:
    """모니터링 결과"""
    timestamp: datetime
    url: str
    method: str
    status_code: Optional[int]
    response_time: float
    success: bool
    error: Optional[str] = None
    content_length: int = 0
    headers: Dict[str, str] = field(default_factory=dict)
    custom_data: Dict[str, Any] = field(default_factory=dict)


class HTTPMonitor:
    """
    HTTP 모니터링 클래스

    여러 HTTP 엔드포인트를 동시에 모니터링하고 실시간 대시보드를 제공합니다.
    """

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.configs: List[HTTPMonitorConfig] = []
        self.results: Dict[str, deque] = {}
        self.statistics: Dict[str, Dict[str, Any]] = {}
        self.response_time_history: Dict[str, deque] = {}  # sparkline용 히스토리
        self.status_history: Dict[str, deque] = {}  # 상태 히스토리
        self.client = HttpClient()
        self.is_running = False
        self._tasks: List[asyncio.Task] = []
        # 터미널 너비 감지
        self.terminal_width = self.console.width

    def add_endpoint(self, config: HTTPMonitorConfig):
        """모니터링할 엔드포인트 추가"""
        self.configs.append(config)
        self.results[config.name] = deque(maxlen=config.max_history)
        self.response_time_history[config.name] = deque(maxlen=60)  # 60개 데이터 포인트 유지
        self.status_history[config.name] = deque(maxlen=60)  # 성공/실패 히스토리
        self.statistics[config.name] = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'error_requests': 0,
            'avg_response_time': 0.0,
            'min_response_time': float('inf'),
            'max_response_time': 0.0,
            'last_check': None,
            'uptime_percentage': 0.0
        }

    def remove_endpoint(self, name: str):
        """엔드포인트 제거"""
        self.configs = [c for c in self.configs if c.name != name]
        if name in self.results:
            del self.results[name]
        if name in self.statistics:
            del self.statistics[name]

    def clear_endpoints(self):
        """모든 엔드포인트 제거"""
        self.configs.clear()
        self.results.clear()
        self.statistics.clear()

    async def check_endpoint(self, config: HTTPMonitorConfig) -> MonitorResult:
        """단일 엔드포인트 체크"""
        start_time = time.time()

        try:
            # HTTP 요청 실행
            response = await self.client.request(
                method=config.method,
                url=config.url,
                headers=config.headers,
                json=config.data if isinstance(config.data, dict) else None,
                data=config.data if isinstance(config.data, str) else None,
                timeout=config.timeout,
                verify_ssl=config.verify_ssl
            )

            response_time = time.time() - start_time

            # 성공 기준 검사
            success = self._check_success_criteria(
                response, response_time, config.success_criteria, config.logical_operator
            )

            result = MonitorResult(
                timestamp=datetime.now(),
                url=config.url,
                method=config.method,
                status_code=response.status_code,
                response_time=response_time,
                success=success,
                content_length=len(response.content) if response.content else 0,
                headers=dict(response.headers) if hasattr(response, 'headers') else {}
            )

        except Exception as e:
            response_time = time.time() - start_time
            result = MonitorResult(
                timestamp=datetime.now(),
                url=config.url,
                method=config.method,
                status_code=None,
                response_time=response_time,
                success=False,
                error=str(e)
            )

        # 결과 저장 및 통계 업데이트
        self._store_result(config.name, result)
        self._update_statistics(config.name, result)

        return result

    def _check_success_criteria(
        self,
        response: HttpResponse,
        response_time: float,
        criteria: List[str],
        operator: str = "and"
    ) -> bool:
        """성공 기준 검사"""
        if not criteria:
            return 200 <= response.status_code < 300

        results = []

        for criterion in criteria:
            if "==" in criterion:
                key, expected = criterion.split("==", 1)
                key = key.strip()
                expected = expected.strip()

                if key == "status_code":
                    results.append(response.status_code == int(expected))
                elif key == "response_time":
                    results.append(response_time == float(expected))
                else:
                    # 응답 데이터에서 키 검색
                    try:
                        if hasattr(response, 'json') and response.content:
                            data = response.json()
                            actual = self._get_nested_value(data, key)
                            results.append(str(actual) == expected)
                        else:
                            results.append(False)
                    except:
                        results.append(False)

            elif "<" in criterion:
                key, threshold = criterion.split("<", 1)
                key = key.strip()
                threshold = float(threshold.strip())

                if key == "response_time":
                    results.append(response_time < threshold)
                else:
                    results.append(False)

            elif ">" in criterion:
                key, threshold = criterion.split(">", 1)
                key = key.strip()
                threshold = float(threshold.strip())

                if key == "response_time":
                    results.append(response_time > threshold)
                else:
                    results.append(False)

        # 논리 연산자 적용
        if operator.lower() == "and":
            return all(results)
        elif operator.lower() == "or":
            return any(results)
        else:
            return all(results)

    def _get_nested_value(self, data: Dict[str, Any], key_path: str) -> Any:
        """중첩된 딕셔너리에서 값 추출"""
        keys = key_path.split(".")
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current

    def _store_result(self, name: str, result: MonitorResult):
        """결과 저장"""
        if name in self.results:
            self.results[name].append(result)

            # Sparkline 히스토리 업데이트
            if name in self.response_time_history:
                self.response_time_history[name].append(result.response_time)

            if name in self.status_history:
                # 성공: 1, 실패: 0
                self.status_history[name].append(1 if result.success else 0)

    def _update_statistics(self, name: str, result: MonitorResult):
        """통계 업데이트"""
        if name not in self.statistics:
            return

        stats = self.statistics[name]
        stats['total_requests'] += 1
        stats['last_check'] = result.timestamp

        if result.success:
            stats['successful_requests'] += 1
        else:
            if result.error:
                stats['error_requests'] += 1
            else:
                stats['failed_requests'] += 1

        # 응답 시간 통계
        if result.response_time > 0:
            stats['min_response_time'] = min(stats['min_response_time'], result.response_time)
            stats['max_response_time'] = max(stats['max_response_time'], result.response_time)

            # 평균 응답 시간 계산 (최근 결과들 기준)
            recent_results = list(self.results[name])
            if recent_results:
                response_times = [r.response_time for r in recent_results if r.response_time > 0]
                if response_times:
                    stats['avg_response_time'] = sum(response_times) / len(response_times)

        # 가동률 계산
        if stats['total_requests'] > 0:
            stats['uptime_percentage'] = (stats['successful_requests'] / stats['total_requests']) * 100

    def get_statistics(self, name: Optional[str] = None) -> Dict[str, Any]:
        """통계 정보 반환"""
        if name:
            return self.statistics.get(name, {})
        return self.statistics.copy()

    def get_recent_results(self, name: str, count: int = 10) -> List[MonitorResult]:
        """최근 결과 반환"""
        if name not in self.results:
            return []

        recent = list(self.results[name])
        return recent[-count:] if len(recent) > count else recent

    async def start_monitoring(self, dashboard: bool = True):
        """모니터링 시작"""
        if not self.configs:
            raise ValueError("No endpoints configured for monitoring")

        self.is_running = True

        # 각 엔드포인트별 모니터링 태스크 생성
        for config in self.configs:
            task = asyncio.create_task(self._monitor_endpoint(config))
            self._tasks.append(task)

        # 대시보드 실행
        if dashboard:
            dashboard_task = asyncio.create_task(self._run_dashboard())
            self._tasks.append(dashboard_task)

        try:
            # 모든 태스크 실행
            await asyncio.gather(*self._tasks)
        except KeyboardInterrupt:
            self.console.print("\n[yellow]모니터링이 중단되었습니다.[/yellow]")
        finally:
            await self.stop_monitoring()

    async def stop_monitoring(self):
        """모니터링 중단"""
        self.is_running = False

        # 모든 태스크 취소
        for task in self._tasks:
            if not task.done():
                task.cancel()

        # 태스크 완료 대기
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

        self._tasks.clear()

    async def _monitor_endpoint(self, config: HTTPMonitorConfig):
        """엔드포인트 모니터링 루프"""
        while self.is_running:
            try:
                await self.check_endpoint(config)
                await asyncio.sleep(config.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                # 에러 로깅 (향후 로거 통합)
                pass

    async def _run_dashboard(self):
        """실시간 대시보드 실행"""
        # 대시보드 시작시 터미널 너비 업데이트
        self.terminal_width = self.console.width
        layout = Layout()

        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", size=12),  # 고정 크기로 축소
            Layout(name="graphs", ratio=3),  # 더 많은 공간 할당
            Layout(name="footer", size=2)    # 푸터 크기 축소
        )

        layout["main"].split_row(
            Layout(name="endpoints", ratio=2),  # 엔드포인트에 더 많은 공간
            Layout(name="statistics", ratio=1)   # 통계는 작게
        )

        with Live(layout, refresh_per_second=2, screen=True) as live:
            while self.is_running:
                try:
                    # 헤더 업데이트
                    layout["header"].update(
                        Panel(
                            f"[bold blue]HTTP 모니터링 대시보드[/bold blue] - "
                            f"엔드포인트: {len(self.configs)}개 | "
                            f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                            style="blue"
                        )
                    )

                    # 엔드포인트 상태 테이블
                    endpoints_table = self._create_endpoints_table()
                    layout["endpoints"].update(Panel(endpoints_table, title="엔드포인트 상태"))

                    # 통계 테이블
                    stats_table = self._create_statistics_table()
                    layout["statistics"].update(Panel(stats_table, title="통계"))

                    # 향상된 그래프 패널
                    graph_content = self._create_sparkline_panel()
                    layout["graphs"].update(Panel(Text.from_markup(graph_content), title="[bold cyan]📈 Performance Graphs[/bold cyan]", border_style="cyan"))

                    # 푸터
                    layout["footer"].update(
                        Panel(
                            "[dim]Ctrl+C를 눌러 모니터링을 중단하세요[/dim]",
                            style="dim"
                        )
                    )

                    await asyncio.sleep(0.5)

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    # 에러 처리
                    pass

    def _create_endpoints_table(self) -> Table:
        """엔드포인트 상태 테이블 생성"""
        table = Table(show_header=True, header_style="bold magenta", expand=True)

        # 터미널 너비에 따른 동적 컬럼 너비 설정
        terminal_width = self.console.width
        # 전체 테이블 너비의 비율로 컬럼 너비 할당
        name_width = max(15, int(terminal_width * 0.10))
        url_width = max(30, int(terminal_width * 0.25))  # URL에 더 많은 공간 할당

        table.add_column("이름", style="cyan", no_wrap=True, width=name_width)
        table.add_column("URL", style="blue", width=url_width)
        table.add_column("상태", justify="center", width=10)
        table.add_column("응답시간", justify="right", width=12)
        table.add_column("마지막 체크", justify="center", width=10)

        for config in self.configs:
            name = config.name
            recent_results = self.get_recent_results(name, 1)

            if recent_results:
                result = recent_results[0]

                # 상태 표시
                if result.success:
                    status = "[green]✅ 정상[/green]"
                    status_code = f"[green]{result.status_code}[/green]"
                else:
                    status = "[red]❌ 실패[/red]"
                    status_code = f"[red]{result.status_code or 'Error'}[/red]"

                # 응답 시간 표시
                response_time = f"{result.response_time:.3f}s"
                if result.response_time > 2.0:
                    response_time = f"[red]{response_time}[/red]"
                elif result.response_time > 1.0:
                    response_time = f"[yellow]{response_time}[/yellow]"
                else:
                    response_time = f"[green]{response_time}[/green]"

                # 마지막 체크 시간
                last_check = result.timestamp.strftime("%H:%M:%S")

            else:
                status = "[dim]대기중[/dim]"
                response_time = "-"
                last_check = "-"

            # URL 표시 - 터미널 너비에 맞게 동적 조정
            terminal_width = self.console.width
            max_url_length = max(30, int(terminal_width * 0.45) - 5)
            display_url = config.url
            if len(display_url) > max_url_length:
                display_url = display_url[:max_url_length-3] + "..."

            table.add_row(
                name,
                display_url,
                status,
                response_time,
                last_check
            )

        return table

    def _create_statistics_table(self) -> Table:
        """통계 테이블 생성"""
        table = Table(show_header=True, header_style="bold green", expand=True)

        # 터미널 너비에 따른 동적 컬럼 너비 설정
        terminal_width = self.console.width
        name_width = max(12, int(terminal_width * 0.1))

        table.add_column("엔드포인트", style="cyan", width=name_width)
        table.add_column("총 요청", justify="right", width=8)
        table.add_column("성공률", justify="right", width=10)
        table.add_column("평균 응답시간", justify="right", width=14)
        table.add_column("최소/최대", justify="right", width=18)

        for name, stats in self.statistics.items():
            if stats['total_requests'] == 0:
                continue

            # 성공률 색상
            uptime = stats['uptime_percentage']
            if uptime >= 99:
                uptime_display = f"[green]{uptime:.1f}%[/green]"
            elif uptime >= 95:
                uptime_display = f"[yellow]{uptime:.1f}%[/yellow]"
            else:
                uptime_display = f"[red]{uptime:.1f}%[/red]"

            # 평균 응답시간 색상
            avg_time = stats['avg_response_time']
            if avg_time < 1.0:
                avg_display = f"[green]{avg_time:.3f}s[/green]"
            elif avg_time < 2.0:
                avg_display = f"[yellow]{avg_time:.3f}s[/yellow]"
            else:
                avg_display = f"[red]{avg_time:.3f}s[/red]"

            # 최소/최대 응답시간
            min_time = stats['min_response_time']
            max_time = stats['max_response_time']

            if min_time == float('inf'):
                min_max_display = "-"
            else:
                min_max_display = f"{min_time:.2f}/{max_time:.2f}s"

            # 이름 길이 제한
            display_name = name
            max_name_length = max(12, int(terminal_width * 0.25) - 2)
            if len(display_name) > max_name_length:
                display_name = display_name[:max_name_length-3] + "..."

            table.add_row(
                display_name,
                str(stats['total_requests']),
                uptime_display,
                avg_display,
                min_max_display
            )

        return table

    def create_sparkline(self, data: List[float], width: int = 40, height: int = 4) -> str:
        """응답 시간 데이터를 sparkline으로 변환 - 색상과 함께"""
        if not data or len(data) < 2:
            return "데이터 수집 중..."

        # 더 세밀한 블록 문자
        blocks = " ▁▂▃▄▅▆▇█"

        # 데이터 정규화
        min_val = min(data)
        max_val = max(data)

        if min_val == max_val:
            return blocks[4] * min(width, len(data))

        range_val = max_val - min_val

        # 너비에 맞게 리샘플링 및 확장
        if len(data) > width:
            step = len(data) / width
            sampled_data = []
            for i in range(width):
                idx = int(i * step)
                sampled_data.append(data[idx])
        elif len(data) < width:
            # 선형 보간으로 데이터를 width 크기로 확장
            if len(data) >= 2:
                sampled_data = []
                for i in range(width):
                    pos = (i / (width - 1)) * (len(data) - 1) if width > 1 else 0
                    idx = int(pos)
                    if idx < len(data) - 1:
                        frac = pos - idx
                        val = data[idx] * (1 - frac) + data[idx + 1] * frac
                        sampled_data.append(val)
                    else:
                        sampled_data.append(data[-1])
            else:
                # 데이터가 1개면 전체 너비로 반복
                sampled_data = [data[0] if data else 0] * width
        else:
            sampled_data = data

        # sparkline 생성 - 값에 따른 색상 적용
        sparkline = ""
        for val in sampled_data:
            normalized = (val - min_val) / range_val if range_val > 0 else 0
            block_idx = int(normalized * (len(blocks) - 1))
            block = blocks[block_idx]

            # 응답 시간에 따른 색상
            if val < 0.5:
                sparkline += f"[bright_green]{block}[/bright_green]"
            elif val < 1.0:
                sparkline += f"[green]{block}[/green]"
            elif val < 2.0:
                sparkline += f"[yellow]{block}[/yellow]"
            elif val < 3.0:
                sparkline += f"[bright_yellow]{block}[/bright_yellow]"
            else:
                sparkline += f"[red]{block}[/red]"

        return sparkline

    def create_ascii_graph(self, data: List[float], width: int = 50, height: int = 6, label: str = "") -> str:
        """멀티라인 ASCII 그래프 생성 - 더 높은 가시성"""
        if not data or height < 2:
            return "데이터 수집 중..."

        # 데이터를 정확히 width 크기로 조정
        original_data = data[:]
        if len(data) > width:
            # 다운샘플링
            step = len(data) / width
            sampled = []
            for i in range(width):
                idx = int(i * step)
                sampled.append(data[idx])
            data = sampled
        elif len(data) < width:
            # 선형 보간으로 데이터 확장
            if len(data) >= 2:
                # 수동 선형 보간
                expanded = []
                for i in range(width):
                    # 현재 위치를 원본 데이터 인덱스로 매핑
                    pos = (i / (width - 1)) * (len(data) - 1) if width > 1 else 0
                    idx = int(pos)

                    if idx < len(data) - 1:
                        # 두 점 사이를 보간
                        frac = pos - idx
                        val = data[idx] * (1 - frac) + data[idx + 1] * frac
                        expanded.append(val)
                    else:
                        expanded.append(data[-1])
                data = expanded
            else:
                # 데이터가 1개면 반복
                data = data * width if data else [0] * width

        # 최소/최대값 계산
        min_val = min(data) if data else 0
        max_val = max(data) if data else 0

        if max_val == min_val:
            max_val = min_val + 1  # 0으로 나누기 방지

        # 그래프 생성
        graph_lines = []

        # 제목 추가 (있을 경우)
        if label:
            graph_lines.append(f"[bold cyan]{label}[/bold cyan]")
            graph_lines.append("")

        # 그래프 문자 세트 (더 부드러운 그래프)
        graph_chars = "▁▂▃▄▅▆▇█"

        # Y축 라벨과 그래프 생성
        for h in range(height, 0, -1):
            line = ""

            # Y축 라벨 - 더 명확한 포맷
            if h == height:
                y_label = f"[dim]{max_val:6.3f}s[/dim] ┤"
            elif h == 1:
                y_label = f"[dim]{min_val:6.3f}s[/dim] ┤"
            elif h == height // 2 + 1:
                mid_val = (max_val + min_val) / 2
                y_label = f"[dim]{mid_val:6.3f}s[/dim] ┤"
            else:
                y_label = "         │"

            line = y_label

            # 데이터 포인트 그리기 - 전체 width 사용
            for i in range(width):
                if i < len(data):
                    val = data[i]
                    if max_val > min_val:
                        normalized_val = (val - min_val) / (max_val - min_val)
                    else:
                        normalized_val = 0.5

                    # 높이에 대한 정규화
                    bar_height = normalized_val * height

                    if bar_height >= h - 0.5:
                        # 더 세밀한 표현을 위해 그래프 문자 선택
                        char_idx = min(int((bar_height - (h - 1)) * len(graph_chars)), len(graph_chars) - 1)
                        char = graph_chars[char_idx]

                        # 값에 따른 색상 적용
                        if val < 0.5:
                            line += f"[bright_green]{char}[/bright_green]"
                        elif val < 1.0:
                            line += f"[green]{char}[/green]"
                        elif val < 2.0:
                            line += f"[yellow]{char}[/yellow]"
                        elif val < 3.0:
                            line += f"[bright_yellow]{char}[/bright_yellow]"
                        else:
                            line += f"[red]{char}[/red]"
                    else:
                        line += " "
                else:
                    line += " "

            graph_lines.append(line)

        # X축 그리기 - 전체 width 사용
        graph_lines.append("         └" + "─" * width)

        # 시간 축 라벨
        if len(data) >= 2:
            time_label = f"        {label} (최근 {len(data)}개 데이터)"
            graph_lines.append(time_label)

        return "\n".join(graph_lines)

    def create_status_sparkline(self, data: List[int], width: int = 40) -> str:
        """상태 히스토리를 sparkline으로 변환 - 더 세밀한 표현"""
        if not data:
            return "데이터 수집 중..."

        # 너비에 맞게 리샘플링 및 확장
        if len(data) > width:
            step = len(data) / width
            sampled_data = []
            for i in range(width):
                idx = int(i * step)
                sampled_data.append(data[idx])
        elif len(data) < width:
            # 선형 보간으로 데이터를 width 크기로 확장
            if len(data) >= 2:
                sampled_data = []
                for i in range(width):
                    pos = (i / (width - 1)) * (len(data) - 1) if width > 1 else 0
                    idx = int(pos)
                    frac = pos - idx
                    if idx < len(data) - 1:
                        # 이진 데이터이므로 보간 대신 가장 가까운 값 사용
                        sampled_data.append(data[idx] if frac < 0.5 else data[idx + 1])
                    else:
                        sampled_data.append(data[-1])
            else:
                # 데이터가 1개면 전체 너비로 반복
                sampled_data = [data[0] if data else 0] * width
        else:
            sampled_data = data

        # 더 세밀한 상태 표현을 위한 문자 세트
        success_chars = "▁▂▃▄▅▆▇█"
        fail_char = "✗"

        # 상태별 색상 적용
        sparkline = ""
        for i, status in enumerate(sampled_data):
            if status == 1:
                # 연속 성공에 따른 다른 표현
                consecutive_success = 0
                for j in range(max(0, i - 3), i + 1):
                    if j < len(sampled_data) and sampled_data[j] == 1:
                        consecutive_success += 1

                char_idx = min(consecutive_success * 2, len(success_chars) - 1)
                sparkline += f"[bright_green]{success_chars[char_idx]}[/bright_green]"
            else:
                sparkline += f"[red]{fail_char}[/red]"

        return sparkline

    def create_status_bar_graph(self, data: List[int], width: int = 50, height: int = 3) -> str:
        """상태 히스토리를 막대 그래프로 변환 - 향상된 시각화"""
        if not data:
            return "데이터 수집 중..."

        # 데이터를 정확히 width 크기로 조정
        if len(data) > width:
            # 구간별 집계
            step = len(data) / width
            aggregated = []
            for i in range(width):
                start_idx = int(i * step)
                end_idx = int((i + 1) * step)
                section = data[start_idx:end_idx]
                success_rate = sum(section) / len(section) if section else 0
                aggregated.append(success_rate)
        else:
            # 데이터 확장 - width에 맞게 보간
            aggregated = []
            if len(data) >= 2:
                # 선형 보간
                for i in range(width):
                    pos = (i / (width - 1)) * (len(data) - 1) if width > 1 else 0
                    idx = int(pos)
                    if idx < len(data) - 1:
                        frac = pos - idx
                        val = data[idx] * (1 - frac) + data[idx + 1] * frac
                        aggregated.append(val)
                    else:
                        aggregated.append(float(data[-1]) if data else 1.0)
            else:
                # 데이터가 1개면 전체 너비로 반복
                aggregated = [float(data[0]) if data else 1.0] * width

        # 그래프 생성 - 더 세밀한 표현
        lines = []
        chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

        # 제목 추가
        lines.append("")

        for h in range(height, 0, -1):
            line = ""
            threshold = (h - 0.5) / height

            # 전체 width 사용
            for i in range(width):
                if i < len(aggregated):
                    rate = aggregated[i]
                else:
                    rate = 0

                if rate >= threshold:
                    # 성공률에 따른 문자와 색상 선택
                    char_idx = min(int(rate * len(chars)), len(chars) - 1)
                    char = chars[char_idx]

                    if rate >= 0.99:
                        line += f"[bright_green]{char}[/bright_green]"
                    elif rate >= 0.95:
                        line += f"[green]{char}[/green]"
                    elif rate >= 0.90:
                        line += f"[yellow]{char}[/yellow]"
                    elif rate >= 0.80:
                        line += f"[bright_yellow]{char}[/bright_yellow]"
                    else:
                        line += f"[red]{char}[/red]"
                else:
                    line += " "

            lines.append(line)

        return "\n".join(lines)

    def _create_sparkline_panel(self) -> str:
        """향상된 그래프 패널 생성"""
        lines = []

        # 터미널 너비를 다시 확인하여 최신 값 사용
        current_width = self.console.width
        # 그래프 너비를 터미널 너비의 80%로 설정 (최소 60, 최대 200)
        graph_width = max(60, min(int(current_width * 0.8), 200))
        # 구분선 너비는 터미널 너비의 90%
        separator_width = min(int(current_width * 0.9), 200)

        # 디버그: 실제 사용되는 너비 표시
        lines.append(f"[dim]Terminal Width: {current_width} | Graph Width: {graph_width}[/dim]")
        lines.append("")

        for config in self.configs:
            name = config.name

            # 엔드포인트 이름
            lines.append(f"[bold cyan]{'═' * separator_width}[/bold cyan]")
            lines.append(f"[bold cyan]📊 {name}[/bold cyan]")
            lines.append("")

            # 응답 시간 ASCII 그래프 (높은 가시성)
            response_times = list(self.response_time_history.get(name, []))
            if response_times:
                # 멀티라인 그래프 생성
                ascii_graph = self.create_ascii_graph(
                    response_times,
                    width=graph_width,
                    height=8,  # 높이도 약간 증가
                    label="응답 시간"
                )
                lines.append("[bold]Response Time Graph:[/bold]")
                lines.append(ascii_graph)

                # 통계 정보
                latest = response_times[-1] if response_times else 0
                avg = sum(response_times) / len(response_times) if response_times else 0
                min_val = min(response_times) if response_times else 0
                max_val = max(response_times) if response_times else 0

                # 색상 적용
                if latest < 1.0:
                    latest_str = f"[green]{latest:.3f}s[/green]"
                elif latest < 2.0:
                    latest_str = f"[yellow]{latest:.3f}s[/yellow]"
                else:
                    latest_str = f"[red]{latest:.3f}s[/red]"

                lines.append("")
                lines.append(f"  📈 현재: {latest_str} | 평균: {avg:.3f}s | 최소: {min_val:.3f}s | 최대: {max_val:.3f}s")

                # 작은 sparkline도 함께 표시 (보조 지표)
                sparkline = self.create_sparkline(response_times, width=graph_width)
                lines.append(f"  Trend: {sparkline}")
                lines.append("")

                # 상태 막대 그래프
                statuses = list(self.status_history.get(name, []))
                if statuses:
                    lines.append("[bold]Success Rate:[/bold]")
                    status_bar = self.create_status_bar_graph(statuses, width=graph_width, height=4)
                    lines.append(status_bar)

                    success_rate = (sum(statuses) / len(statuses)) * 100 if statuses else 0

                    if success_rate >= 99:
                        rate_str = f"[green]{success_rate:.1f}%[/green]"
                    elif success_rate >= 95:
                        rate_str = f"[yellow]{success_rate:.1f}%[/yellow]"
                    else:
                        rate_str = f"[red]{success_rate:.1f}%[/red]"

                    # 상태 sparkline (보조)
                    status_sparkline = self.create_status_sparkline(statuses, width=graph_width)
                    lines.append("")
                    lines.append(f"  Status: {status_sparkline}")
                    lines.append(f"  📊 성공률: {rate_str} ({sum(statuses)}/{len(statuses)})")

                lines.append("")  # 빈 줄 추가

        return "\n".join(lines) if lines else "모니터링 데이터 수집 중..."

    def export_results(self, filename: str, format: str = "json"):
        """결과를 파일로 내보내기"""
        if format.lower() == "json":
            data = {
                "timestamp": datetime.now().isoformat(),
                "statistics": self.statistics,
                "results": {}
            }

            for name, results in self.results.items():
                data["results"][name] = [
                    {
                        "timestamp": r.timestamp.isoformat(),
                        "url": r.url,
                        "method": r.method,
                        "status_code": r.status_code,
                        "response_time": r.response_time,
                        "success": r.success,
                        "error": r.error,
                        "content_length": r.content_length
                    }
                    for r in results
                ]

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        else:
            raise ValueError(f"Unsupported format: {format}")


# 편의 함수들
async def monitor_single_url(
    url: str,
    method: str = "GET",
    interval: float = 1.0,
    duration: Optional[float] = None,
    dashboard: bool = True,
    **kwargs
) -> HTTPMonitor:
    """단일 URL 모니터링"""
    config = HTTPMonitorConfig(
        url=url,
        method=method,
        interval=interval,
        **kwargs
    )

    monitor = HTTPMonitor()
    monitor.add_endpoint(config)

    if duration:
        # 지정된 시간 동안만 실행
        async def timed_monitoring():
            monitoring_task = asyncio.create_task(monitor.start_monitoring(dashboard))
            await asyncio.sleep(duration)
            await monitor.stop_monitoring()

        await timed_monitoring()
    else:
        await monitor.start_monitoring(dashboard)

    return monitor


async def monitor_multiple_urls(
    configs: List[HTTPMonitorConfig],
    dashboard: bool = True
) -> HTTPMonitor:
    """여러 URL 동시 모니터링"""
    monitor = HTTPMonitor()

    for config in configs:
        monitor.add_endpoint(config)

    await monitor.start_monitoring(dashboard)
    return monitor
