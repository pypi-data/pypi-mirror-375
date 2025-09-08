"""고급 로깅 시스템"""

from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

from pawnstack.config.settings import LoggingConfig


class Logger:
    """PawnStack 로거 클래스"""

    def __init__(self, config: LoggingConfig) -> None:
        """
        로거 초기화

        Args:
            config: 로깅 설정
        """
        self.config = config
        self._logger = logging.getLogger("pawnstack")
        self._console: Optional[Console] = None

        self._setup_logger()

    def _setup_logger(self) -> None:
        """로거 설정"""
        # 기존 핸들러 제거
        for handler in self._logger.handlers[:]:
            self._logger.removeHandler(handler)

        # 로그 레벨 설정
        self._logger.setLevel(getattr(logging, self.config.level.upper()))

        # 콘솔 핸들러 설정
        if self.config.enable_console:
            if self.config.enable_rich:
                self._setup_rich_handler()
            else:
                self._setup_console_handler()

        # 파일 핸들러 설정
        if self.config.file_path:
            self._setup_file_handler()

    def _setup_rich_handler(self) -> None:
        """Rich 콘솔 핸들러 설정"""
        self._console = Console()

        rich_handler = RichHandler(
            console=self._console,
            show_time=True,
            show_path=True,
            markup=True,
            rich_tracebacks=True,
        )
        rich_handler.setLevel(getattr(logging, self.config.level.upper()))

        self._logger.addHandler(rich_handler)

    def _setup_console_handler(self) -> None:
        """기본 콘솔 핸들러 설정"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.config.level.upper()))

        formatter = logging.Formatter(self.config.format)
        console_handler.setFormatter(formatter)

        self._logger.addHandler(console_handler)

    def _setup_file_handler(self) -> None:
        """파일 핸들러 설정"""
        if not self.config.file_path:
            return

        # 로그 디렉토리 생성
        log_dir = self.config.file_path.parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # 회전 파일 핸들러 설정
        file_handler = logging.handlers.RotatingFileHandler(
            filename=self.config.file_path,
            maxBytes=self.config.max_file_size,
            backupCount=self.config.backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(getattr(logging, self.config.level.upper()))

        formatter = logging.Formatter(self.config.format)
        file_handler.setFormatter(formatter)

        self._logger.addHandler(file_handler)

    @property
    def console(self) -> Optional[Console]:
        """Rich 콘솔 인스턴스"""
        return self._console

    def debug(self, message: str, *args, **kwargs) -> None:
        """디버그 로그"""
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """정보 로그"""
        self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """경고 로그"""
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """에러 로그"""
        self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """치명적 에러 로그"""
        self._logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        """예외 로그 (스택 트레이스 포함)"""
        self._logger.exception(message, *args, **kwargs)
