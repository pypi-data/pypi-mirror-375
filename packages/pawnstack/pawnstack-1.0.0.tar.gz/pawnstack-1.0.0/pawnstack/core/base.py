"""PawnStack 메인 클래스"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Optional

from pawnstack.config.settings import Config
from pawnstack.core.mixins import LoggerMixin
from pawnstack.http_client.client import HttpClient
# ⬇️ 기존 Logger 제거
# from pawnstack.logging.logger import Logger
from pawnstack.log import setup as log_setup, get_logger, get_console  # 새 파사드

if TYPE_CHECKING:
    from pawnstack.system.monitor import SystemMonitor


class PawnStack(LoggerMixin):
    """
    PawnStack 메인 클래스

    모든 PawnStack 기능에 대한 중앙 집중식 접근점을 제공합니다.
    """

    def __init__(self, config: Optional[Config] = None) -> None:
        """
        PawnStack 인스턴스 초기화

        Args:
            config: 설정 객체. None인 경우 기본 설정 사용
        """
        self.config = config or Config()

        # --- 로깅 초기화 (전역 1회, 여러 인스턴스여도 중복 안전) ---
        # Config.logging(= LoggingConfig) 필드 매핑
        lc = self.config.logging
        log_setup(
            level=getattr(lc, "level", "INFO"),
            enable_console=getattr(lc, "enable_console", True),
            enable_rich=getattr(lc, "enable_rich", True),
            fmt=getattr(lc, "format", None),
            file_path=getattr(lc, "file_path", None),
            max_file_size=getattr(lc, "max_file_size", 10 * 1024 * 1024),
            backup_count=getattr(lc, "backup_count", 5),
            # 필요하면 show_path/show_time도 settings에 추가해 매핑 가능
        )

        # LoggerMixin 초기화 (logger 프로퍼티 제공)
        super().__init__()

        # 핵심 컴포넌트
        self._http: Optional[HttpClient] = None
        self._system_monitor: Optional[SystemMonitor] = None

        # 사용: 믹스인이 제공하는 self.logger (표준 logging.Logger)
        self.logger.info(f"PawnStack 초기화 완료 - 버전: {self.config.version}")

        # Rich 콘솔을 쓰고 싶으면 필요 시 가져와서 사용 가능
        # c = get_console()
        # if c:
        #     c.rule("[bold green]PawnStack Started[/]")

    @property
    def http(self) -> HttpClient:
        """HTTP 클라이언트 인스턴스"""
        if self._http is None:
            self._http = HttpClient()
        return self._http

    @property
    def system(self) -> SystemMonitor:
        """시스템 모니터 인스턴스"""
        if self._system_monitor is None:
            from pawnstack.system.monitor import SystemMonitor
            self._system_monitor = SystemMonitor(config=self.config.system)
        return self._system_monitor

    async def __aenter__(self) -> PawnStack:
        """비동기 컨텍스트 매니저 진입"""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """비동기 컨텍스트 매니저 종료"""
        await self.close()

    async def close(self) -> None:
        """리소스 정리"""
        # HTTPClient는 각 요청마다 새로운 클라이언트를 생성하므로 별도 정리 불필요
        self.logger.info("PawnStack 리소스 정리 완료")

    def __repr__(self) -> str:
        return f"PawnStack(config={self.config})"
