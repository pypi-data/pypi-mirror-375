#!/usr/bin/env python3
"""
PawnStack CLI 메인 엔트리포인트

레거시 pawnlib.cli.main_cli와 호환되는 현대적인 CLI 시스템
"""

import os
import sys
import asyncio
import argparse
import importlib
from glob import glob
from pathlib import Path
from typing import Optional, Dict, Any

from pawnstack.config.global_config import pawn
from pawnstack.cli.formatter import ColoredHelpFormatter
from pawnstack.cli.parser import CustomArgumentParser
from pawnstack.cli.banner import generate_banner
from pawnstack import __version__


def get_real_path(file_path: str) -> Path:
    """파일의 실제 경로 반환"""
    return Path(os.path.dirname(os.path.abspath(file_path)))


def get_module_name(name: str) -> str:
    """파일명에서 모듈명 추출"""
    return os.path.basename(name)[:-3]


def get_submodule_names() -> list:
    """사용 가능한 하위 모듈 이름 목록 반환"""
    module_list = glob(os.path.join(get_real_path(__file__), "*.py"))
    main_cli_name = get_module_name(__file__)
    exclude_module_names = ["__init__", main_cli_name, "base", "parser", "formatter"]
    modules = []

    for module_file in module_list:
        module_name = get_module_name(module_file)
        if module_name not in exclude_module_names:
            modules.append(module_name)

    return modules


def run_module(module_name: str, args=None) -> Any:
    """CLI 모듈 실행"""
    try:
        module = importlib.import_module(f"pawnstack.cli.{module_name}")
        pawn.console.log(f"🔧 Loading pawnstack.cli.{module_name}")

        # CLI 클래스가 있는지 확인 (여러 패턴 시도)
        possible_class_names = [
            f"{module_name.upper()}CLI",      # HTTPCLI
            f"{module_name.title()}CLI",      # HttpCLI
            f"{module_name.capitalize()}CLI", # HttpCLI
            # 특별한 케이스들
            "WebSocketCLI" if module_name == "websocket" else None,
            "ProxyCLI" if module_name == "proxy" else None,
            "IconCLI" if module_name == "icon" else None,
            "ServerCLI" if module_name == "server" else None,
            "InfoCLI" if module_name == "info" else None,
            "BannerCLI" if module_name == "banner" else None,
            "MonCLI" if module_name == "mon" else None,
            "NotiCLI" if module_name == "noti" else None,
            "ScanKeyCLI" if module_name == "scan_key" else None,
            "AWSCLI" if module_name == "aws" else None,
            "S3CLI" if module_name == "s3" else None,
            "InspectCLI" if module_name == "inspect" else None,
            "DepsCLI" if module_name == "deps" else None,
        ]

        # None 값 제거
        possible_class_names = [name for name in possible_class_names if name is not None]

        cli_class = None
        cli_class_name = None

        for class_name in possible_class_names:
            if hasattr(module, class_name):
                cli_class = getattr(module, class_name)
                cli_class_name = class_name
                break

        if cli_class:
            if pawn.get('PAWN_DEBUG'):
                pawn.console.log(f"🐛 Found CLI class: {cli_class_name}")
            cli_instance = cli_class(args)
            if pawn.get('PAWN_DEBUG'):
                pawn.console.log(f"🐛 CLI instance created with args: {cli_instance.args}")
            return cli_instance.main()

        # 비동기 함수인지 확인
        elif asyncio.iscoroutinefunction(getattr(module, 'main', None)):
            pawn.console.log(f"⚡ '{module_name}.main' is async function. Running with asyncio.run().")
            try:
                asyncio.run(module.main())
            except Exception as e:
                pawn.console.log(f"[red]❌ Error during async execution of {module_name}: {e}")
                raise e

        # 일반 함수인지 확인
        elif callable(getattr(module, 'main', None)):
            pawn.console.log(f"🔄 '{module_name}.main' is sync function. Running directly.")
            # 레거시 main 함수는 사용하지 않음 - CLI 클래스를 우선 사용
            pawn.console.log(f"[yellow]⚠️  Module '{module_name}' uses legacy main() function. Consider using {cli_class_name} class.")
            module.main()
        else:
            pawn.console.log(f"[red]❌ Module '{module_name}' does not have a main() function or CLI class.")
            sys.exit(1)

        return module

    except ImportError as e:
        pawn.console.log(f"[red]❌ Failed to import module {module_name}: {e}")
        sys.exit(1)
    except Exception as e:
        pawn.console.log(f"[red]❌ Error running module {module_name}: {e}")
        if pawn.get('PAWN_DEBUG'):
            pawn.console.print_exception(show_locals=True, width=160)
        sys.exit(1)


def parse_args(parser: argparse.ArgumentParser, commands) -> tuple:
    """명령줄 인수 파싱"""
    command = sys.argv[1] if len(sys.argv) > 1 else None

    # 명령어별 인수 파싱
    try:
        # 전체 인수를 파싱하되, 알려지지 않은 인수는 무시
        args, unknown = parser.parse_known_args()

        # 전역 디버그 설정 적용
        if hasattr(args, 'debug') and args.debug:
            pawn.set(PAWN_DEBUG=True)

        if hasattr(args, 'no_color') and args.no_color:
            pawn.set(PAWN_NO_COLOR=True)

        # 디버깅 정보 출력
        if pawn.get('PAWN_DEBUG'):
            pawn.console.log(f"🐛 Parsed args: {args}")
            pawn.console.log(f"🐛 Unknown args: {unknown}")
            pawn.console.log(f"🐛 Command: {command}")

        return args, command
    except SystemExit:
        raise


def get_sys_argv() -> str:
    """첫 번째 시스템 인수 반환"""
    return sys.argv[1] if len(sys.argv) > 1 else ""


def load_cli_module(commands, module_name: str, load_arguments: bool = True):
    """CLI 모듈 로드 및 파서 등록"""
    pawn.console.log(f"📦 Adding parser for '{module_name}'")

    try:
        module = importlib.import_module(f"pawnstack.cli.{module_name}")

        # 모듈 메타데이터 가져오기
        description = getattr(module, "__description__", f"{module_name} module")
        epilog = getattr(module, "__epilog__", "")

        if isinstance(epilog, tuple):
            epilog = "\n".join(epilog)

        # 서브파서 추가 - 독립적인 인수 네임스페이스와 conflict_handler 사용
        _parser = commands.add_parser(
            module_name,
            help=f'{description}',
            epilog=epilog,
            formatter_class=ColoredHelpFormatter,
            description=description.upper(),
            conflict_handler='resolve',  # 인수 충돌시 나중에 추가된 것으로 덮어쓰기
            add_help=True,  # 각 서브커맨드에 독립적인 help 추가
        )

        # 인수 로드가 필요한 경우에만 수행
        if not load_arguments:
            return

        # CLI 클래스에서 인수 정의 가져오기
        cli_class = None
        possible_class_names = [
            f"{module_name.upper()}CLI",
            f"{module_name.title()}CLI",
            f"{module_name.capitalize()}CLI",
            "WebSocketCLI" if module_name == "websocket" else None,
            "ProxyCLI" if module_name == "proxy" else None,
            "IconCLI" if module_name == "icon" else None,
            "ServerCLI" if module_name == "server" else None,
            "InfoCLI" if module_name == "info" else None,
            "BannerCLI" if module_name == "banner" else None,
            "MonCLI" if module_name == "mon" else None,
            "NotiCLI" if module_name == "noti" else None,
            "ScanKeyCLI" if module_name == "scan_key" else None,
            "AWSCLI" if module_name == "aws" else None,
            "S3CLI" if module_name == "s3" else None,
            "InspectCLI" if module_name == "inspect" else None,
            "DepsCLI" if module_name == "deps" else None,
        ]

        # None 값 제거
        possible_class_names = [name for name in possible_class_names if name is not None]

        for class_name in possible_class_names:
            if hasattr(module, class_name):
                cli_class = getattr(module, class_name)
                break

        # CLI 클래스의 get_arguments 메서드 호출
        if cli_class and hasattr(cli_class, 'get_arguments'):
            # 임시 인스턴스 생성하여 인수 정의 가져오기
            try:
                temp_instance = cli_class()
                temp_instance.get_arguments(_parser)
            except Exception as e:
                pawn.console.log(f"[yellow]⚠️  Failed to get arguments for {cli_class.__name__}: {e}")
        elif hasattr(module, 'get_arguments'):
            try:
                module.get_arguments(_parser)
            except Exception as e:
                pawn.console.log(f"[yellow]⚠️  Failed to get arguments from module.get_arguments: {e}")
        elif hasattr(module, 'define_arguments'):
            try:
                module.define_arguments(_parser)
            except Exception as e:
                pawn.console.log(f"[yellow]⚠️  Failed to define arguments from module.define_arguments: {e}")
        else:
            pawn.console.log(f"[yellow]⚠️  Module {module_name} has no argument definition function")

    except ImportError as e:
        pawn.console.log(f"[red]❌ Failed to load module {module_name}: {e}")
    except argparse.ArgumentError as e:
        # 인수 충돌 에러 처리
        pawn.console.log(f"❌ Error loading module {module_name}: {e}")
    except Exception as e:
        pawn.console.log(f"[red]❌ Error loading module {module_name}: {e}")


def get_args() -> tuple:
    """CLI 인수 파싱 및 설정"""
    # 사용자 입력 명령어 확인
    command = get_sys_argv()
    available_modules = get_submodule_names()

    # 메인 파서 생성 - 전역 옵션은 최소화
    # 배너는 한 번만 표시되도록 설정
    banner_text = generate_banner(app_name="PAWNS", version=__version__, author="PawnStack", font="graffiti")

    # 메인 파서 생성
    parser = argparse.ArgumentParser(
        prog=os.path.basename(sys.argv[0]),
        usage=banner_text,
        description="PawnStack CLI - Modern Infrastructure as Code toolkit",
        formatter_class=ColoredHelpFormatter,
        add_help=True,
    )

    # 전역 옵션은 메인 파서에만 추가 (서브커맨드 파서에는 추가하지 않음)
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )

    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )

    # 서브명령어 파서 추가 - 부모 파서 상속 없이 독립적으로 생성
    commands = parser.add_subparsers(title='Available Commands', dest='command', help='Available commands')

    # 명령어가 유효한 하위 모듈인지 확인
    if command and command in available_modules:
        # 특정 명령어만 로드 (인수 포함)
        try:
            load_cli_module(commands, command, load_arguments=True)
        except Exception as e:
            pawn.console.log(f"❌ Error loading module {command}: {e}")
            # 에러가 발생해도 help를 보여주기 위해 인수 없이 로드
            try:
                load_cli_module(commands, command, load_arguments=False)
            except:
                pass
    else:
        # 모든 사용 가능한 모듈 로드 - help 표시용으로만 기본 정보 로드
        for module_name in available_modules:
            try:
                # 전체 목록 표시시에는 인수를 로드하지 않음 (충돌 방지)
                module = importlib.import_module(f"pawnstack.cli.{module_name}")
                description = getattr(module, "__description__", f"{module_name} module")
                epilog = getattr(module, "__epilog__", "")
                if isinstance(epilog, tuple):
                    epilog = "\n".join(epilog)

                # 서브파서만 추가, 인수는 추가하지 않음
                _parser = commands.add_parser(
                    module_name,
                    help=f'{description}',
                    formatter_class=ColoredHelpFormatter,
                    conflict_handler='resolve',
                    add_help=False,  # 전체 목록에서는 help 비활성화
                )
            except Exception as e:
                pawn.console.log(f"❌ Error loading module {module_name}: {e}")

    # 인수 파싱
    try:
        args, command = parse_args(parser, commands)
        return args, command, parser
    except SystemExit as e:
        # 도움말이나 오류로 인한 종료
        if e.code != 0:
            # 오류인 경우만 처리 (help는 정상 종료)
            pass
        sys.exit(e.code)


def cleanup_args():
    """시스템 인수 정리"""
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        pawn.console.log(f"🧹 Removing argument '{sys.argv[1]}' from {sys.argv}")
        del sys.argv[1]


def run_with_keyboard_interrupt(func):
    """키보드 인터럽트 처리 래퍼"""
    try:
        func()
    except KeyboardInterrupt:
        pawn.console.log("\n[yellow]⚠️  Operation cancelled by user (Ctrl+C)")
        sys.exit(130)  # Standard exit code for Ctrl+C
    except Exception as e:
        pawn.console.log(f"[red]❌ Unexpected error: {e}")
        if pawn.get('PAWN_DEBUG'):
            pawn.console.print_exception(show_locals=True, width=160)
        sys.exit(1)


def main():
    """메인 CLI 엔트리포인트"""
    pawn.console.log("🚀 Starting PawnStack CLI")

    # 전역 설정
    pawn.set(PAWN_LINE=False)

    args, command, parser = None, None, None

    try:
        pawn.console.log(f"📝 Command line arguments: {sys.argv}")
        args, command, parser = get_args()
        pawn.console.log(f"🎯 Selected command: {command}")
        cleanup_args()

    except Exception as e:
        pawn.console.log(f"[red]❌ Exception while parsing arguments: {e}")
        if pawn.get('PAWN_DEBUG'):
            pawn.console.print_exception(show_locals=True, width=160)
        sys.exit(1)

    pawn.console.log(f"🔍 Command: {command}, Parser: {parser is not None}, Args: {args is not None}")

    if command:
        try:
            # 명령어별 인수 가져오기 - args 자체를 전달
            if pawn.get('PAWN_DEBUG'):
                pawn.console.log(f"🐛 Passing args to {command}: {args}")
            run_module(command, args)
        except KeyboardInterrupt:
            pawn.console.log("[yellow]⚠️  KeyboardInterrupt")
            sys.exit(130)
        except Exception as e:
            if pawn.get('PAWN_DEBUG'):
                pawn.console.print_exception(show_locals=True, width=160)
            else:
                pawn.console.log(f"[red]❌ {e}")
            sys.exit(1)
    else:
        # No command provided - show help
        if parser:
            parser.print_help()
        else:
            pawn.console.log("[red]❌ No parser available")
        sys.exit(1)


if __name__ == '__main__':
    run_with_keyboard_interrupt(main)
