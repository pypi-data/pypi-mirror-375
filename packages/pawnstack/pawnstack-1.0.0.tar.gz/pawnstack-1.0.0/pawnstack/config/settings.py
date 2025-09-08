"""설정 관리"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from pawnstack.__version__ import __version__


class LoggingConfig:
    """로깅 설정"""

    def __init__(self):
        self.level = "INFO"
        self.format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.file_path = None
        self.max_file_size = 10 * 1024 * 1024
        self.backup_count = 5
        self.enable_console = True
        self.enable_rich = True


class HttpConfig:
    """HTTP 클라이언트 설정"""

    def __init__(self):
        self.timeout = 30.0
        self.max_retries = 3
        self.retry_delay = 1.0
        self.user_agent = f"PawnStack/{__version__}"
        self.verify_ssl = True
        self.follow_redirects = True


class SystemConfig:
    """시스템 모니터링 설정"""

    def __init__(self):
        self.monitor_interval = 1.0
        self.cpu_threshold = 80.0
        self.memory_threshold = 80.0
        self.disk_threshold = 90.0


class Config:
    """PawnStack 메인 설정"""

    def __init__(self, **kwargs):
        # 기본 설정
        self.app_name = kwargs.get("app_name", "pawnstack")
        self.version = kwargs.get("version", __version__)
        self.debug = kwargs.get("debug", False)

        # 작업 디렉토리
        self.work_dir = Path.cwd()

        # 하위 설정
        self.logging = LoggingConfig()
        self.http = HttpConfig()
        self.system = SystemConfig()

        # 추가 설정 (동적)
        self.extra_config = {}

        # kwargs로 전달된 설정 적용
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.extra_config[key] = value

    @classmethod
    def from_file(cls, config_path):
        """파일에서 설정 로드"""
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")

        if config_path.suffix.lower() in [".yaml", ".yml"]:
            import yaml
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        elif config_path.suffix.lower() == ".json":
            import json
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            raise ValueError(f"지원하지 않는 설정 파일 형식: {config_path.suffix}")

        return cls(**data)

    def to_dict(self):
        """설정을 딕셔너리로 변환"""
        return {
            "app_name": self.app_name,
            "version": self.version,
            "debug": self.debug,
            "work_dir": str(self.work_dir),
            "extra_config": self.extra_config,
        }

    def update(self, **kwargs):
        """설정 업데이트"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.extra_config[key] = value

    def get(self, key, default=None):
        """설정 값 조회"""
        if hasattr(self, key):
            return getattr(self, key)
        return self.extra_config.get(key, default)
