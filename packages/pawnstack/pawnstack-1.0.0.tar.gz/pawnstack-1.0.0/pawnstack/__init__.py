"""
PawnStack: 차세대 Infrastructure as Code (IaC) Python 라이브러리

PawnStack은 현대적인 Python 개발 패러다임을 적용하여 설계된 포괄적인 IaC 도구입니다.
SSH 모니터링, WebSocket 연결, 블록체인 통합, 클라우드 자동화 등을 지원합니다.
"""

from pawnstack.__version__ import __version__
from pawnstack.config.settings import Config
from pawnstack.config.global_config import (
    PawnStackConfig,
    ConfigHandler,
    NestedNamespace,
    pawnstack_config,
    pawn
)

# Lazy import to avoid circular import issues
def _get_pawnstack():
    from pawnstack.core.base import PawnStack
    return PawnStack

# Create a lazy-loaded PawnStack
import sys
class LazyPawnStack:
    def __new__(cls, *args, **kwargs):
        PawnStack = _get_pawnstack()
        return PawnStack(*args, **kwargs)

# Add PawnStack to module
sys.modules[__name__].PawnStack = LazyPawnStack

__all__ = [
    "__version__",
    "PawnStack",
    "Config",
    "PawnStackConfig",
    "ConfigHandler",
    "NestedNamespace",
    "pawnstack_config",
    "pawn"
]
