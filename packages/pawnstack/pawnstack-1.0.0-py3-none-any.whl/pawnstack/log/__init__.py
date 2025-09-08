"""로깅 모듈"""

from __future__ import annotations

import inspect
import logging
import logging.handlers
import sys
import datetime
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console  # type: ignore
    from rich.logging import RichHandler  # type: ignore
except Exception:  # rich 미설치 환경도 동작하도록
    Console = None  # type: ignore
    RichHandler = None  # type: ignore

__all__ = [
    "setup", "get_logger", "get_console",
    "set_level", "add_rotating_file_handler",
    "Log", "MicrosecondFormatter", "AppLogger",  # AppLogger 추가
]

_configured = False
_console: Optional["Console"] = None  # rich 콘솔(선택)


class MicrosecondFormatter(logging.Formatter):
    """마이크로초까지 지원하는 포맷터 클래스"""

    def formatTime(self, record, datefmt=None):
        """마이크로초 정밀도로 시간 포맷팅"""
        ct = datetime.datetime.fromtimestamp(record.created)
        if datefmt:
            if "%f" in datefmt:
                msec = ct.strftime("%f")[:3]  # 밀리초만 사용 (마이크로초 앞 3자리)
                datefmt = datefmt.replace("%f", msec)
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%H:%M:%S")
            s = f"{t},{ct.strftime('%f')[:3]}"
        return s


# AppLogger 클래스 추가
class AppLogger:
    """기존 AppLogger와 호환되는 클래스"""

    def __init__(self, name: Optional[str] = None):
        self._logger = get_logger(name)

    def debug(self, msg: str, *args, **kwargs) -> None:
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        self._logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        self._logger.exception(msg, *args, **kwargs)

    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """Get a logger instance."""
        return get_logger(name)


def setup(
    *,
    level: str | int = "INFO",
    enable_console: bool = True,
    enable_rich: bool = True,
    fmt: str | None = None,
    file_path: str | Path | None = None,
    max_file_size: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    show_path: bool = True,
    show_time: bool = True,
) -> None:
    """전역 로깅 초기화(앱 시작 시 1회)."""
    global _configured, _console
    if _configured:
        return

    root = logging.getLogger()
    root.handlers.clear()

    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    root.setLevel(level)

    # 콘솔 핸들러
    if enable_console:
        if enable_rich and RichHandler is not None and Console is not None:
            _console = Console()
            handler = RichHandler(
                console=_console,
                rich_tracebacks=True,
                show_path=show_path,
                show_time=show_time,
            )
            # Rich 핸들러용 커스텀 시간 포맷 설정
            handler = RichHandler(
                console=_console,
                rich_tracebacks=True,
                show_path=show_path,
                show_time=show_time,
                omit_repeated_times=False,
                log_time_format=lambda dt: f"[{dt.strftime('%H:%M:%S,%f')[:-3]}]",  # 일관된 시간 포맷 적용 (밀리초만 포함)
            )
            handler.setLevel(level)
        else:
            handler = logging.StreamHandler(sys.stdout)
            formatter = MicrosecondFormatter(
                fmt or "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
                datefmt="%H:%M:%S,%f"  # 일관된 시간 포맷 적용 (밀리초 포함)
            )
            handler.setLevel(level)
            handler.setFormatter(formatter)
        root.addHandler(handler)

    # 파일 핸들러(옵션)
    if file_path:
        add_rotating_file_handler(
            file_path,
            level=level,
            fmt="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
            datefmt="%H:%M:%S,%f",  # 일관된 시간 포맷 적용 (밀리초 포함)
            max_file_size=max_file_size,
            backup_count=backup_count,
        )

    _configured = True

def add_rotating_file_handler(
    file_path: str | Path,
    *,
    level: int | str = logging.INFO,
    fmt: str | None = "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    datefmt: str | None = "%H:%M:%S,%f",  # 시간 포맷 매개변수 추가 (밀리초 포함)
    max_file_size: int = 10 * 1024 * 1024,
    backup_count: int = 5,
) -> None:
    """회전 파일 핸들러 추가."""
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    p = Path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    fh = logging.handlers.RotatingFileHandler(
        filename=str(p),
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding="utf-8",
    )
    fh.setLevel(level)
    fh.setFormatter(MicrosecondFormatter(fmt, datefmt=datefmt))
    logging.getLogger().addHandler(fh)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """표준 logging.Logger 반환. name 없으면 호출자 모듈명."""
    if name is None:
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        name = module.__name__ if module else "app"
    return logging.getLogger(name)

def get_console() -> Optional["Console"]:
    """Rich 콘솔 인스턴스(없으면 None)."""
    return _console

def set_level(level: int | str) -> None:
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    logging.getLogger().setLevel(level)

class Log:
    """
    기존 Logger 객체와 동일한 사용감을 주는 프록시.
    - .console 프로퍼티 제공
    - .debug/.info/... 메서드 위임
    """
    def __init__(self, name: Optional[str] = None) -> None:
        self._logger = get_logger(name)

    # --- 기존과 동일한 프로퍼티/메서드 ---
    @property
    def console(self) -> Optional["Console"]:
        return get_console()

    def debug(self, msg: str, *args, **kwargs) -> None:
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        self._logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        self._logger.exception(msg, *args, **kwargs)
