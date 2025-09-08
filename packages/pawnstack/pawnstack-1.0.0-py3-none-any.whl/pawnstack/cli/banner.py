"""
PawnStack CLI 배너 생성기

ASCII 아트 배너 및 버전 정보 생성
"""

import os
from typing import Optional, Dict
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

# ASCII 폰트 정의
FONTS = {
    "graffiti": {
        "A": ["  ▄▄▄  ", " ▄▀   ▀▄", "▄▀     ▀▄", "█  ▄▀▄  █", "█ ▀   ▀ █", "▀▄     ▄▀", " ▀▄▄▄▄▄▀ "],
        "B": ["██████▄ ", "█     █ ", "█     █ ", "██████▄ ", "█     █ ", "█     █ ", "██████▀ "],
        "C": [" ▄▄▄▄▄▄ ", "█       ", "█       ", "█       ", "█       ", "█       ", " ▀▀▀▀▀▀ "],
        "D": ["██████▄ ", "█     █ ", "█     █ ", "█     █ ", "█     █ ", "█     █ ", "██████▀ "],
        "E": ["███████ ", "█       ", "█       ", "██████  ", "█       ", "█       ", "███████ "],
        "F": ["███████ ", "█       ", "█       ", "██████  ", "█       ", "█       ", "█       "],
        "G": [" ▄▄▄▄▄▄ ", "█       ", "█       ", "█  ████ ", "█     █ ", "█     █ ", " ▀▀▀▀▀▀ "],
        "H": ["█     █ ", "█     █ ", "█     █ ", "███████ ", "█     █ ", "█     █ ", "█     █ "],
        "I": ["███████ ", "   █    ", "   █    ", "   █    ", "   █    ", "   █    ", "███████ "],
        "J": ["███████ ", "      █ ", "      █ ", "      █ ", "█     █ ", "█     █ ", " ▀▀▀▀▀▀ "],
        "K": ["█     █ ", "█   ▄▀  ", "█ ▄▀    ", "██      ", "█ ▀▄    ", "█   ▀▄  ", "█     █ "],
        "L": ["█       ", "█       ", "█       ", "█       ", "█       ", "█       ", "███████ "],
        "M": ["█     █ ", "██   ██ ", "█ █ █ █ ", "█  █  █ ", "█     █ ", "█     █ ", "█     █ "],
        "N": ["█▄    █ ", "██▄   █ ", "█ █▄  █ ", "█  █▄ █ ", "█   ██ █", "█    ██ ", "█     █ "],
        "O": [" ▄▄▄▄▄▄ ", "█      █", "█      █", "█      █", "█      █", "█      █", " ▀▀▀▀▀▀ "],
        "P": ["██████▄ ", "█     █ ", "█     █ ", "██████▀ ", "█       ", "█       ", "█       "],
        "Q": [" ▄▄▄▄▄▄ ", "█      █", "█      █", "█   █  █", "█    █ █", "█     ██", " ▀▀▀▀▀█ "],
        "R": ["██████▄ ", "█     █ ", "█     █ ", "██████▀ ", "█   ▀▄  ", "█     ▀▄", "█      █"],
        "S": [" ▄▄▄▄▄▄ ", "█       ", "█       ", " ▀▀▀▀▀█ ", "      █ ", "      █ ", " ▄▄▄▄▄▀ "],
        "T": ["███████ ", "   █    ", "   █    ", "   █    ", "   █    ", "   █    ", "   █    "],
        "U": ["█     █ ", "█     █ ", "█     █ ", "█     █ ", "█     █ ", "█     █ ", " ▀▀▀▀▀▀ "],
        "V": ["█     █ ", "█     █ ", "█     █ ", "█     █ ", " █   █  ", "  █ █   ", "   █    "],
        "W": ["█     █ ", "█  █  █ ", "█  █  █ ", "█  █  █ ", "█ ▀█▀ █ ", "█  █  █ ", "▀▄   ▄▀ "],
        "X": ["█     █ ", " █   █  ", "  █ █   ", "   █    ", "  █ █   ", " █   █  ", "█     █ "],
        "Y": ["█     █ ", " █   █  ", "  █ █   ", "   █    ", "   █    ", "   █    ", "   █    "],
        "Z": ["███████ ", "     █  ", "    █   ", "   █    ", "  █     ", " █      ", "███████ "],
        " ": ["        ", "        ", "        ", "        ", "        ", "        ", "        "],
    },
    "block": {
        "P": ["██████  ", "██   ██ ", "██████  ", "██      ", "██      ", "        "],
        "A": ["   ██   ", "  ████  ", " ██  ██ ", "████████", "██    ██", "        "],
        "W": ["██    ██", "██    ██", "██ ██ ██", "████████", "██    ██", "        "],
        "N": ["███    █", "████   █", "██ ██  █", "██  ██ █", "██   ███", "        "],
        "S": ["███████ ", "██      ", "███████ ", "      ██", "███████ ", "        "],
        " ": ["        ", "        ", "        ", "        ", "        ", "        "],
    },
    "simple": {
        "P": ["PPPP ", "P   P", "PPPP ", "P    ", "P    "],
        "A": [" AAA ", "A   A", "AAAAA", "A   A", "A   A"],
        "W": ["W   W", "W   W", "W W W", "WW WW", "W   W"],
        "N": ["N   N", "NN  N", "N N N", "N  NN", "N   N"],
        "S": ["SSSSS", "S    ", "SSSS ", "    S", "SSSSS"],
        " ": ["     ", "     ", "     ", "     ", "     "],
    }
}


def generate_ascii_text(text: str, font: str = "graffiti") -> list:
    """ASCII 아트 텍스트 생성"""
    if font not in FONTS:
        font = "graffiti"
    
    font_data = FONTS[font]
    text = text.upper()
    
    # 폰트 높이 계산
    height = len(next(iter(font_data.values())))
    
    # 각 라인별로 문자 조합
    lines = [""] * height
    
    for char in text:
        if char in font_data:
            char_lines = font_data[char]
            for i in range(height):
                lines[i] += char_lines[i] if i < len(char_lines) else " " * len(char_lines[0])
        else:
            # 지원하지 않는 문자는 공백으로 처리
            space_width = len(font_data.get(" ", ["        "])[0])
            for i in range(height):
                lines[i] += " " * space_width
    
    return lines


def generate_banner(
    app_name: str = "PAWNS",
    version: str = "1.0.0",
    author: str = "PawnStack",
    font: str = "graffiti",
    width: Optional[int] = None,
    style: str = "cyan"
) -> str:
    """CLI 배너 생성"""
    
    console = Console()
    
    # ASCII 아트 생성
    ascii_lines = generate_ascii_text(app_name, font)
    
    # 배너 텍스트 구성
    banner_text = Text()
    
    # ASCII 아트 추가
    for line in ascii_lines:
        banner_text.append(line + "\n", style=f"bold {style}")
    
    # 버전 정보 추가
    banner_text.append(f"\nVersion: {version}\n", style="bold white")
    banner_text.append(f"Author: {author}\n", style="dim white")
    
    # 설명 추가
    banner_text.append("\nModern Infrastructure as Code toolkit\n", style="italic yellow")
    
    # 패널로 감싸기
    panel = Panel(
        Align.center(banner_text),
        border_style=style,
        padding=(1, 2),
        title="[bold white]PawnStack CLI[/bold white]",
        subtitle="[dim]Ready to deploy[/dim]"
    )
    
    # 문자열로 변환
    with console.capture() as capture:
        console.print(panel)
    
    return capture.get()


def generate_simple_banner(app_name: str, version: str) -> str:
    """간단한 배너 생성"""
    return f"""
╭─────────────────────────────────────────╮
│  {app_name:<20} v{version:<10}  │
│  Modern Infrastructure as Code toolkit  │
╰─────────────────────────────────────────╯
"""


def generate_version_info(
    app_name: str = "PawnStack",
    version: str = "1.0.0",
    python_version: str = None,
    platform: str = None
) -> str:
    """버전 정보 생성"""
    import sys
    import platform as plt
    
    if python_version is None:
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    if platform is None:
        platform = plt.system()
    
    info_text = Text()
    info_text.append(f"{app_name} ", style="bold cyan")
    info_text.append(f"v{version}\n", style="bold white")
    info_text.append(f"Python {python_version} on {platform}\n", style="dim white")
    
    return str(info_text)


def print_startup_banner():
    """시작 배너 출력"""
    from pawnstack import __version__
    from pawnstack.config.global_config import pawn
    
    banner = generate_banner(
        app_name="PAWNS",
        version=__version__,
        author="PawnStack Team",
        font="graffiti"
    )
    
    pawn.console.print(banner)


def print_completion_banner(command: str, duration: float = None):
    """완료 배너 출력"""
    from pawnstack.config.global_config import pawn
    
    completion_text = Text()
    completion_text.append("✅ ", style="bold green")
    completion_text.append(f"Command '{command}' completed successfully", style="bold white")
    
    if duration:
        completion_text.append(f" in {duration:.2f}s", style="dim white")
    
    panel = Panel(
        Align.center(completion_text),
        border_style="green",
        padding=(0, 2)
    )
    
    pawn.console.print(panel)


def print_error_banner(command: str, error: str):
    """오류 배너 출력"""
    from pawnstack.config.global_config import pawn
    
    error_text = Text()
    error_text.append("❌ ", style="bold red")
    error_text.append(f"Command '{command}' failed\n", style="bold white")
    error_text.append(f"Error: {error}", style="red")
    
    panel = Panel(
        error_text,
        border_style="red",
        padding=(1, 2),
        title="[bold red]Error[/bold red]"
    )
    
    pawn.console.print(panel)


# CLI 명령어 부분 추가
import sys
from argparse import ArgumentParser
from pawnstack.cli.base import BaseCLI

# 모듈 메타데이터
__description__ = "Generate and display ASCII art banners"
__epilog__ = "Create beautiful ASCII art banners with various fonts and styles"


class BannerCLI(BaseCLI):
    """배너 생성 CLI"""
    
    def get_arguments(self, parser: ArgumentParser):
        """인수 정의"""
        parser.add_argument(
            'text',
            nargs='?',
            default='PAWNS',
            help='Text to convert to ASCII art (default: PAWNS)'
        )
        
        parser.add_argument(
            '--font',
            choices=['graffiti', 'block', 'simple'],
            default='graffiti',
            help='Font style (default: graffiti)'
        )
        
        parser.add_argument(
            '--style',
            choices=['cyan', 'green', 'red', 'yellow', 'blue', 'magenta'],
            default='cyan',
            help='Color style (default: cyan)'
        )
        
        parser.add_argument(
            '--version',
            type=str,
            help='Version to display'
        )
        
        parser.add_argument(
            '--author',
            type=str,
            default='PawnStack',
            help='Author name (default: PawnStack)'
        )
        
        parser.add_argument(
            '--simple',
            action='store_true',
            help='Use simple banner format'
        )
    
    def run(self) -> int:
        """배너 생성 및 출력"""
        from pawnstack import __version__
        
        text = getattr(self.args, 'text', 'PAWNS')
        version = getattr(self.args, 'version', None) or __version__
        author = getattr(self.args, 'author', 'PawnStack')
        font = getattr(self.args, 'font', 'graffiti')
        style = getattr(self.args, 'style', 'cyan')
        simple = getattr(self.args, 'simple', False)
        
        if simple:
            banner = generate_simple_banner(text, version)
            print(banner)
        else:
            banner = generate_banner(
                app_name=text,
                version=version,
                author=author,
                font=font,
                style=style
            )
            print(banner)
        
        return 0


def get_arguments(parser: ArgumentParser):
    """인수 정의 (레거시 호환)"""
    cli = BannerCLI()
    cli.get_arguments(parser)


def main():
    """메인 함수 (레거시 호환)"""
    cli = BannerCLI()
    return cli.main()


if __name__ == '__main__':
    sys.exit(main())