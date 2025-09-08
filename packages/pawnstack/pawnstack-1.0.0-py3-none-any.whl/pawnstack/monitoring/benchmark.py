"""
성능 벤치마킹 및 회귀 테스트 도구

HTTP 요청 성능 측정, 메모리 사용량 모니터링, 성능 회귀 테스트를 위한
벤치마크 기준 설정 및 비교 기능을 제공합니다.
"""

import asyncio
import json
import os
import time
import statistics
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.text import Text

from .performance import PerformanceMonitor, BenchmarkResult


@dataclass
class BenchmarkBaseline:
    """벤치마크 기준선"""
    name: str
    version: str
    timestamp: datetime
    metrics: Dict[str, float]
    environment: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None


@dataclass
class RegressionTestConfig:
    """회귀 테스트 설정"""
    name: str
    url: str
    method: str = "GET"
    requests: int = 100
    concurrency: int = 10
    timeout: float = 30.0
    acceptable_regression_percent: float = 10.0  # 허용 가능한 성능 저하 %
    critical_regression_percent: float = 25.0    # 심각한 성능 저하 %
    headers: Dict[str, str] = field(default_factory=dict)
    data: Union[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class RegressionTestResult:
    """회귀 테스트 결과"""
    config_name: str
    baseline: BenchmarkBaseline
    current_result: BenchmarkResult
    regression_detected: bool
    regression_severity: str  # "none", "acceptable", "critical"
    performance_changes: Dict[str, Dict[str, float]]  # metric -> {baseline, current, change_percent}
    timestamp: datetime = field(default_factory=datetime.now)


class BenchmarkManager:
    """
    벤치마크 관리 및 회귀 테스트 클래스

    성능 기준선 설정, 벤치마크 실행, 회귀 테스트를 관리합니다.
    """

    def __init__(self, baseline_dir: str = ".benchmarks", console: Optional[Console] = None):
        self.baseline_dir = Path(baseline_dir)
        self.baseline_dir.mkdir(exist_ok=True)
        self.console = console or Console()
        self.performance_monitor = PerformanceMonitor(console)
        self.baselines: Dict[str, BenchmarkBaseline] = {}
        self.regression_configs: Dict[str, RegressionTestConfig] = {}

        # 기존 기준선 로드
        self._load_baselines()

    def _load_baselines(self):
        """저장된 기준선들을 로드"""
        baseline_files = self.baseline_dir.glob("*.json")

        for baseline_file in baseline_files:
            try:
                with open(baseline_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                baseline = BenchmarkBaseline(
                    name=data['name'],
                    version=data['version'],
                    timestamp=datetime.fromisoformat(data['timestamp']),
                    metrics=data['metrics'],
                    environment=data.get('environment', {}),
                    description=data.get('description')
                )

                self.baselines[baseline.name] = baseline

            except Exception as e:
                self.console.print(f"[yellow]기준선 로드 실패 {baseline_file}: {e}[/yellow]")

    def create_baseline(
        self,
        name: str,
        version: str,
        url: str,
        method: str = "GET",
        requests: int = 200,
        concurrency: int = 10,
        description: Optional[str] = None,
        **kwargs
    ) -> BenchmarkBaseline:
        """새로운 성능 기준선 생성"""
        self.console.print(f"[blue]성능 기준선 생성 중: {name} (v{version})[/blue]")

        # 벤치마크 실행
        result = asyncio.run(
            self.performance_monitor.run_benchmark(
                name=f"{name}_baseline",
                url=url,
                method=method,
                concurrent_requests=concurrency,
                total_requests=requests,
                **kwargs
            )
        )

        # 환경 정보 수집
        import platform
        import psutil

        environment = {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "timestamp": datetime.now().isoformat()
        }

        # 기준선 메트릭 추출
        metrics = {
            "requests_per_second": result.requests_per_second,
            "avg_response_time": result.avg_response_time,
            "p95_response_time": result.percentiles.get(95, 0),
            "p99_response_time": result.percentiles.get(99, 0),
            "error_rate": result.error_rate,
            "throughput_bytes_per_sec": result.throughput_bytes_per_sec,
            "peak_memory_mb": result.memory_usage.get('peak', 0),
            "avg_memory_mb": result.memory_usage.get('average', 0),
            "peak_cpu_percent": result.cpu_usage.get('peak', 0),
            "avg_cpu_percent": result.cpu_usage.get('average', 0)
        }

        baseline = BenchmarkBaseline(
            name=name,
            version=version,
            timestamp=datetime.now(),
            metrics=metrics,
            environment=environment,
            description=description
        )

        # 기준선 저장
        self._save_baseline(baseline)
        self.baselines[name] = baseline

        self.console.print(f"[green]성능 기준선이 생성되었습니다: {name} (v{version})[/green]")
        self._display_baseline(baseline)

        return baseline

    def _save_baseline(self, baseline: BenchmarkBaseline):
        """기준선을 파일로 저장"""
        filename = self.baseline_dir / f"{baseline.name}_{baseline.version}.json"

        data = {
            "name": baseline.name,
            "version": baseline.version,
            "timestamp": baseline.timestamp.isoformat(),
            "metrics": baseline.metrics,
            "environment": baseline.environment,
            "description": baseline.description
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _display_baseline(self, baseline: BenchmarkBaseline):
        """기준선 정보 출력"""
        table = Table(title=f"성능 기준선: {baseline.name} v{baseline.version}")
        table.add_column("메트릭", style="cyan")
        table.add_column("값", style="magenta")

        table.add_row("생성 시간", baseline.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        if baseline.description:
            table.add_row("설명", baseline.description)

        table.add_row("", "")  # 구분선

        # 성능 메트릭
        metrics_display = {
            "requests_per_second": ("초당 요청 수", "RPS"),
            "avg_response_time": ("평균 응답시간", "초"),
            "p95_response_time": ("95th 백분위수", "초"),
            "p99_response_time": ("99th 백분위수", "초"),
            "error_rate": ("에러율", "%"),
            "throughput_bytes_per_sec": ("처리량", "bytes/s"),
            "peak_memory_mb": ("최대 메모리", "MB"),
            "avg_memory_mb": ("평균 메모리", "MB"),
            "peak_cpu_percent": ("최대 CPU", "%"),
            "avg_cpu_percent": ("평균 CPU", "%")
        }

        for key, (label, unit) in metrics_display.items():
            if key in baseline.metrics:
                value = baseline.metrics[key]
                if key.endswith("_time"):
                    table.add_row(label, f"{value:.3f} {unit}")
                elif key.endswith("_rate") or key.endswith("_percent"):
                    table.add_row(label, f"{value:.2f} {unit}")
                elif key == "throughput_bytes_per_sec":
                    table.add_row(label, f"{value/1024:.2f} KB/s")
                else:
                    table.add_row(label, f"{value:.2f} {unit}")

        self.console.print(table)

    def list_baselines(self) -> List[BenchmarkBaseline]:
        """저장된 기준선 목록 반환"""
        return list(self.baselines.values())

    def get_baseline(self, name: str) -> Optional[BenchmarkBaseline]:
        """특정 기준선 반환"""
        return self.baselines.get(name)

    def delete_baseline(self, name: str, version: Optional[str] = None):
        """기준선 삭제"""
        if name not in self.baselines:
            self.console.print(f"[red]기준선을 찾을 수 없습니다: {name}[/red]")
            return

        baseline = self.baselines[name]

        # 파일 삭제
        if version:
            filename = self.baseline_dir / f"{name}_{version}.json"
        else:
            filename = self.baseline_dir / f"{name}_{baseline.version}.json"

        if filename.exists():
            filename.unlink()

        # 메모리에서 제거
        del self.baselines[name]

        self.console.print(f"[green]기준선이 삭제되었습니다: {name}[/green]")

    def add_regression_test(self, config: RegressionTestConfig):
        """회귀 테스트 설정 추가"""
        self.regression_configs[config.name] = config
        self.console.print(f"[green]회귀 테스트가 추가되었습니다: {config.name}[/green]")

    def remove_regression_test(self, name: str):
        """회귀 테스트 설정 제거"""
        if name in self.regression_configs:
            del self.regression_configs[name]
            self.console.print(f"[green]회귀 테스트가 제거되었습니다: {name}[/green]")
        else:
            self.console.print(f"[red]회귀 테스트를 찾을 수 없습니다: {name}[/red]")

    async def run_regression_test(self, test_name: str) -> RegressionTestResult:
        """단일 회귀 테스트 실행"""
        if test_name not in self.regression_configs:
            raise ValueError(f"회귀 테스트 설정을 찾을 수 없습니다: {test_name}")

        config = self.regression_configs[test_name]

        # 기준선 확인
        if test_name not in self.baselines:
            raise ValueError(f"기준선을 찾을 수 없습니다: {test_name}")

        baseline = self.baselines[test_name]

        self.console.print(f"[blue]회귀 테스트 실행 중: {test_name}[/blue]")

        # 현재 성능 측정
        current_result = await self.performance_monitor.run_benchmark(
            name=f"{test_name}_regression_test",
            url=config.url,
            method=config.method,
            concurrent_requests=config.concurrency,
            total_requests=config.requests,
            timeout=config.timeout,
            headers=config.headers,
            data=config.data
        )

        # 성능 변화 분석
        performance_changes = self._analyze_performance_changes(baseline, current_result)

        # 회귀 감지
        regression_detected, severity = self._detect_regression(
            performance_changes,
            config.acceptable_regression_percent,
            config.critical_regression_percent
        )

        result = RegressionTestResult(
            config_name=test_name,
            baseline=baseline,
            current_result=current_result,
            regression_detected=regression_detected,
            regression_severity=severity,
            performance_changes=performance_changes
        )

        # 결과 출력
        self._display_regression_result(result)

        return result

    async def run_all_regression_tests(self) -> List[RegressionTestResult]:
        """모든 회귀 테스트 실행"""
        if not self.regression_configs:
            self.console.print("[yellow]실행할 회귀 테스트가 없습니다.[/yellow]")
            return []

        self.console.print(f"[blue]{len(self.regression_configs)}개의 회귀 테스트를 실행합니다.[/blue]")

        results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("회귀 테스트 실행", total=len(self.regression_configs))

            for test_name in self.regression_configs:
                try:
                    result = await self.run_regression_test(test_name)
                    results.append(result)
                except Exception as e:
                    self.console.print(f"[red]회귀 테스트 실패 {test_name}: {e}[/red]")

                progress.advance(task)

        # 전체 결과 요약
        self._display_regression_summary(results)

        return results

    def _analyze_performance_changes(
        self,
        baseline: BenchmarkBaseline,
        current: BenchmarkResult
    ) -> Dict[str, Dict[str, float]]:
        """성능 변화 분석"""
        changes = {}

        # 현재 결과에서 메트릭 추출
        current_metrics = {
            "requests_per_second": current.requests_per_second,
            "avg_response_time": current.avg_response_time,
            "p95_response_time": current.percentiles.get(95, 0),
            "p99_response_time": current.percentiles.get(99, 0),
            "error_rate": current.error_rate,
            "throughput_bytes_per_sec": current.throughput_bytes_per_sec,
            "peak_memory_mb": current.memory_usage.get('peak', 0),
            "avg_memory_mb": current.memory_usage.get('average', 0),
            "peak_cpu_percent": current.cpu_usage.get('peak', 0),
            "avg_cpu_percent": current.cpu_usage.get('average', 0)
        }

        # 각 메트릭별 변화율 계산
        for metric_name in baseline.metrics:
            if metric_name in current_metrics:
                baseline_value = baseline.metrics[metric_name]
                current_value = current_metrics[metric_name]

                if baseline_value > 0:
                    change_percent = ((current_value - baseline_value) / baseline_value) * 100
                else:
                    change_percent = 0

                changes[metric_name] = {
                    "baseline": baseline_value,
                    "current": current_value,
                    "change_percent": change_percent
                }

        return changes

    def _detect_regression(
        self,
        changes: Dict[str, Dict[str, float]],
        acceptable_threshold: float,
        critical_threshold: float
    ) -> Tuple[bool, str]:
        """회귀 감지"""
        # 중요한 메트릭들과 그들의 방향성 (True = 높을수록 좋음, False = 낮을수록 좋음)
        important_metrics = {
            "requests_per_second": True,
            "avg_response_time": False,
            "p95_response_time": False,
            "error_rate": False
        }

        max_regression = 0
        regression_detected = False
        severity = "none"

        for metric, is_higher_better in important_metrics.items():
            if metric not in changes:
                continue

            change_percent = changes[metric]["change_percent"]

            # 회귀 판단 (성능이 나빠진 경우)
            if is_higher_better:
                # 높을수록 좋은 메트릭 (RPS 등)
                regression_percent = -change_percent if change_percent < 0 else 0
            else:
                # 낮을수록 좋은 메트릭 (응답시간, 에러율 등)
                regression_percent = change_percent if change_percent > 0 else 0

            max_regression = max(max_regression, regression_percent)

        if max_regression >= critical_threshold:
            regression_detected = True
            severity = "critical"
        elif max_regression >= acceptable_threshold:
            regression_detected = True
            severity = "acceptable"

        return regression_detected, severity

    def _display_regression_result(self, result: RegressionTestResult):
        """회귀 테스트 결과 출력"""
        # 결과 상태에 따른 색상
        if result.regression_severity == "critical":
            status_color = "red"
            status_icon = "🚨"
            status_text = "심각한 성능 저하"
        elif result.regression_severity == "acceptable":
            status_color = "yellow"
            status_icon = "⚠️"
            status_text = "성능 저하 감지"
        else:
            status_color = "green"
            status_icon = "✅"
            status_text = "성능 정상"

        self.console.print(f"\n[{status_color}]{status_icon} {result.config_name}: {status_text}[/{status_color}]")

        # 성능 변화 테이블
        table = Table(title=f"성능 변화: {result.config_name}")
        table.add_column("메트릭", style="cyan")
        table.add_column("기준선", justify="right")
        table.add_column("현재", justify="right")
        table.add_column("변화", justify="right")

        for metric, change_data in result.performance_changes.items():
            baseline_val = change_data["baseline"]
            current_val = change_data["current"]
            change_percent = change_data["change_percent"]

            # 변화율 색상
            if abs(change_percent) < 5:
                change_color = "white"
            elif change_percent > 0:
                if metric in ["requests_per_second", "throughput_bytes_per_sec"]:
                    change_color = "green"  # 높을수록 좋은 메트릭
                else:
                    change_color = "red"    # 낮을수록 좋은 메트릭
            else:
                if metric in ["requests_per_second", "throughput_bytes_per_sec"]:
                    change_color = "red"    # 높을수록 좋은 메트릭
                else:
                    change_color = "green"  # 낮을수록 좋은 메트릭

            # 값 포맷팅
            if metric.endswith("_time"):
                baseline_str = f"{baseline_val:.3f}s"
                current_str = f"{current_val:.3f}s"
            elif metric.endswith("_rate") or metric.endswith("_percent"):
                baseline_str = f"{baseline_val:.2f}%"
                current_str = f"{current_val:.2f}%"
            elif metric == "throughput_bytes_per_sec":
                baseline_str = f"{baseline_val/1024:.2f} KB/s"
                current_str = f"{current_val/1024:.2f} KB/s"
            else:
                baseline_str = f"{baseline_val:.2f}"
                current_str = f"{current_val:.2f}"

            change_str = f"[{change_color}]{change_percent:+.1f}%[/{change_color}]"

            table.add_row(
                metric.replace("_", " ").title(),
                baseline_str,
                current_str,
                change_str
            )

        self.console.print(table)

    def _display_regression_summary(self, results: List[RegressionTestResult]):
        """회귀 테스트 전체 결과 요약"""
        if not results:
            return

        # 통계 계산
        total_tests = len(results)
        critical_regressions = sum(1 for r in results if r.regression_severity == "critical")
        acceptable_regressions = sum(1 for r in results if r.regression_severity == "acceptable")
        passed_tests = total_tests - critical_regressions - acceptable_regressions

        # 요약 테이블
        summary_table = Table(title="회귀 테스트 요약")
        summary_table.add_column("상태", style="cyan")
        summary_table.add_column("개수", justify="right")
        summary_table.add_column("비율", justify="right")

        summary_table.add_row(
            "[green]✅ 통과[/green]",
            str(passed_tests),
            f"{(passed_tests/total_tests*100):.1f}%"
        )
        summary_table.add_row(
            "[yellow]⚠️ 성능 저하[/yellow]",
            str(acceptable_regressions),
            f"{(acceptable_regressions/total_tests*100):.1f}%"
        )
        summary_table.add_row(
            "[red]🚨 심각한 저하[/red]",
            str(critical_regressions),
            f"{(critical_regressions/total_tests*100):.1f}%"
        )

        self.console.print(summary_table)

        # 실패한 테스트 목록
        if critical_regressions > 0 or acceptable_regressions > 0:
            failed_table = Table(title="성능 저하 감지된 테스트")
            failed_table.add_column("테스트", style="cyan")
            failed_table.add_column("심각도", justify="center")
            failed_table.add_column("주요 문제", style="red")

            for result in results:
                if result.regression_detected:
                    # 가장 큰 회귀를 찾기
                    max_regression = 0
                    worst_metric = ""

                    for metric, change_data in result.performance_changes.items():
                        change_percent = abs(change_data["change_percent"])
                        if change_percent > max_regression:
                            max_regression = change_percent
                            worst_metric = metric

                    severity_display = {
                        "critical": "[red]🚨 심각[/red]",
                        "acceptable": "[yellow]⚠️ 주의[/yellow]"
                    }

                    failed_table.add_row(
                        result.config_name,
                        severity_display[result.regression_severity],
                        f"{worst_metric}: {max_regression:.1f}% 저하"
                    )

            self.console.print(failed_table)

    def export_regression_results(self, results: List[RegressionTestResult], filename: str):
        """회귀 테스트 결과를 파일로 내보내기"""
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_tests": len(results),
            "results": []
        }

        for result in results:
            data["results"].append({
                "config_name": result.config_name,
                "timestamp": result.timestamp.isoformat(),
                "regression_detected": result.regression_detected,
                "regression_severity": result.regression_severity,
                "baseline": {
                    "name": result.baseline.name,
                    "version": result.baseline.version,
                    "timestamp": result.baseline.timestamp.isoformat(),
                    "metrics": result.baseline.metrics
                },
                "current_result": {
                    "requests_per_second": result.current_result.requests_per_second,
                    "avg_response_time": result.current_result.avg_response_time,
                    "error_rate": result.current_result.error_rate,
                    "percentiles": result.current_result.percentiles
                },
                "performance_changes": result.performance_changes
            })

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.console.print(f"[green]회귀 테스트 결과가 {filename}에 저장되었습니다.[/green]")


# CLI 통합을 위한 편의 함수들
async def create_performance_baseline(
    name: str,
    version: str,
    url: str,
    requests: int = 200,
    concurrency: int = 10,
    baseline_dir: str = ".benchmarks"
) -> BenchmarkBaseline:
    """성능 기준선 생성 (CLI용)"""
    manager = BenchmarkManager(baseline_dir)
    return manager.create_baseline(name, version, url, requests=requests, concurrency=concurrency)


async def run_performance_regression_test(
    config_file: str,
    baseline_dir: str = ".benchmarks"
) -> List[RegressionTestResult]:
    """회귀 테스트 실행 (CLI용)"""
    manager = BenchmarkManager(baseline_dir)

    # 설정 파일 로드
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    # 회귀 테스트 설정 추가
    for test_config in config_data.get('regression_tests', []):
        config = RegressionTestConfig(**test_config)
        manager.add_regression_test(config)

    # 모든 회귀 테스트 실행
    return await manager.run_all_regression_tests()
