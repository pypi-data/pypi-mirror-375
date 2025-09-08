"""
PawnStack 정보 명령어 (레거시 호환)

시스템 리소스, 네트워크, 디스크 사용량 등 상세 정보 출력
"""

import os
import sys
from argparse import ArgumentParser
from rich.tree import Tree

from pawnstack import __version__
from pawnstack.config.global_config import pawn
from pawnstack.cli.base import BaseCLI
from pawnstack.cli.banner import generate_banner
from pawnstack.resource import (
    get_hostname,
    get_platform_info,
    get_mem_info,
    get_rlimit_nofile,
    get_uptime,
    get_swap_usage,
    get_load_average,
    get_interface_ips,
    get_public_ip,
    get_location_with_ip_api,
    get_location,
    DiskUsage
)
from pawnstack.utils.file import write_json
from pawnstack.resource.disk import get_color_by_threshold
from pawnstack.type_utils.converters import dict_to_line

# 모듈 메타데이터
__description__ = "This command displays server resource information."

__epilog__ = (
    "This tool provides a detailed overview of your server's system and network resources.\n\n"
    "Usage examples:\n"
    "  1. Display all resource information in verbose mode:\n"
    "     - Displays detailed information about system and network resources.\n\n"
    "     `pawns info -v`\n"

    "  2. Run in quiet mode without displaying any output:\n"
    "     - Executes the script without showing any output, useful for logging purposes.\n\n"
    "     `pawns info -q`\n"

    "  3. Specify a custom base directory and configuration file:\n"
    "     - Uses the specified base directory and configuration file for operations.\n\n"
    "     `pawns info -b /path/to/base/dir --config-file my_config.ini`\n"

    "  4. Write output to a specified file in quiet mode without displaying any output:\n"
    "     - Writes the collected resource information to 'output.json'.\n\n"
    "    `pawns info -q --output-file output.json`\n\n"

    "For more detailed command usage and options, refer to the help documentation by running 'pawns info --help'."
)


class InfoCLI(BaseCLI):
    """레거시 호환 정보 출력 CLI"""

    def get_arguments(self, parser: ArgumentParser):
        """인수 정의 (레거시 호환)"""
        parser.add_argument('-c', '--config-file', type=str, help='config', default="config.ini")
        parser.add_argument('--verbose-level', action='count', help='verbose mode. view level (default: %(default)s)', default=1)
        parser.add_argument('-q', '--quiet', action='count', help='Quiet mode. Dont show any messages. (default: %(default)s)', default=0)
        parser.add_argument('-b', '--base-dir', type=str, help='base dir for httping (default: %(default)s)', default=os.getcwd())
        parser.add_argument('-d', '--debug-level', action='count', help='debug mode (default: %(default)s)', default=0)
        parser.add_argument('--ip-api-provider', type=str, help='API provider to fetch public IP information (e.g., ip-api.com, another-api.com)', default="ip-api.com")
        parser.add_argument(
            '-w', '--write-file',
            type=str,
            nargs='?',
            const='resource_info.json',
            help='Write the output to a file. Default file is "resource_info.json". If a filename is provided, it will be used instead.',
            default=None
        )

    def setup_config(self):
        """설정 초기화 (레거시 호환)"""
        args = self.args
        app_name = 'Resource Information'

        # args에 config_file 속성이 없으면 기본값 설정
        if not hasattr(args, 'config_file'):
            args.config_file = "config.ini"

        if not hasattr(args, 'base_dir'):
            args.base_dir = os.getcwd()

        is_hide_line_number = getattr(args, 'verbose_level', 1) > 2

        pawn.set(
            PAWN_CONFIG_FILE=args.config_file,
            PAWN_PATH=args.base_dir,
            PAWN_CONSOLE=dict(
                redirect=True,
                record=True,
                log_path=is_hide_line_number,  # hide line number on the right side
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
        if not getattr(self.args, 'quiet', False):
            banner = generate_banner(
                app_name=pawn.get('app_name', 'PawnStack'),
                author="PawnStack Team",
                version=__version__,
                font="graffiti"
            )
            print(banner)

    def print_unless_quiet_mode(self, message=""):
        """조용한 모드가 아닐 때만 출력"""
        if not getattr(self.args, 'quiet', False):
            pawn.console.print(message)

    def run(self) -> int:
        """정보 출력 실행 (레거시 호환)"""
        self.setup_config()
        self.print_banner()

        result = {
            "system": {},
            "network": {},
            "disk": {},
        }

        # 시스템 정보 수집 및 출력
        self.collect_and_display_system_info(result)

        # 네트워크 정보 수집 및 출력
        self.collect_and_display_network_info(result)

        # 디스크 정보 수집 및 출력
        self.collect_and_display_disk_info(result)

        # 파일 출력
        write_file = getattr(self.args, 'write_file', None)
        if write_file:
            write_res = write_json(filename=write_file, data=result)
            pawn.console.log(write_res)

        return 0

    def collect_and_display_system_info(self, result: dict):
        """시스템 정보 수집 및 출력"""
        system_tree = Tree("[bold]🖥️  System Information[/bold]")

        # 호스트명
        hostname = get_hostname()
        system_tree.add(f"Hostname: {hostname}")
        result['system']['hostname'] = hostname

        # 플랫폼 정보
        platform_info = get_platform_info()
        for k, v in platform_info.items():
            system_tree.add(f"{k.title()}: {v}")
            result['system'][k] = v

        # 메모리 정보
        mem_info = get_mem_info()
        result['system']['mem_total'] = mem_info.get('mem_total')
        system_tree.add(f"Memory: {result['system']['mem_total']} GB")

        # 리소스 제한
        resource_limit = get_rlimit_nofile(detail=bool(getattr(self.args, 'debug_level', 0)))
        result['system']["resource_limit"] = resource_limit

        resource_tree = system_tree.add(f"Resource limit")
        for k, v in resource_limit.items():
            resource_tree.add(f"{k.title()}: {v}")

        # 스왑, CPU 로드, 업타임
        swap_usage = get_swap_usage()
        cpu_load = get_load_average()
        uptime = get_uptime()

        system_tree.add(f"Swap Usage: {swap_usage}")
        system_tree.add(f"CPU Load: {cpu_load}")
        system_tree.add(f"Uptime: {uptime}")

        result['system']['swap_usage'] = swap_usage
        result['system']['cpu_load'] = cpu_load
        result['system']['uptime'] = uptime

        self.print_unless_quiet_mode(system_tree)
        self.print_unless_quiet_mode("")

    def collect_and_display_network_info(self, result: dict):
        """네트워크 정보 수집 및 출력"""
        network_tree = Tree("[bold]🛜 Network Interface[/bold]")

        # 공용 IP 정보
        ip_api_provider = getattr(self.args, 'ip_api_provider', "ip-api.com")
        if ip_api_provider == "ip-api.com":
            public_ip_info = get_location_with_ip_api()
            if public_ip_info.get('status'):
                del public_ip_info['status']

            result['network']['public_ip'] = {"ip": public_ip_info.get('query')}
            public_ip_tree = network_tree.add(f"[bold] Public IP[/bold]: {result['network']['public_ip']['ip']}")

            if result['network']['public_ip']:
                result['network']['public_ip'].update(public_ip_info)
                public_ip_tree.add(f"[bold] Region: {public_ip_info.get('countryCode')}, {public_ip_info.get('regionName')}, {public_ip_info.get('city')}, "
                                 f"{public_ip_info.get('country')}, Timezone={public_ip_info.get('timezone')}")
                public_ip_tree.add(f"[bold] ASN: {public_ip_info.get('as')}, ISP: {public_ip_info.get('isp')}, ORG: {public_ip_info.get('org')}")
        else:
            public_ip = get_public_ip()
            result['network']['public_ip'] = {"ip": public_ip}
            public_ip_tree = network_tree.add(f"[bold] Public IP[/bold]: {public_ip}")

            if result['network']['public_ip']:
                _location = get_location(public_ip)
                if _location:
                    result['network']['public_ip'].update(_location)
                    public_ip_tree.add(f"[bold] Region: {_location.get('region')}, Timezone={_location.get('timezone')}")
                    public_ip_tree.add(f"[bold] ASN: {dict_to_line(_location.get('asn'), end_separator=', ')}")

        # 로컬 IP 정보
        local_tree = network_tree.add("[bold] Local IP[/bold]")
        interface_list = get_interface_ips(ignore_interfaces=['lo0', 'lo'], detail=True)

        if interface_list:
            longest_length = max(len(item[0]) for item in interface_list)

            for interface, ipaddr in interface_list:
                subnet_str = f" / {ipaddr.get('subnet')}" if ipaddr.get('subnet') else ""
                gateway_str = f", G/W: {ipaddr.get('gateway')}" if ipaddr.get('gateway') else ""
                formatted_ipaddr = f"{ipaddr.get('ip'):<10}{subnet_str}{gateway_str}"

                result['network'][interface] = ipaddr
                if "gateway" in ipaddr:
                    interface = f"[bold blue][on #050B27]{interface:<{longest_length}} [/bold blue]"
                    formatted_ipaddr = f"{formatted_ipaddr}[/on #050B27]"
                local_tree.add(f"[bold]{interface:<{longest_length+1}}[/bold]: {formatted_ipaddr}")

        self.print_unless_quiet_mode(network_tree)
        self.print_unless_quiet_mode("")

    def collect_and_display_disk_info(self, result: dict):
        """디스크 정보 수집 및 출력"""
        disk_usage = DiskUsage()
        disk_usage_result = disk_usage.get_disk_usage("all", unit="auto")
        result['disk'] = disk_usage_result

        disk_tree = Tree("[bold]💾 Disk Usage[/bold]")
        for mount_point, usage in disk_usage_result.items():
            if 'error' in usage:
                continue

            color, percent = get_color_by_threshold(usage['percent'], return_tuple=True)
            color_unit = f"[grey74]{usage['unit']}[/grey74]"
            usage_line = f"[{color}]{usage['used']:>7}[/{color}] {color_unit}[{color}] / {usage['total']:>7}[/{color}] {color_unit} [{color}]({percent}%)[/{color}] "
            disk_tree.add(f"[bold blue]{mount_point:<11}[/bold blue][dim]{usage['device']}[/dim]: {usage_line}")

        self.print_unless_quiet_mode(disk_tree)

    def collect_info(self) -> dict:
        """정보 수집 (테스트용)"""
        result = {
            "system": {},
            "network": {},
            "disk": {},
        }

        # 시스템 정보 수집
        hostname = get_hostname()
        result['system']['hostname'] = hostname

        platform_info = get_platform_info()
        for k, v in platform_info.items():
            result['system'][k] = v

        # 네트워크 정보 수집
        interface_list = get_interface_ips(ignore_interfaces=['lo0', 'lo'], detail=True)
        if interface_list:
            for interface, ipaddr in interface_list:
                result['network'][interface] = ipaddr

        # 디스크 정보 수집
        disk_usage = DiskUsage()
        disk_usage_result = disk_usage.get_disk_usage("all", unit="auto")
        result['disk'] = disk_usage_result

        return result


def get_arguments(parser: ArgumentParser):
    """인수 정의 (레거시 호환)"""
    cli = InfoCLI()
    cli.get_arguments(parser)


def main():
    """메인 함수 (레거시 호환)"""
    cli = InfoCLI()
    return cli.main()


if __name__ == '__main__':
    sys.exit(main())
