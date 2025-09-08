# pawnstack/mixins.py
from __future__ import annotations
import logging
from pawnstack.log import get_logger, Log

class LoggerMixin:
    """표준 logger와 프록시 둘 다 제공"""
    def __init__(self) -> None:
        name = f"{self.__class__.__module__}.{self.__class__.__name__}"
        self._logger: logging.Logger | None = get_logger(name)
        self._log: Log | None = Log(name)

    @property
    def logger(self) -> logging.Logger:
        return self._logger  # 표준 logging.Logger

    @property
    def log(self) -> Log:
        return self._log     # .console/.info/... 지원
