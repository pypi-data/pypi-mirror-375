"""
성능 측정 및 벤치마킹 모듈

HTTP 요청 성능, 메모리 사용량, 시스템 리소스를 측정하고 벤치마크를 제공합니다.
"""

import asyncio
import time
import psutil
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Union
from datetime import datetime, timedelta
from collections import defaultdict, deque

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text

from pawnstack.http_client.client import HttpClient


@dataclass
class BenchmarkResult:
    """벤치마크 결과"""
    name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_time: float
    requests_per_second: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    percentiles: Dict[int, float]  # 50th, 90th, 95th, 99th percentiles
    error_rate: float
    throughput_bytes_per_sec: float
    memory_usage: Dict[str, float]  # peak, average memory usage
    cpu_usage: Dict[str, float]  # peak, average CPU usage
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PerformanceMetrics:
    """성능 메트릭"""
    timestamp: datetime
    response_time: float
    status_code: Optional[int]
    content_length: int
    memory_usage_mb: float
    cpu_percent: float
    success: bool
    error: Optional[str] = None


class PerformanceMonitor:
    """
    성능 모니터링 및 벤치마킹 클래스

    HTTP 요청 성능, 시스템 리소스 사용량을 측정하고 벤치마크를 수행합니다.
    """

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.client = HttpClient()
        self.metrics_history: deque = deque(maxlen=10000)
        self.benchmark_results: List[BenchmarkResult] = []
        self.baseline_metrics: Optional[Dict[str, float]] = None

    def set_baseline(self, metrics: Dict[str, float]):
        """성능 기준선 설정"""
        self.baseline_metrics = metrics.copy()
        self.console.print(f"[green]성능 기준선이 설정되었습니다: {metrics}[/green]")

    def clear_baseline(self):
        """성능 기준선 제거"""
        self.baseline_metrics = None
        self.console.print("[yellow]성능 기준선이 제거되었습니다.[/yellow]")

    async def measure_single_request(
        self,
        url: str,
        method: str = "GET",
        **kwargs
    ) -> PerformanceMetrics:
        """단일 요청 성능 측정"""
        # 시작 시점 메모리/CPU 측정
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        start_cpu = process.cpu_percent()

        start_time = time.time()

        try:
            response = await self.client.request(method, url, **kwargs)

            end_time = time.time()
            response_time = end_time - start_time

            # 종료 시점 메모리/CPU 측정
            end_memory = process.memory_info().rss / 1024 / 1024  # MB
            end_cpu = process.cpu_percent()

            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                response_time=response_time,
                status_code=response.status_code,
                content_length=len(response.content) if response.content else 0,
                memory_usage_mb=max(start_memory, end_memory),
                cpu_percent=max(start_cpu, end_cpu),
                success=200 <= response.status_code < 300
            )

        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time

            end_memory = process.memory_info().rss / 1024 / 1024  # MB
            end_cpu = process.cpu_percent()

            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                response_time=response_time,
                status_code=None,
                content_length=0,
                memory_usage_mb=max(start_memory, end_memory),
                cpu_percent=max(start_cpu, end_cpu),
                success=False,
                error=str(e)
            )

        # 메트릭 히스토리에 저장
        self.metrics_history.append(metrics)

        return metrics

    async def run_benchmark(
        self,
        name: str,
        url: str,
        method: str = "GET",
        concurrent_requests: int = 10,
        total_requests: int = 100,
        duration: Optional[float] = None,
        warmup_requests: int = 10,
        **kwargs
    ) -> BenchmarkResult:
        """
        HTTP 벤치마크 실행

        Args:
            name: 벤치마크 이름
            url: 테스트할 URL
            method: HTTP 메서드
            concurrent_requests: 동시 요청 수
            total_requests: 총 요청 수 (duration이 None인 경우)
            duration: 실행 시간(초) (total_requests 대신 사용 가능)
            warmup_requests: 워밍업 요청 수
            **kwargs: HTTP 요청 추가 파라미터
        """
        self.console.print(f"[blue]벤치마크 시작: {name}[/blue]")

        # 워밍업
        if warmup_requests > 0:
            self.console.print(f"[yellow]워밍업 중... ({warmup_requests}개 요청)[/yellow]")
            warmup_tasks = [
                self.measure_single_request(url, method, **kwargs)
                for _ in range(warmup_requests)
            ]
            await asyncio.gather(*warmup_tasks, return_exceptions=True)

        # 벤치마크 실행
        start_time = time.time()
        metrics_list: List[PerformanceMetrics] = []

        # 시스템 리소스 모니터링 시작
        resource_monitor_task = asyncio.create_task(
            self._monitor_system_resources(duration or (total_requests / concurrent_requests * 2))
        )

        if duration:
            # 시간 기반 벤치마크
            end_time = start_time + duration
            request_count = 0

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task(f"벤치마크 실행: {name}", total=100)

                while time.time() < end_time:
                    # 동시 요청 실행
                    batch_tasks = [
                        self.measure_single_request(url, method, **kwargs)
                        for _ in range(concurrent_requests)
                    ]

                    batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                    for result in batch_results:
                        if isinstance(result, PerformanceMetrics):
                            metrics_list.append(result)
                            request_count += 1

                    # 진행률 업데이트
                    elapsed = time.time() - start_time
                    progress.update(task, completed=(elapsed / duration) * 100)

                    # 짧은 대기 (과부하 방지)
                    await asyncio.sleep(0.01)

        else:
            # 요청 수 기반 벤치마크
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task(f"벤치마크 실행: {name}", total=total_requests)

                completed = 0
                while completed < total_requests:
                    # 배치 크기 계산
                    batch_size = min(concurrent_requests, total_requests - completed)

                    # 동시 요청 실행
                    batch_tasks = [
                        self.measure_single_request(url, method, **kwargs)
                        for _ in range(batch_size)
                    ]

                    batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                    for result in batch_results:
                        if isinstance(result, PerformanceMetrics):
                            metrics_list.append(result)
                            completed += 1
                            progress.update(task, completed=completed)

        # 시스템 리소스 모니터링 중단
        resource_monitor_task.cancel()
        try:
            resource_stats = await resource_monitor_task
        except asyncio.CancelledError:
            resource_stats = {"memory": {"peak": 0, "average": 0}, "cpu": {"peak": 0, "average": 0}}

        total_time = time.time() - start_time

        # 결과 분석
        result = self._analyze_benchmark_results(name, metrics_list, total_time, resource_stats)
        self.benchmark_results.append(result)

        # 결과 출력
        self._display_benchmark_result(result)

        return result

    async def _monitor_system_resources(self, duration: float) -> Dict[str, Dict[str, float]]:
        """시스템 리소스 모니터링"""
        process = psutil.Process()
        memory_samples = []
        cpu_samples = []

        start_time = time.time()

        try:
            while time.time() - start_time < duration:
                memory_mb = process.memory_info().rss / 1024 / 1024
                cpu_percent = process.cpu_percent()

                memory_samples.append(memory_mb)
                cpu_samples.append(cpu_percent)

                await asyncio.sleep(0.1)  # 100ms 간격으로 샘플링

        except asyncio.CancelledError:
            pass

        return {
            "memory": {
                "peak": max(memory_samples) if memory_samples else 0,
                "average": statistics.mean(memory_samples) if memory_samples else 0
            },
            "cpu": {
                "peak": max(cpu_samples) if cpu_samples else 0,
                "average": statistics.mean(cpu_samples) if cpu_samples else 0
            }
        }

    def _analyze_benchmark_results(
        self,
        name: str,
        metrics_list: List[PerformanceMetrics],
        total_time: float,
        resource_stats: Dict[str, Dict[str, float]]
    ) -> BenchmarkResult:
        """벤치마크 결과 분석"""
        if not metrics_list:
            return BenchmarkResult(
                name=name,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                total_time=total_time,
                requests_per_second=0,
                avg_response_time=0,
                min_response_time=0,
                max_response_time=0,
                percentiles={},
                error_rate=100.0,
                throughput_bytes_per_sec=0,
                memory_usage=resource_stats.get("memory", {}),
                cpu_usage=resource_stats.get("cpu", {})
            )

        # 기본 통계
        total_requests = len(metrics_list)
        successful_requests = sum(1 for m in metrics_list if m.success)
        failed_requests = total_requests - successful_requests

        # 응답 시간 분석
        response_times = [m.response_time for m in metrics_list]
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)

        # 백분위수 계산
        percentiles = {}
        for p in [50, 90, 95, 99]:
            try:
                percentiles[p] = statistics.quantiles(response_times, n=100)[p-1]
            except:
                percentiles[p] = 0

        # 처리량 계산
        requests_per_second = total_requests / total_time if total_time > 0 else 0

        # 데이터 처리량 계산
        total_bytes = sum(m.content_length for m in metrics_list)
        throughput_bytes_per_sec = total_bytes / total_time if total_time > 0 else 0

        # 에러율 계산
        error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0

        return BenchmarkResult(
            name=name,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            total_time=total_time,
            requests_per_second=requests_per_second,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            percentiles=percentiles,
            error_rate=error_rate,
            throughput_bytes_per_sec=throughput_bytes_per_sec,
            memory_usage=resource_stats.get("memory", {}),
            cpu_usage=resource_stats.get("cpu", {})
        )

    def _display_benchmark_result(self, result: BenchmarkResult):
        """벤치마크 결과 출력"""
        table = Table(title=f"벤치마크 결과: {result.name}")
        table.add_column("메트릭", style="cyan", no_wrap=True)
        table.add_column("값", style="magenta")

        # 기본 통계
        table.add_row("총 요청 수", f"{result.total_requests:,}")
        table.add_row("성공 요청", f"{result.successful_requests:,}")
        table.add_row("실패 요청", f"{result.failed_requests:,}")
        table.add_row("총 실행 시간", f"{result.total_time:.2f}초")
        table.add_row("초당 요청 수 (RPS)", f"{result.requests_per_second:.2f}")
        table.add_row("에러율", f"{result.error_rate:.2f}%")

        # 응답 시간 통계
        table.add_row("", "")  # 구분선
        table.add_row("평균 응답시간", f"{result.avg_response_time:.3f}초")
        table.add_row("최소 응답시간", f"{result.min_response_time:.3f}초")
        table.add_row("최대 응답시간", f"{result.max_response_time:.3f}초")

        # 백분위수
        for p, value in result.percentiles.items():
            table.add_row(f"{p}th 백분위수", f"{value:.3f}초")

        # 처리량
        table.add_row("", "")  # 구분선
        table.add_row("데이터 처리량", f"{result.throughput_bytes_per_sec / 1024:.2f} KB/s")

        # 시스템 리소스
        if result.memory_usage:
            table.add_row("", "")  # 구분선
            table.add_row("최대 메모리 사용량", f"{result.memory_usage.get('peak', 0):.2f} MB")
            table.add_row("평균 메모리 사용량", f"{result.memory_usage.get('average', 0):.2f} MB")

        if result.cpu_usage:
            table.add_row("최대 CPU 사용률", f"{result.cpu_usage.get('peak', 0):.2f}%")
            table.add_row("평균 CPU 사용률", f"{result.cpu_usage.get('average', 0):.2f}%")

        self.console.print(table)

        # 성능 기준선과 비교
        if self.baseline_metrics:
            self._compare_with_baseline(result)

    def _compare_with_baseline(self, result: BenchmarkResult):
        """성능 기준선과 비교"""
        baseline = self.baseline_metrics

        comparison_table = Table(title="기준선 대비 성능 비교")
        comparison_table.add_column("메트릭", style="cyan")
        comparison_table.add_column("현재", style="magenta")
        comparison_table.add_column("기준선", style="blue")
        comparison_table.add_column("변화", style="green")

        # RPS 비교
        if "requests_per_second" in baseline:
            baseline_rps = baseline["requests_per_second"]
            current_rps = result.requests_per_second
            change = ((current_rps - baseline_rps) / baseline_rps * 100) if baseline_rps > 0 else 0

            change_text = f"{change:+.1f}%"
            if change > 5:
                change_text = f"[green]{change_text}[/green]"
            elif change < -5:
                change_text = f"[red]{change_text}[/red]"
            else:
                change_text = f"[yellow]{change_text}[/yellow]"

            comparison_table.add_row(
                "초당 요청 수",
                f"{current_rps:.2f}",
                f"{baseline_rps:.2f}",
                change_text
            )

        # 평균 응답시간 비교
        if "avg_response_time" in baseline:
            baseline_time = baseline["avg_response_time"]
            current_time = result.avg_response_time
            change = ((current_time - baseline_time) / baseline_time * 100) if baseline_time > 0 else 0

            change_text = f"{change:+.1f}%"
            if change < -5:  # 응답시간은 낮을수록 좋음
                change_text = f"[green]{change_text}[/green]"
            elif change > 5:
                change_text = f"[red]{change_text}[/red]"
            else:
                change_text = f"[yellow]{change_text}[/yellow]"

            comparison_table.add_row(
                "평균 응답시간",
                f"{current_time:.3f}s",
                f"{baseline_time:.3f}s",
                change_text
            )

        self.console.print(comparison_table)

    def get_performance_summary(self, last_n_minutes: int = 60) -> Dict[str, Any]:
        """최근 N분간의 성능 요약"""
        cutoff_time = datetime.now() - timedelta(minutes=last_n_minutes)
        recent_metrics = [
            m for m in self.metrics_history
            if m.timestamp >= cutoff_time
        ]

        if not recent_metrics:
            return {}

        response_times = [m.response_time for m in recent_metrics]
        successful_requests = sum(1 for m in recent_metrics if m.success)

        return {
            "period_minutes": last_n_minutes,
            "total_requests": len(recent_metrics),
            "successful_requests": successful_requests,
            "success_rate": (successful_requests / len(recent_metrics) * 100),
            "avg_response_time": statistics.mean(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times),
            "avg_memory_usage": statistics.mean([m.memory_usage_mb for m in recent_metrics]),
            "avg_cpu_usage": statistics.mean([m.cpu_percent for m in recent_metrics])
        }

    def detect_performance_regression(self, threshold_percent: float = 10.0) -> List[str]:
        """성능 회귀 감지"""
        if not self.baseline_metrics or len(self.benchmark_results) < 2:
            return []

        latest_result = self.benchmark_results[-1]
        regressions = []

        # RPS 회귀 검사
        if "requests_per_second" in self.baseline_metrics:
            baseline_rps = self.baseline_metrics["requests_per_second"]
            current_rps = latest_result.requests_per_second

            if baseline_rps > 0:
                change_percent = ((current_rps - baseline_rps) / baseline_rps) * 100
                if change_percent < -threshold_percent:
                    regressions.append(
                        f"RPS 성능 저하: {change_percent:.1f}% "
                        f"({baseline_rps:.2f} → {current_rps:.2f})"
                    )

        # 응답시간 회귀 검사
        if "avg_response_time" in self.baseline_metrics:
            baseline_time = self.baseline_metrics["avg_response_time"]
            current_time = latest_result.avg_response_time

            if baseline_time > 0:
                change_percent = ((current_time - baseline_time) / baseline_time) * 100
                if change_percent > threshold_percent:
                    regressions.append(
                        f"응답시간 성능 저하: {change_percent:.1f}% "
                        f"({baseline_time:.3f}s → {current_time:.3f}s)"
                    )

        return regressions

    def export_benchmark_results(self, filename: str):
        """벤치마크 결과를 파일로 내보내기"""
        import json

        data = {
            "export_timestamp": datetime.now().isoformat(),
            "baseline_metrics": self.baseline_metrics,
            "benchmark_results": []
        }

        for result in self.benchmark_results:
            data["benchmark_results"].append({
                "name": result.name,
                "timestamp": result.timestamp.isoformat(),
                "total_requests": result.total_requests,
                "successful_requests": result.successful_requests,
                "failed_requests": result.failed_requests,
                "total_time": result.total_time,
                "requests_per_second": result.requests_per_second,
                "avg_response_time": result.avg_response_time,
                "min_response_time": result.min_response_time,
                "max_response_time": result.max_response_time,
                "percentiles": result.percentiles,
                "error_rate": result.error_rate,
                "throughput_bytes_per_sec": result.throughput_bytes_per_sec,
                "memory_usage": result.memory_usage,
                "cpu_usage": result.cpu_usage
            })

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.console.print(f"[green]벤치마크 결과가 {filename}에 저장되었습니다.[/green]")


# 편의 함수들
async def quick_benchmark(
    url: str,
    name: Optional[str] = None,
    requests: int = 100,
    concurrency: int = 10,
    **kwargs
) -> BenchmarkResult:
    """빠른 벤치마크 실행"""
    monitor = PerformanceMonitor()

    benchmark_name = name or f"Quick benchmark: {url}"

    return await monitor.run_benchmark(
        name=benchmark_name,
        url=url,
        concurrent_requests=concurrency,
        total_requests=requests,
        **kwargs
    )


async def compare_endpoints(
    endpoints: List[Dict[str, Any]],
    requests_per_endpoint: int = 50,
    concurrency: int = 5
) -> List[BenchmarkResult]:
    """여러 엔드포인트 성능 비교"""
    monitor = PerformanceMonitor()
    results = []

    for endpoint in endpoints:
        name = endpoint.get('name', endpoint['url'])
        url = endpoint['url']
        method = endpoint.get('method', 'GET')

        result = await monitor.run_benchmark(
            name=name,
            url=url,
            method=method,
            concurrent_requests=concurrency,
            total_requests=requests_per_endpoint,
            **endpoint.get('kwargs', {})
        )

        results.append(result)

    # 비교 결과 출력
    comparison_table = Table(title="엔드포인트 성능 비교")
    comparison_table.add_column("엔드포인트", style="cyan")
    comparison_table.add_column("RPS", justify="right")
    comparison_table.add_column("평균 응답시간", justify="right")
    comparison_table.add_column("에러율", justify="right")
    comparison_table.add_column("P95 응답시간", justify="right")

    for result in results:
        p95 = result.percentiles.get(95, 0)
        comparison_table.add_row(
            result.name,
            f"{result.requests_per_second:.2f}",
            f"{result.avg_response_time:.3f}s",
            f"{result.error_rate:.1f}%",
            f"{p95:.3f}s"
        )

    console = Console()
    console.print(comparison_table)

    return results
