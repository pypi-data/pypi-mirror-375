#!/usr/bin/env python3
"""
PawnStack Top 도구 (독립 실행 버전)

실시간 시스템 리소스 모니터링 - 레거시 호환
"""

import os
import time
import psutil
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from argparse import ArgumentParser


@dataclass
class SystemStats:
    """시스템 통계 저장"""
    timestamp: float = 0
    net_bytes_sent: int = 0
    net_bytes_recv: int = 0
    net_packets_sent: int = 0
    net_packets_recv: int = 0
    disk_read_bytes: int = 0
    disk_write_bytes: int = 0


class TopCLI:
    """Top CLI (독립 실행 버전)"""

    def __init__(self, args=None):
        self.args = args
        self.prev_stats = None  # 이전 통계 저장

    def get_current_stats(self) -> SystemStats:
        """현재 시스템 통계 수집"""
        current_time = time.time()
        net_io = psutil.net_io_counters()
        disk_io = psutil.disk_io_counters()

        return SystemStats(
            timestamp=current_time,
            net_bytes_sent=net_io.bytes_sent if net_io else 0,
            net_bytes_recv=net_io.bytes_recv if net_io else 0,
            net_packets_sent=net_io.packets_sent if net_io else 0,
            net_packets_recv=net_io.packets_recv if net_io else 0,
            disk_read_bytes=disk_io.read_bytes if disk_io else 0,
            disk_write_bytes=disk_io.write_bytes if disk_io else 0
        )

    def calculate_rates(self, current: SystemStats, previous: SystemStats) -> Dict[str, float]:
        """초당 전송률 계산"""
        if not previous or current.timestamp <= previous.timestamp:
            return {
                "net_in_rate": 0.0,
                "net_out_rate": 0.0,
                "pk_in_rate": 0.0,
                "pk_out_rate": 0.0,
                "disk_rd_rate": 0.0,
                "disk_wr_rate": 0.0
            }

        time_diff = current.timestamp - previous.timestamp

        # 네트워크 전송률 (MB/s)
        net_in_rate = (current.net_bytes_recv - previous.net_bytes_recv) / time_diff / (1024 * 1024)
        net_out_rate = (current.net_bytes_sent - previous.net_bytes_sent) / time_diff / (1024 * 1024)

        # 패킷 전송률 (packets/s)
        pk_in_rate = (current.net_packets_recv - previous.net_packets_recv) / time_diff
        pk_out_rate = (current.net_packets_sent - previous.net_packets_sent) / time_diff

        # 디스크 I/O 전송률 (MB/s)
        disk_rd_rate = (current.disk_read_bytes - previous.disk_read_bytes) / time_diff / (1024 * 1024)
        disk_wr_rate = (current.disk_write_bytes - previous.disk_write_bytes) / time_diff / (1024 * 1024)

        return {
            "net_in_rate": max(0, net_in_rate),
            "net_out_rate": max(0, net_out_rate),
            "pk_in_rate": max(0, pk_in_rate),
            "pk_out_rate": max(0, pk_out_rate),
            "disk_rd_rate": max(0, disk_rd_rate),
            "disk_wr_rate": max(0, disk_wr_rate)
        }

    def get_resource_status(self) -> Dict[str, Any]:
        """리소스 상태 수집"""
        # 현재 통계 수집
        current_stats = self.get_current_stats()

        # CPU 정보
        cpu_times = psutil.cpu_times_percent(interval=0.1)
        load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)

        # 메모리 정보
        memory = psutil.virtual_memory()

        # 전송률 계산
        rates = self.calculate_rates(current_stats, self.prev_stats)

        # 이전 통계 업데이트
        self.prev_stats = current_stats

        return {
            "time": time.strftime("%H:%M:%S"),
            "net_in": f"{rates['net_in_rate']:.2f}M",
            "net_out": f"{rates['net_out_rate']:.2f}M",
            "pk_in": f"{int(rates['pk_in_rate'])}",
            "pk_out": f"{int(rates['pk_out_rate'])}",
            "load": f"{load_avg[0]:.2f}",
            "usr": f"{cpu_times.user:.1f}%" if hasattr(cpu_times, 'user') else "0.0%",
            "sys": f"{cpu_times.system:.1f}%" if hasattr(cpu_times, 'system') else "0.0%",
            "i/o": f"{cpu_times.iowait:.2f}" if hasattr(cpu_times, 'iowait') else "0.00",
            "disk_rd": f"{rates['disk_rd_rate']:.2f}M",
            "disk_wr": f"{rates['disk_wr_rate']:.2f}M",
            "mem_%": f"{memory.percent:.1f}%",
        }

    def get_system_info(self) -> Dict[str, Any]:
        """시스템 정보 수집"""
        import platform

        return {
            "hostname": platform.node(),
            "system": platform.system(),
            "cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "memory": round(psutil.virtual_memory().total / (1024**3), 1),  # GB
            "model": platform.machine()
        }

    def get_column_widths(self, data: Dict[str, Any]) -> Dict[str, int]:
        """컬럼 너비 계산"""
        column_widths = {
            "time": 8,
            "net_in": 9,
            "net_out": 9,
            "pk_in": 10,
            "pk_out": 10,
            "load": 5,
            "usr": 6,
            "sys": 6,
            "i/o": 6,
            "disk_rd": 9,
            "disk_wr": 9,
            "mem_%": 6,
        }

        # 동적 너비 계산
        for column_key, value in data.items():
            align_space = max(len(str(value)), len(column_key)) + 1
            if column_key not in column_widths:
                column_widths[column_key] = align_space

        return column_widths

    def print_line_status(self, data: Dict[str, Any], system_info: Dict[str, Any], is_header: bool = False):
        """라인 형태로 상태 출력"""
        hostname = system_info.get('hostname', 'unknown')[:20]
        cores = system_info.get('cores', 1)
        memory = system_info.get('memory', 0)

        if is_header:
            table_title = f"🐰 {hostname} <{cores} cores, {memory}GB> 🐰"
            print(f"\n{table_title}")

        column_widths = self.get_column_widths(data)

        if is_header:
            # 헤더 출력
            headers = []
            for column_key in data.keys():
                align_space = column_widths[column_key]
                headers.append(f"{column_key:>{align_space}}")
            print("│" + "│".join(headers) + "│")

        # 값 출력
        values = []
        for column_key, value in data.items():
            align_space = column_widths[column_key]
            values.append(f"{str(value):>{align_space}}")

        print("│" + "│".join(values) + "│")

    def monitor_resources(self, interval: float = 1.0):
        """리소스 모니터링 실행"""
        system_info = self.get_system_info()
        count = 0

        print(f"🚀 Starting resource monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop")

        try:
            # 첫 번째 측정 (기준점 설정)
            self.prev_stats = self.get_current_stats()
            time.sleep(interval)

            while True:
                try:
                    columns, rows = os.get_terminal_size()
                except OSError:
                    columns, rows = 80, 24

                data = self.get_resource_status()

                # 헤더를 주기적으로 출력 (터미널 높이에 따라)
                if count % (rows - 5) == 0:
                    self.print_line_status(data, system_info, is_header=True)
                else:
                    self.print_line_status(data, system_info, is_header=False)

                count += 1
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n리소스 모니터링이 중단되었습니다")

    def run(self) -> int:
        """Top CLI 실행"""
        interval = getattr(self.args, 'interval', 1.0) if self.args else 1.0
        self.monitor_resources(interval)
        return 0


def get_arguments(parser: ArgumentParser):
    """인수 정의"""
    parser.add_argument('command', help='Command to execute (resource, net, proc)',
                      type=str, nargs='?', default="resource")

    parser.add_argument('-i', '--interval', type=float,
                      help='Refresh interval in seconds (default: 1)', default=1.0)
    parser.add_argument('-t', '--print-type', type=str, help='Output type',
                      default="line", choices=["live", "layout", "line"])

    # 모니터링 옵션
    parser.add_argument('--top-n', type=int, default=10,
                      help='Number of top processes to display (default: 10)')


def main():
    """메인 함수"""
    parser = ArgumentParser(description='PawnStack Top - 실시간 시스템 리소스 모니터링')
    get_arguments(parser)
    args = parser.parse_args()

    cli = TopCLI(args)
    return cli.run()


if __name__ == '__main__':
    import sys
    sys.exit(main())
