"""
PawnStack CLI 파서

커스텀 ArgumentParser 및 관련 유틸리티
"""

import argparse
import sys
from typing import Optional, List, Any

from pawnstack.config.global_config import pawn


class CustomArgumentParser(argparse.ArgumentParser):
    """PawnStack용 커스텀 ArgumentParser"""
    
    def __init__(self, *args, **kwargs):
        # 기본 설정
        kwargs.setdefault('add_help', True)
        kwargs.setdefault('allow_abbrev', False)
        
        super().__init__(*args, **kwargs)
        
        # 전역 옵션 추가
        self.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug mode'
        )
        
        self.add_argument(
            '--verbose', '-v',
            action='count',
            default=0,
            help='Increase verbosity (use -v, -vv, -vvv for more verbose)'
        )
        
        self.add_argument(
            '--config',
            type=str,
            help='Configuration file path'
        )
        
        self.add_argument(
            '--no-color',
            action='store_true',
            help='Disable colored output'
        )
    
    def error(self, message):
        """오류 메시지 출력 및 종료"""
        # Don't print help again if usage was already shown
        # Just print the error message
        sys.stderr.write(f"{self.prog}: error: {message}\n")
        sys.exit(2)
    
    def parse_args(self, args=None, namespace=None):
        """인수 파싱 및 전역 설정 적용"""
        parsed_args = super().parse_args(args, namespace)
        
        # 전역 설정 적용
        if hasattr(parsed_args, 'debug') and parsed_args.debug:
            pawn.set(PAWN_DEBUG=True)
        
        if hasattr(parsed_args, 'verbose') and parsed_args.verbose:
            pawn.set(PAWN_VERBOSE=parsed_args.verbose)
        
        if hasattr(parsed_args, 'config') and parsed_args.config:
            pawn.set(PAWN_CONFIG_FILE=parsed_args.config)
        
        if hasattr(parsed_args, 'no_color') and parsed_args.no_color:
            pawn.set(PAWN_NO_COLOR=True)
        
        return parsed_args
    
    def format_help(self):
        """도움말 포맷팅"""
        help_text = super().format_help()
        
        # 추가 정보 포함
        footer = "\n" + "=" * 50 + "\n"
        footer += "PawnStack CLI - Modern Infrastructure as Code toolkit\n"
        footer += f"Version: {pawn.version}\n"
        footer += "For more information, visit: https://github.com/JINWOO-J/pawnstack\n"
        footer += "=" * 50 + "\n"
        
        return help_text + footer


class OrderedNamespace(argparse.Namespace):
    """명령어 순서를 추적하는 네임스페이스"""
    
    def __init__(self, **kwargs):
        self.command_order = []
        super().__init__(**kwargs)
    
    def __setattr__(self, name, value):
        name = name.replace('-', '_')
        if value and name not in self.command_order and not name.startswith('_'):
            self.command_order.append(name)
        super().__setattr__(name, value)


def parse_args_into_namespaces(parser: argparse.ArgumentParser, commands) -> OrderedNamespace:
    """
    명령어별로 인수를 분리하여 네임스페이스에 저장
    
    Example: `add 2 mul 5 --repeat 3`
    -> add 명령어와 mul 명령어를 순차적으로 처리
    """
    
    # argv를 명령어별로 분할
    split_argv = [[]]
    for c in sys.argv[1:]:
        if hasattr(commands, 'choices') and c in commands.choices:
            split_argv.append([c])
        else:
            split_argv[-1].append(c)
    
    # 전역 네임스페이스 생성
    args = OrderedNamespace()
    cmd, args_raw = 'globals', split_argv.pop(0)
    
    # 전역 인수 파싱
    args_parsed = parser.parse_args(args_raw, namespace=OrderedNamespace())
    setattr(args, cmd, args_parsed)
    
    # 각 명령어별 인수 파싱
    pos = 0
    while len(split_argv):
        pos += 1
        cmd, *args_raw = split_argv.pop(0)
        
        assert cmd[0].isalpha(), 'Command must start with a letter.'
        
        if hasattr(commands, 'choices') and cmd in commands.choices:
            args_parsed = commands.choices[cmd].parse_args(args_raw, namespace=OrderedNamespace())
            setattr(args, f'{cmd}~{pos}', args_parsed)
    
    return args


def remove_argument(parser: argparse.ArgumentParser, arg: str):
    """파서에서 특정 인수 제거"""
    for action in parser._actions:
        opts = action.option_strings
        if (opts and opts[0] == arg) or action.dest == arg:
            parser._remove_action(action)
            pawn.console.log(f"🗑️  Removed argument: {arg}")
            break
    
    for action in parser._action_groups:
        for group_action in action._group_actions:
            if group_action.dest == arg:
                action._group_actions.remove(group_action)
                pawn.console.log(f"🗑️  Removed group argument: {arg}")
                return


def add_common_arguments(parser: argparse.ArgumentParser):
    """공통 인수 추가"""
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    
    parser.add_argument(
        '--retry',
        type=int,
        default=3,
        help='Number of retries (default: 3)'
    )
    
    parser.add_argument(
        '--output', '-o',
        choices=['json', 'yaml', 'table', 'text'],
        default='table',
        help='Output format (default: table)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress output'
    )


def validate_required_args(args: argparse.Namespace, required_fields: List[str]) -> bool:
    """필수 인수 검증"""
    missing_fields = []
    
    for field in required_fields:
        if not hasattr(args, field) or getattr(args, field) is None:
            missing_fields.append(field)
    
    if missing_fields:
        pawn.console.log(f"[red]❌ Missing required arguments: {', '.join(missing_fields)}")
        return False
    
    return True


def setup_logging_from_args(args: argparse.Namespace):
    """인수에서 로깅 설정"""
    if hasattr(args, 'debug') and args.debug:
        pawn.set(PAWN_DEBUG=True)
        pawn.console.log("🐛 Debug mode enabled")
    
    if hasattr(args, 'verbose') and args.verbose:
        pawn.set(PAWN_VERBOSE=args.verbose)
        pawn.console.log(f"📢 Verbose level: {args.verbose}")
    
    if hasattr(args, 'quiet') and args.quiet:
        pawn.set(PAWN_QUIET=True)
        pawn.console.log("🤫 Quiet mode enabled")