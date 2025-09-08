"""출력 모듈"""

from rich.console import Console
from rich.syntax import Syntax

__all__ = ["syntax_highlight", "print_syntax"]

console = Console()

def syntax_highlight(code: str, language: str = "python", theme: str = "monokai") -> Syntax:
    """
    코드에 문법 강조를 적용합니다.
    
    :param code: 문법 강조를 적용할 코드
    :param language: 언어 (기본값: "python")
    :param theme: 테마 (기본값: "monokai")
    :return: Syntax 객체
    """
    return Syntax(code, language, theme=theme, line_numbers=True)

def print_syntax(code: str, language: str = "python", theme: str = "monokai") -> None:
    """
    코드를 문법 강조하여 출력합니다.
    
    :param code: 문법 강조를 적용할 코드
    :param language: 언어 (기본값: "python")
    :param theme: 테마 (기본값: "monokai")
    """
    syntax = syntax_highlight(code, language, theme)
    console.print(syntax)