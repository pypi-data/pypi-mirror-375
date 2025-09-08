"""
PawnStack CLI 포맷터

Rich 기반의 컬러 도움말 포맷터
"""

import argparse
from rich.console import Console
from rich.text import Text
from rich.panel import Panel


class ColoredHelpFormatter(argparse.HelpFormatter):
    """Rich를 사용한 컬러 도움말 포맷터"""
    
    def __init__(self, prog, indent_increment=2, max_help_position=24, width=None):
        super().__init__(prog, indent_increment, max_help_position, width)
        self.console = Console()
    
    def _format_usage(self, usage, actions, groups, prefix):
        """사용법 포맷팅"""
        if prefix is None:
            prefix = 'usage: '
        
        # 기본 사용법 생성
        usage_text = super()._format_usage(usage, actions, groups, prefix)
        
        # Rich 스타일 적용
        styled_usage = Text()
        styled_usage.append("Usage: ", style="bold cyan")
        styled_usage.append(usage_text.replace(prefix, "").strip(), style="white")
        
        return str(styled_usage) + "\n"
    
    def _format_action(self, action):
        """액션 포맷팅"""
        # 기본 포맷팅 가져오기
        help_text = super()._format_action(action)
        
        if not help_text:
            return help_text
        
        # 옵션 이름 스타일링
        lines = help_text.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip():
                # 옵션 라인인지 확인
                if line.startswith('  -') or line.startswith('  --'):
                    # 옵션 부분과 도움말 부분 분리
                    parts = line.split('  ', 2)
                    if len(parts) >= 3:
                        indent = parts[0]
                        option = parts[1]
                        help_desc = parts[2] if len(parts) > 2 else ""
                        
                        styled_line = Text()
                        styled_line.append(indent)
                        styled_line.append(option, style="bold green")
                        styled_line.append("  ")
                        styled_line.append(help_desc, style="white")
                        formatted_lines.append(str(styled_line))
                    else:
                        formatted_lines.append(line)
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def format_help(self):
        """전체 도움말 포맷팅"""
        help_text = super().format_help()
        
        # 섹션별 스타일링
        lines = help_text.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line and not line.startswith(' '):
                # 섹션 헤더
                if line.endswith(':'):
                    styled_line = Text()
                    styled_line.append(line, style="bold yellow")
                    formatted_lines.append(str(styled_line))
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)


class NewlineHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """개행을 보존하는 도움말 포맷터"""
    
    def _fill_text(self, text, width, indent):
        """텍스트 채우기 (개행 보존)"""
        return ''.join(indent + line for line in text.splitlines(keepends=True))
    
    def _split_lines(self, text, width):
        """라인 분할 (개행 보존)"""
        return text.splitlines()


class PanelHelpFormatter(ColoredHelpFormatter):
    """패널 스타일 도움말 포맷터"""
    
    def format_help(self):
        """패널로 감싼 도움말 포맷팅"""
        help_text = super().format_help()
        
        # Rich 패널로 감싸기
        panel = Panel(
            help_text,
            title="[bold cyan]PawnStack CLI Help[/bold cyan]",
            border_style="blue",
            padding=(1, 2)
        )
        
        # 콘솔에 출력하지 않고 문자열로 반환
        with self.console.capture() as capture:
            self.console.print(panel)
        
        return capture.get()