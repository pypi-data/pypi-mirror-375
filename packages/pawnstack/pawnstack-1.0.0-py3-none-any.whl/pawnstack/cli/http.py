"""
PawnStack HTTP 모니터링 도구

HTTP/HTTPS 요청의 RTT 측정 및 모니터링 (레거시 호환)
"""

import os
import sys
import json
import time
import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from argparse import ArgumentParser

from pawnstack import __version__
from pawnstack.config.global_config import pawn
from pawnstack.cli.base import HTTPBaseCLI
from pawnstack.cli.banner import generate_banner
from pawnstack.utils.file import write_json, read_file
from pawnstack.type_utils.validators import is_valid_url, is_json
from pawnstack.http_client.client import HttpClient
from pawnstack.monitoring import HTTPMonitor, HTTPMonitorConfig, quick_benchmark

# 모듈 메타데이터
__description__ = 'This is a tool to measure RTT on HTTP/S requests.'

http_config_example = """
    # The configuration options are provided below. You can customize these settings in the 'http_config.ini' file.

    [default]
    success = status_code==200
    slack_url =
    interval = 3
    method = get
    ; data = sdsd
    data = {"sdsd": "sd222sd"}

    [post]
    url = http://httpbin.org/post
    method = post

    [http_200_ok]
    url = http://httpbin.org/status/200
    success = status_code==200

    [http_300_ok_and_2ms_time]
    url = http://httpbin.org/status/400
    success = ['status_code==300', 'response_time<0.02']

    [http_400_ok]
    url = http://httpbin.org/status/400
    success = ["status_code==400"]
    """

__epilog__ = (
    f"This script provides various options to check the HTTP status of URLs. \n\n"
    f"Usage examples:\n"
    f"  1. Basic usage:  \n\tpawns http https://example.com\n\n"
    f"  2. Verbose mode: \n\tpawns http https://example.com -v\n\n"
    f"  3. Using custom headers and POST method: \n\tpawns http https://example.com -m POST --headers '{{\"Content-Type\": \"application/json\"}}' --data '{{\"param\": \"value\"}}'\n\n"
    f"  4. Ignoring SSL verification and setting a custom timeout: \n\tpawns http https://example.com --ignore-ssl --timeout 5\n\n"
    f"  5. Checking with specific success criteria: \n\tpawns http https://example.com --success 'status_code==200' 'response_time<2'\n\n"
    f"  6. Running with a custom config file and interval: \n\tpawns http https://example.com -c http_config.ini -i 3\n"
    f"  7. Setting maximum workers and stack limit: \n\tpawns http https://example.com -w 5 --stack-limit 10\n\n"
    f"  8. Dry run without actual HTTP request: \n\tpawns http https://example.com --dry-run\n\n"
    f"  9. Sending notifications to a Slack URL on failure: \n\tpawns http https://example.com --slack-url 'https://hooks.slack.com/services/...'\n\n"
    f" 10. Checking blockheight increase: \n\tpawns http http://test-node-01:26657/status --blockheight-key \"result.sync_info.latest_block_height\" -i 5\n\n"
    f"\n{http_config_example}\n\n"
    f"For more details, use the -h or --help flag."
)


@dataclass
class HTTPTask:
    """HTTP 작업 설정"""
    url: str = ""
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    data: Union[str, Dict[str, Any]] = field(default_factory=dict)
    timeout: float = 10.0
    success_criteria: List[str] = field(default_factory=lambda: ["status_code==200"])
    logical_operator: str = "and"
    section_name: str = "default"


# HTTPMonitor 클래스 제거됨 - 기능이 HTTPCLI로 통합됨


class HTTPCLI(HTTPBaseCLI):
    """HTTP 모니터링 CLI (레거시 호환)"""

    def __init__(self, args=None):
        super().__init__(args)
        self.response_times = []
        self.total_count = 0
        self.fail_count = 0
        self.error_count = 0
        self.consecutive_errors = 0  # 연속 에러 카운트
        self.sequence = 0  # 시퀀스 번호
        self.max_response_time = 0
        self.min_response_time = float('inf')
        self.avg_response_time = 0
        self.successful_response_times = []  # 성공한 요청들의 응답시간

    def get_arguments(self, parser: ArgumentParser):
        """인수 정의 (레거시 호환)"""
        parser.add_argument('url', help='URL to be checked', type=str, nargs='?', default="")

        parser.add_argument('-c', '--config-file', type=str, help='Path to the configuration file. Defaults to "config.ini".', default="config.ini")
        parser.add_argument('--verbose-level', action='count', help='Enables verbose mode. Higher values increase verbosity level. Default is 1.', default=1)
        parser.add_argument('-q', '--quiet', action='count', help='Enables quiet mode. Suppresses all messages. Default is 0.', default=0)
        parser.add_argument('-i', '--interval', type=float, help='Interval time in seconds between checks. Default is 1 second.', default=1)
        parser.add_argument('-m', '--method', type=lambda s: s.upper(), help='HTTP method to use (e.g., GET, POST). Default is "GET".', default="GET")
        parser.add_argument('-t', '--timeout', type=float, help='Timeout in seconds for each HTTP request. Default is 10 seconds.', default=10)
        parser.add_argument('-b', '--base-dir', type=str, help='Base directory for logs and config. Default is current directory.', default=os.getcwd())

        parser.add_argument('--success', type=str, action='append', help='Success criteria (e.g., "status_code==200", "response_time<2"). Can be used multiple times.')
        parser.add_argument('--logical-operator', type=str, choices=['and', 'or'], help='Logical operator for multiple success criteria. Default is "and".', default="and")
        parser.add_argument('--ignore-ssl', action='store_true', help='Ignore SSL certificate verification. Default is False.')

        parser.add_argument('--data', type=str, help='Data to send with the request (JSON format for POST/PUT requests).')
        parser.add_argument('--headers', type=str, help='HTTP headers in JSON format (e.g., \'{"Content-Type": "application/json"}\').')

        parser.add_argument('-w', '--workers', type=int, help='Number of worker threads for concurrent requests. Default is 10.', default=10)
        parser.add_argument('--stack-limit', type=int, help='Maximum number of items to keep in response time stack. Default is 5.', default=5)

        parser.add_argument('--dry-run', action='store_true', help='Perform a dry run without making actual HTTP requests.')
        parser.add_argument('--slack-url', type=str, help='Slack webhook URL for notifications on failures.')
        parser.add_argument('--blockheight-key', type=str, help='JSON key path to extract block height from response (for blockchain monitoring).')

        parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help='Logging level. Default is INFO.', default="INFO")
        parser.add_argument('--output-file', type=str, help='File to write monitoring results.')

        # 새로운 모니터링 기능 옵션들
        parser.add_argument('--dashboard', action='store_true', help='Enable rich dashboard for monitoring. Default is False.')
        parser.add_argument('--benchmark', action='store_true', help='Run performance benchmark instead of monitoring.')
        parser.add_argument('--benchmark-requests', type=int, help='Number of requests for benchmark. Default is 100.', default=100)
        parser.add_argument('--benchmark-concurrency', type=int, help='Concurrent requests for benchmark. Default is 10.', default=10)

    def setup_config(self):
        """설정 초기화 (레거시 호환)"""
        args = self.args
        app_name = 'httping'

        is_hide_line_number = getattr(args, 'verbose_level', 1) > 1
        stdout = not getattr(args, 'quiet', 0)

        pawn.set(
            PAWN_CONFIG_FILE=getattr(args, 'config_file', 'config.ini'),
            PAWN_PATH=getattr(args, 'base_dir', os.getcwd()),
            PAWN_LOGGER=dict(
                log_level=getattr(args, 'log_level', 'INFO'),
                stdout_level=getattr(args, 'log_level', 'INFO'),
                log_path=f"{getattr(args, 'base_dir', os.getcwd())}/logs",
                stdout=stdout,
                use_hook_exception=True,
                show_path=False,
            ),
            PAWN_CONSOLE=dict(
                redirect=True,
                record=True,
                log_path=is_hide_line_number,
            ),
            app_name=app_name,
            args=args,
            try_pass=False,
            last_execute_point=0,
            data={
                "response_time": [],
            },
            fail_count=0,
            total_count=0,
            default_config={},
        )

        if getattr(args, 'verbose_level', 1) > 2:
            pawn.set(
                PAWN_LOGGER=dict(
                    log_level="DEBUG",
                    stdout_level="DEBUG",
                )
            )

    def print_banner(self):
        """배너 출력 (레거시 호환)"""
        if not getattr(self.args, 'quiet', 0):
            banner = generate_banner(
                app_name=pawn.get('app_name', 'httping'),
                author="PawnStack Team",
                version=__version__,
                font="graffiti"
            )
            print(banner)

    def parse_headers(self) -> Dict[str, str]:
        """헤더 파싱"""
        headers = {}

        if hasattr(self.args, 'headers') and self.args.headers:
            try:
                if is_json(self.args.headers):
                    headers = json.loads(self.args.headers)
                else:
                    # "Key: Value" 형태로 파싱
                    for header in self.args.headers.split(','):
                        if ':' in header:
                            key, value = header.split(':', 1)
                            headers[key.strip()] = value.strip()
            except Exception as e:
                self.log_warning(f"Failed to parse headers: {e}")

        return headers

    def parse_data(self) -> Union[str, Dict[str, Any]]:
        """데이터 파싱"""
        if hasattr(self.args, 'data') and self.args.data:
            try:
                if is_json(self.args.data):
                    return json.loads(self.args.data)
                else:
                    return self.args.data
            except Exception as e:
                self.log_warning(f"Failed to parse data: {e}")
                return self.args.data

        return {}

    def generate_tasks_from_config(self) -> List[HTTPTask]:
        """설정 파일에서 작업 생성"""
        tasks = []

        # 디버깅 정보 출력
        if pawn.get('PAWN_DEBUG') or getattr(self.args, 'verbose', 0) >= 3:
            self.log_debug(f"Args namespace: {self.args}")
            self.log_debug(f"URL from args: {getattr(self.args, 'url', 'NOT_FOUND')}")
            self.log_debug(f"Method from args: {getattr(self.args, 'method', 'NOT_FOUND')}")
            self.log_debug(f"All args attributes: {vars(self.args) if hasattr(self.args, '__dict__') else 'No __dict__'}")

        # URL이 직접 제공된 경우
        if getattr(self.args, 'url', ''):
            if not is_valid_url(self.args.url):
                self.log_error(f"Invalid URL: {self.args.url}")
                return []

            task = HTTPTask(
                url=self.args.url,
                method=getattr(self.args, 'method', 'GET'),
                headers=self.parse_headers(),
                data=self.parse_data(),
                timeout=getattr(self.args, 'timeout', 10.0),
                success_criteria=getattr(self.args, 'success', None) or ["status_code==200"],
                logical_operator=getattr(self.args, 'logical_operator', 'and'),
                section_name="command_line"
            )
            tasks.append(task)

        # 설정 파일에서 추가 작업 로드
        config_file = getattr(self.args, 'config_file', 'config.ini')
        if os.path.exists(config_file):
            try:
                import configparser
                config = configparser.ConfigParser()
                config.read(config_file)

                for section_name in config.sections():
                    if section_name == 'default':
                        continue

                    section = config[section_name]
                    url = section.get('url', '')

                    if url and is_valid_url(url):
                        # 헤더 파싱
                        headers = {}
                        if section.get('headers'):
                            try:
                                headers = json.loads(section.get('headers'))
                            except:
                                pass

                        # 데이터 파싱
                        data = {}
                        if section.get('data'):
                            try:
                                data = json.loads(section.get('data'))
                            except:
                                data = section.get('data')

                        # 성공 기준 파싱
                        success_criteria = ["status_code==200"]
                        if section.get('success'):
                            try:
                                if section.get('success').startswith('['):
                                    success_criteria = json.loads(section.get('success'))
                                else:
                                    success_criteria = [section.get('success')]
                            except:
                                success_criteria = [section.get('success')]

                        task = HTTPTask(
                            url=url,
                            method=section.get('method', 'GET').upper(),
                            headers=headers,
                            data=data,
                            timeout=float(section.get('timeout', 10.0)),
                            success_criteria=success_criteria,
                            logical_operator=section.get('logical_operator', 'and'),
                            section_name=section_name
                        )
                        tasks.append(task)

            except Exception as e:
                self.log_warning(f"Failed to load config file {config_file}: {e}")

        return tasks

    def check_success_criteria(self, response, response_time: float, criteria: List[str], operator: str = "and") -> bool:
        """성공 기준 검사"""
        if not criteria or criteria == [None]:
            return response.status_code == 200

        results = []

        # 디버그 모드에서 상세 정보 출력
        if getattr(self.args, 'verbose_level', 1) >= 3:
            pawn.console.log(f"[dim]Checking criteria: {criteria}, operator: {operator}[/dim]")

        for criterion in criteria:
            if "==" in criterion:
                key, expected = criterion.split("==", 1)
                key = key.strip()
                expected = expected.strip()

                if key == "status_code":
                    result = response.status_code == int(expected)
                    results.append(result)
                    if getattr(self.args, 'verbose_level', 1) >= 3:
                        pawn.console.log(f"[dim]  status_code: {response.status_code} == {expected} => {result}[/dim]")
                elif key == "response_time":
                    result = response_time == float(expected)
                    results.append(result)
                    if getattr(self.args, 'verbose_level', 1) >= 3:
                        pawn.console.log(f"[dim]  response_time: {response_time:.3f} == {expected} => {result}[/dim]")
                else:
                    # 응답 데이터에서 키 검색
                    try:
                        if hasattr(response, 'json') and response.content:
                            data = response.json()
                            actual = self.get_nested_value(data, key)
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
                    result = response_time < threshold
                    results.append(result)
                    if getattr(self.args, 'verbose_level', 1) >= 3:
                        pawn.console.log(f"[dim]  response_time: {response_time:.3f} < {threshold} => {result}[/dim]")
                else:
                    results.append(False)

            elif ">" in criterion:
                key, threshold = criterion.split(">", 1)
                key = key.strip()
                threshold = float(threshold.strip())

                if key == "response_time":
                    result = response_time > threshold
                    results.append(result)
                    if getattr(self.args, 'verbose_level', 1) >= 3:
                        pawn.console.log(f"[dim]  response_time: {response_time:.3f} > {threshold} => {result}[/dim]")
                else:
                    results.append(False)

        # 결과가 비어있으면 status_code 200 검사
        if not results:
            return response.status_code == 200

        # 논리 연산자 적용
        final_result = all(results) if operator.lower() == "and" else any(results)

        if getattr(self.args, 'verbose_level', 1) >= 3:
            pawn.console.log(f"[dim]  Final: {results} with {operator} => {final_result}[/dim]")

        return final_result

    def get_nested_value(self, data: Dict[str, Any], key_path: str) -> Any:
        """중첩된 딕셔너리에서 값 추출"""
        keys = key_path.split(".")
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current

    async def run_monitoring(self, tasks: List[HTTPTask]):
        """모니터링 실행"""
        interval = getattr(self.args, 'interval', 1.0)

        pawn.console.log(f"🚀 Start httping ... url_count={len(tasks)}")
        pawn.console.log("If you want to see more logs, use the [yellow]--verbose[/yellow] option")

        if getattr(self.args, 'dry_run', False):
            # 드라이 런 모드
            for task in tasks:
                pawn.console.log(f"[DRY RUN] Would check: {task.method} {task.url}")
            return

        try:
            while True:
                for task in tasks:
                    result = await self.check_url(task)

                    # 결과 출력
                    if not getattr(self.args, 'quiet', 0):
                        self.display_result(result)

                    # 실패 시 슬랙 알림
                    if not result.get('success') and hasattr(self.args, 'slack_url') and self.args.slack_url:
                        await self.send_slack_notification(result)

                # 통계 출력은 개별 결과 출력에 포함됨 (레거시 형식)

                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            self.log_info("HTTP monitoring stopped by user")

    def display_result(self, result: Dict[str, Any]):
        """결과 출력 - 레거시 형식"""
        # 응답 시간을 밀리초로 변환
        response_time_ms = int(result.get('response_time', 0) * 1000)

        # 통계 정보 생성
        stats_str = f"<CER:{self.consecutive_errors}/ER:{self.error_count}/SQ:{self.sequence}>"

        # 응답 시간 통계 (밀리초)
        if self.successful_response_times:
            avg_ms = int(self.avg_response_time * 1000)
            max_ms = int(self.max_response_time * 1000)
            min_ms = int(self.min_response_time * 1000) if self.min_response_time != float('inf') else 0
        else:
            avg_ms = max_ms = min_ms = response_time_ms if result.get('success') else 0

        if 'error' in result:
            # 에러 발생 시
            log_message = f"[ERROR] {stats_str} url='{result['url']}', error={result['error']}"
            if getattr(self.args, 'verbose_level', 1) >= 1:
                pawn.console.log(f"[red]{log_message}[/red]")
            else:
                pawn.app_logger.error(log_message)
        else:
            status = " OK " if result.get('success') else "FAIL"
            status_color = "green" if result.get('success') else "red"
            log_level = "INF" if result.get('success') else "WRN"

            # 레거시 형식으로 출력
            log_message = f"[ {status} ] {stats_str} url='{result['url']}', status={result['status_code']}, {response_time_ms:4d}ms (avg: {avg_ms:4d}, max: {max_ms:4d}, min: {min_ms:4d})"

            if getattr(self.args, 'verbose_level', 1) >= 1:
                # 콘솔 출력 (색상 포함) - 레거시 형식
                pawn.console.log(f"{log_level} {log_message}")
            else:
                # 로거 출력 (레거시 호환)
                if result.get('success'):
                    pawn.app_logger.info(log_message)
                else:
                    pawn.app_logger.warning(log_message)

    async def send_slack_notification(self, result: Dict[str, Any]):
        """슬랙 알림 전송"""
        try:
            message = f"🚨 HTTP Check Failed\n"
            message += f"URL: {result['url']}\n"
            message += f"Method: {result['method']}\n"

            if 'error' in result:
                message += f"Error: {result['error']}\n"
            else:
                message += f"Status Code: {result['status_code']}\n"
                message += f"Response Time: {result['response_time']:.3f}s\n"

            # 슬랙 전송 로직 (향후 구현)
            self.log_info(f"Would send Slack notification: {message}")

        except Exception as e:
            self.log_error(f"Failed to send Slack notification: {e}")

    def run(self) -> int:
        """동기 실행 (비동기 래퍼)"""
        return asyncio.run(self.run_async())

    async def run_async(self) -> int:
        """HTTP 모니터링 실행"""
        self.setup_config()
        self.print_banner()

        # 벤치마크 모드 확인
        if getattr(self.args, 'benchmark', False):
            return await self.run_benchmark_mode()

        # 대시보드 모드 확인
        if getattr(self.args, 'dashboard', False):
            return await self.run_dashboard_mode()

        # 기존 모니터링 모드 (레거시 호환)
        tasks = self.generate_tasks_from_config()

        if not tasks:
            self.log_error("No valid URLs to monitor")
            return 1

        await self.run_monitoring(tasks)
        return 0

    async def run_benchmark_mode(self) -> int:
        """벤치마크 모드 실행"""
        if not getattr(self.args, 'url', ''):
            self.log_error("URL is required for benchmark mode")
            return 1

        url = self.args.url
        method = getattr(self.args, 'method', 'GET')
        requests = getattr(self.args, 'benchmark_requests', 100)
        concurrency = getattr(self.args, 'benchmark_concurrency', 10)

        self.log_info(f"벤치마크 모드 시작: {url}")
        self.log_info(f"요청 수: {requests}, 동시 요청: {concurrency}")

        try:
            result = await quick_benchmark(
                url=url,
                name=f"CLI Benchmark: {url}",
                requests=requests,
                concurrency=concurrency,
                method=method,
                headers=self.parse_headers(),
                data=self.parse_data(),
                timeout=getattr(self.args, 'timeout', 10.0),
                verify_ssl=not getattr(self.args, 'ignore_ssl', False)
            )

            # 결과 출력
            pawn.console.log(f"[green]벤치마크 완료![/green]")
            pawn.console.log(f"RPS: {result.requests_per_second:.2f}")
            pawn.console.log(f"평균 응답시간: {result.avg_response_time:.3f}초")
            pawn.console.log(f"에러율: {result.error_rate:.2f}%")

            if result.percentiles:
                pawn.console.log(f"95th 백분위수: {result.percentiles.get(95, 0):.3f}초")
                pawn.console.log(f"99th 백분위수: {result.percentiles.get(99, 0):.3f}초")

            return 0

        except Exception as e:
            self.log_error(f"벤치마크 실행 중 오류: {e}")
            return 1

    async def run_dashboard_mode(self) -> int:
        """대시보드 모드 실행"""
        tasks = self.generate_tasks_from_config()

        if not tasks:
            self.log_error("No valid URLs to monitor")
            return 1

        # HTTPMonitorConfig로 변환
        monitor_configs = []
        for task in tasks:
            config = HTTPMonitorConfig(
                url=task.url,
                method=task.method,
                headers=task.headers,
                data=task.data,
                timeout=task.timeout,
                interval=getattr(self.args, 'interval', 1.0),
                success_criteria=task.success_criteria,
                logical_operator=task.logical_operator,
                name=task.section_name,
                verify_ssl=not getattr(self.args, 'ignore_ssl', False)
            )
            monitor_configs.append(config)

        # HTTP 모니터 생성 및 실행
        monitor = HTTPMonitor()
        for config in monitor_configs:
            monitor.add_endpoint(config)

        self.log_info(f"대시보드 모드 시작: {len(monitor_configs)}개 엔드포인트")

        try:
            await monitor.start_monitoring(dashboard=True)

            # 결과 내보내기
            if getattr(self.args, 'output_file', None):
                monitor.export_results(self.args.output_file)
                self.log_info(f"결과가 {self.args.output_file}에 저장되었습니다.")

            return 0

        except KeyboardInterrupt:
            self.log_info("모니터링이 사용자에 의해 중단되었습니다.")
            return 0
        except Exception as e:
            self.log_error(f"대시보드 모드 실행 중 오류: {e}")
            return 1

    async def check_url(self, task: HTTPTask) -> Dict[str, Any]:
        """URL 체크"""
        start_time = time.time()
        self.sequence += 1  # 시퀀스 증가

        try:
            from pawnstack.http_client.client import HttpClient
            client = HttpClient()

            # HTTP 요청 실행
            response = await client.request(
                method=task.method,
                url=task.url,
                headers=task.headers,
                json=task.data if isinstance(task.data, dict) else None,
                data=task.data if isinstance(task.data, str) else None,
                timeout=task.timeout,
                verify_ssl=not getattr(self.args, 'ignore_ssl', False)
            )

            response_time = time.time() - start_time
            self.response_times.append(response_time)
            self.total_count += 1

            # 성공 기준 검사
            success = self.check_success_criteria(response, response_time, task.success_criteria, task.logical_operator)

            # 디버그 정보 출력
            if getattr(self.args, 'verbose_level', 1) >= 2:
                pawn.console.log(f"[dim]Debug: status_code={response.status_code}, response_time={response_time:.3f}s, criteria={task.success_criteria}, success={success}[/dim]")

            if not success:
                self.fail_count += 1
                self.consecutive_errors += 1
            else:
                # 성공 시 연속 에러 카운트 리셋
                self.consecutive_errors = 0

                # 성공한 요청의 응답 시간 통계 업데이트
                self.successful_response_times.append(response_time)

                # 최소/최대/평균 응답 시간 업데이트
                if response_time < self.min_response_time:
                    self.min_response_time = response_time
                if response_time > self.max_response_time:
                    self.max_response_time = response_time

                # 평균 계산
                self.avg_response_time = sum(self.successful_response_times) / len(self.successful_response_times)

            result = {
                "url": task.url,
                "method": task.method,
                "status_code": response.status_code,
                "response_time": response_time,
                "success": success,
                "timestamp": time.time(),
                "section": task.section_name,
                "content_length": len(response.content) if response.content else 0,
                "headers": dict(response.headers) if hasattr(response, 'headers') else {}
            }

            # 블록 높이 체크 (블록체인용)
            if hasattr(self.args, 'blockheight_key') and self.args.blockheight_key:
                try:
                    if response.content:
                        data = response.json()
                        blockheight = self.get_nested_value(data, self.args.blockheight_key)
                        result["blockheight"] = blockheight
                except:
                    pass

            return result

        except Exception as e:
            self.error_count += 1
            self.consecutive_errors += 1
            self.total_count += 1

            return {
                "url": task.url,
                "method": task.method,
                "error": str(e),
                "response_time": time.time() - start_time,
                "success": False,
                "timestamp": time.time(),
                "section": task.section_name
            }

    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보 반환"""
        if not self.response_times:
            return {}

        return {
            "total_requests": self.total_count,
            "failed_requests": self.fail_count,
            "error_requests": self.error_count,
            "success_rate": ((self.total_count - self.fail_count) / self.total_count * 100) if self.total_count > 0 else 0,
            "avg_response_time": sum(self.response_times) / len(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
        }


def get_arguments(parser: ArgumentParser):
    """인수 정의 (레거시 호환)"""
    cli = HTTPCLI()
    cli.get_arguments(parser)


def main():
    """메인 함수 (레거시 호환)"""
    cli = HTTPCLI()
    return cli.main()


if __name__ == '__main__':
    sys.exit(main())
