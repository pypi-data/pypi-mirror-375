"""
PawnStack 전역 설정 관리 모듈

환경변수 기반 전역 설정과 Rich 콘솔 기능을 제공합니다.
레거시 pawnlib.config.globalconfig에서 마이그레이션된 기능들을 포함합니다.
"""

import os
import sys
import json
import configparser
from pathlib import Path
from typing import Optional, Dict, Any, Union, Callable
from collections import defaultdict, OrderedDict
from types import SimpleNamespace
from uuid import uuid4
import copy

from rich.console import Console as RichConsole
from rich.traceback import install as rich_traceback_install
from rich.table import Table
from rich.panel import Panel
from rich import inspect as rich_inspect
from rich.tree import Tree
from rich import box

from pawnstack import __version__


class NestedNamespace(SimpleNamespace):
    """중첩된 딕셔너리를 네임스페이스로 변환하는 클래스"""
    
    @staticmethod
    def _map_entry(entry):
        """딕셔너리 엔트리를 NestedNamespace 인스턴스로 매핑"""
        if isinstance(entry, dict):
            return NestedNamespace(**entry)
        return entry

    def __init__(self, **kwargs):
        """중첩된 딕셔너리와 리스트를 NestedNamespace 인스턴스로 변환하여 초기화"""
        super().__init__(**kwargs)
        for key, val in kwargs.items():
            if isinstance(val, dict):
                setattr(self, key, NestedNamespace(**val))
            elif isinstance(val, list):
                setattr(self, key, list(map(self._map_entry, val)))

    def keys(self) -> list:
        """현재 네임스페이스의 키 목록 반환"""
        return list(self.__dict__.keys())

    def values(self) -> list:
        """현재 네임스페이스의 값 목록 반환"""
        return list(self.__dict__.values())

    def as_dict(self) -> dict:
        """NestedNamespace를 딕셔너리로 변환 (재귀적)"""
        return self._namespace_to_dict(self.__dict__)

    def _namespace_to_dict(self, _dict):
        """NestedNamespace를 딕셔너리로 재귀적 변환하는 헬퍼 메서드"""
        result = {}
        for key, value in _dict.items():
            if isinstance(value, (dict, NestedNamespace)):
                result[key] = self._namespace_to_dict(value._asdict())
            else:
                result[key] = value
        return result

    def _asdict(self) -> dict:
        """내부 딕셔너리 표현 반환"""
        return self.__dict__

    def get_nested(self, keys: list):
        """키 리스트를 사용하여 중첩된 값 검색"""
        result = self
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key, None)
            else:
                result = getattr(result, key, None)
            if result is None:
                return None
        return result

    def __repr__(self, indent=4):
        result = self.__class__.__name__ + '('
        items_len = len(self.__dict__)
        _first = 0
        _indent_space = ''

        for k, v in self.__dict__.items():
            if _first == 0 and items_len > 0:
                result += "\n"
                _first = 1
            if k.startswith('__'):
                continue
            if isinstance(v, NestedNamespace):
                value_str = v.__repr__(indent + 4)
            else:
                value_str = str(v)

            if k and value_str:
                if _first:
                    _indent_space = ' ' * indent
                result += _indent_space + k + '=' + value_str + ",\n"
        result += ' ' * (len(_indent_space) - 4) + f')'
        return result


class ConfigHandler:
    """설정 파일, 환경변수, 명령줄 인수를 통합 관리하는 클래스"""
    
    def __init__(
        self, 
        config_file: str = 'config.ini',
        args: Optional[Any] = None,
        allowed_env_keys: Optional[list] = None,
        env_prefix: Optional[str] = None,
        section_pattern: Optional[str] = None,
        defaults: Optional[dict] = None
    ):
        """
        ConfigHandler 초기화
        
        Args:
            config_file: 설정 파일 경로
            args: 파싱된 명령줄 인수
            allowed_env_keys: 허용된 환경변수 키 목록
            env_prefix: 환경변수 접두사
            section_pattern: 섹션 이름 검색용 정규식
            defaults: 기본값 딕셔너리
        """
        self.config = configparser.ConfigParser()
        self.config_file = config_file
        self.config.read(config_file)
        self.args = {k.lower(): v for k, v in vars(args).items()} if args else {}
        self.allowed_env_keys = [k.lower() for k in allowed_env_keys] if allowed_env_keys else []
        self.env_prefix = env_prefix.lower() if env_prefix else None
        self.section_pattern = section_pattern
        self.defaults = defaults or {}

        if self.config.has_section('default'):
            self.config_keys = set(k.lower() for k in self.config['default'])
        else:
            self.config_keys = set()

        self.args_keys = set(self.args.keys())
        self.combined_keys = self.args_keys.union(self.config_keys)
        self.env = self._filter_env(os.environ)
        self.original_keys = {}
        self._populate_original_keys()

        # 소스 히스토리 초기화
        self.source_history = defaultdict(list)
        self._initialize_source_history()

    def _populate_original_keys(self):
        """원본 키 이름 저장 (우선순위: args > env > config.ini)"""
        # Args에서 원본 키
        for key in self.args:
            if key not in self.original_keys:
                self.original_keys[key] = key

        # 환경변수에서 원본 키
        for key in self.env:
            if key not in self.original_keys:
                original_key = next((k for k in os.environ if k.lower() == key), key)
                self.original_keys[key] = original_key

        # config.ini에서 원본 키
        if self.config.has_section('default'):
            for key in self.config['default']:
                key_lower = key.lower()
                if key_lower not in self.original_keys:
                    self.original_keys[key_lower] = key

    def _initialize_source_history(self):
        """각 키의 소스 히스토리 초기화"""
        for key_lower in self.combined_keys:
            if key_lower in self.args and self.args[key_lower] is not None:
                self.source_history[key_lower].append('args')
            elif key_lower in self.env:
                self.source_history[key_lower].append('env')
            elif self.config.has_option('default', key_lower):
                self.source_history[key_lower].append('config.ini')
            else:
                if key_lower in self.defaults:
                    self.source_history[key_lower].append('default')
                else:
                    self.source_history[key_lower].append('undefined')

    def _filter_env(self, env: dict) -> dict:
        """허용된 키나 접두사로 환경변수 필터링"""
        filtered_env = {}

        for k, v in env.items():
            key_lower = k.lower()

            # args나 config.ini의 키와 일치하는지 확인
            if key_lower in self.combined_keys:
                filtered_env[key_lower] = v
                continue

            # allowed_env_keys에 있는지 확인
            if self.allowed_env_keys and key_lower in self.allowed_env_keys:
                filtered_env[key_lower] = v
                continue

            # env_prefix로 시작하는지 확인
            if self.env_prefix and key_lower.startswith(self.env_prefix):
                stripped_key = key_lower[len(self.env_prefix):]
                if stripped_key:
                    filtered_env[stripped_key] = v
                continue

        return filtered_env

    @staticmethod
    def _convert_value(value):
        """값을 적절한 타입으로 변환"""
        if isinstance(value, bool) or value is None:
            return value
        if isinstance(value, str):
            value_lower = value.lower()
            if value_lower in ('true', 'yes', 'on'):
                return True
            if value_lower in ('false', 'no', 'off'):
                return False
            try:
                if '.' in value:
                    return float(value)
                return int(value)
            except ValueError:
                return value
        return value

    def get(self, key: str, default=None):
        """
        우선순위에 따라 값 반환:
        1. 명령줄 인수 (args)
        2. 환경변수 (env)
        3. 설정 파일 (config.ini)
        4. 기본값
        """
        key_lower = key.lower()
        if key_lower in self.args and self.args[key_lower] is not None:
            return self.args[key_lower]
        if key_lower in self.env:
            return self._convert_value(self.env.get(key_lower))
        if self.config.has_option('default', key_lower):
            return self._convert_value(self.config.get('default', key_lower))
        if key_lower in self.defaults:
            return self.defaults[key_lower]
        return self._convert_value(default)

    def as_dict(self) -> dict:
        """최종 병합된 설정을 딕셔너리로 반환"""
        merged = {}
        
        # config.ini 값 추가
        if self.config.has_section('default'):
            for key, value in self.config.items('default'):
                key_lower = key.lower()
                merged[key_lower] = self._convert_value(value)

        # 환경변수로 덮어쓰기
        for key, value in self.env.items():
            merged[key] = self._convert_value(value)

        # args로 덮어쓰기
        for key, value in self.args.items():
            if value is not None:
                merged[key] = value

        # 기본값 추가 (설정되지 않은 경우만)
        for key, value in self.defaults.items():
            key_lower = key.lower()
            if key_lower not in merged:
                merged[key_lower] = self._convert_value(value)

        return merged

    def as_namespace(self) -> NestedNamespace:
        """최종 병합된 설정을 NestedNamespace로 반환"""
        return NestedNamespace(**self.as_dict())

    def get_source(self, key: str) -> str:
        """값의 최신 소스 반환"""
        key_lower = key.lower()
        if key_lower in self.args and self.args[key_lower] is not None:
            return 'args'
        if key_lower in self.env:
            return 'env'
        if self.config.has_option('default', key_lower):
            return 'config.ini'
        if key_lower in self.defaults:
            return 'default'
        return 'undefined'

    def update(self, updates: dict):
        """여러 설정값 업데이트"""
        for key, value in updates.items():
            key_lower = key.lower()
            self.args[key_lower] = value
            self.original_keys[key_lower] = key

            if len(self.source_history[key_lower]) == 0:
                self.source_history[key_lower].append('args (added)')
            else:
                self.source_history[key_lower].append('args (updated)')

    def set(self, key: str, value):
        """단일 설정값 업데이트"""
        self.update({key: value})

    def print_config(self, console: Optional[RichConsole] = None):
        """설정 개요를 테이블로 출력"""
        if console is None:
            console = RichConsole()
            
        table = Table(title="Configuration Overview")
        table.add_column("Key", justify="left", style="bold")
        table.add_column("Value", justify="left")
        table.add_column("Source", justify="left")

        # 소스별 색상 매핑
        source_colors = {
            'args': 'green',
            'args (updated)': 'bright_green',
            'env': 'blue',
            'env (updated)': 'bright_blue',
            self.config_file: 'yellow',
            f'{self.config_file} (updated)': 'bright_yellow',
            'default': 'white',
            'args (added)': 'bright_green',
            'env (added)': 'bright_blue',
            f'{self.config_file} (added)': 'bright_yellow',
            'undefined': 'dim',
        }

        # 고유 키 수집
        keys = set()
        if self.config.has_section('default'):
            keys.update([k.lower() for k in self.config['default']])
        keys.update(self.env.keys())
        keys.update(self.args.keys())
        keys.update([k.lower() for k in self.defaults.keys()])

        for key_lower in sorted(keys):
            original_key = self.original_keys.get(key_lower, key_lower)
            value = self.get(key_lower)
            
            latest_source = self.source_history[key_lower][-1] if self.source_history[key_lower] else 'undefined'
            color = source_colors.get(latest_source, 'white')
            
            source_display = " -> ".join(self.source_history[key_lower])
            
            table.add_row(
                original_key,
                str(value),
                source_display,
                style=color
            )

        console.print(table)


class Singleton(type):
    """싱글톤 메타클래스"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls in cls._instances:
            return cls._instances[cls]
        instance = super(Singleton, cls).__call__(*args, **kwargs)
        cls._instances[cls] = instance
        return instance


class PawnStackConfig(metaclass=Singleton):
    """PawnStack 전역 설정 관리 클래스"""
    
    def __init__(
        self,
        global_name: str = "pawnstack_global_config",
        debug: bool = False,
        timeout: int = 6000,
        env_prefix: str = "PAWN"
    ):
        """
        PawnStackConfig 초기화
        
        Args:
            global_name: 전역 변수 이름
            debug: 디버그 모드
            timeout: 전역 타임아웃
            env_prefix: 환경변수 접두사
        """
        self.global_name = f"{global_name}_{uuid4()}"
        self.debug = debug
        self.timeout = timeout
        self.verbose = 0
        self.env_prefix = env_prefix
        self.version = f"PawnStack/{__version__}"
        self.version_number = __version__
        self.app_name = ""
        
        self._config = {}
        self._environments = {}
        self._current_path: Optional[Path] = None
        self._config_file = None
        self._loaded = {
            "console": False,
            "on_ready": False,
            "rich_traceback_installed": False
        }
        
        # Rich Console 초기화
        self.console = None
        self.console_options = None
        self.log_time_format = None
        self.stdout_log_formatter = None
        self._init_console()
        
        # 데이터 네임스페이스
        self.data = NestedNamespace()

    def _log_formatter(self, dt):
        """시간 포맷터 (레거시 호환)"""
        if self.log_time_format and self.log_time_format.endswith('.%f'):
            return dt.strftime(self.log_time_format)[:-3]
        elif self.log_time_format:
            return dt.strftime(self.log_time_format)
        else:
            # 일관된 시간 포맷 사용 (밀리초 포함)
            return f"[{dt.strftime('%H:%M:%S,%f')[:-3]}]"

    def _init_console(self, force_init: bool = True):
        """Rich Console 초기화 (레거시 호환)"""
        is_interactive = hasattr(sys, 'ps1') or sys.stdin.isatty()
        
        console_options = {
            'record': True,
            'soft_wrap': False,
            'force_terminal': True,
            'log_time_format': lambda dt: f"[{dt.strftime('%H:%M:%S,%f')[:-3]}]"  # 일관된 시간 포맷 사용 (밀리초 포함)
        }
        
        if not self._loaded.get('console'):
            console_options['redirect'] = False
            
        if self._loaded.get('console') or force_init:
            if self.console_options:
                # 시간 포맷 처리 (레거시 호환)
                if self.console_options.get('log_time_format') and not isinstance(self.console_options.get('log_time_format'), Callable):
                    _log_time_format = self.console_options['log_time_format']
                    self.log_time_format = self.console_options['log_time_format']
                    
                    if ".%f" in _log_time_format:
                        self.console_options['log_time_format'] = lambda dt: f"[{dt.strftime(_log_time_format)[:-3]}]"
                    else:
                        self.console_options['log_time_format'] = lambda dt: f"[{dt.strftime(_log_time_format)}]"
                    self.stdout_log_formatter = self.console_options['log_time_format']
                
                console_options.update(self.console_options)
            
            # Rich Console에서 지원하지 않는 옵션 제거
            if 'redirect' in console_options:
                del console_options['redirect']
                
            self.console = RichConsole(**console_options)

    @staticmethod
    def str2bool(v) -> bool:
        """문자열을 불린값으로 변환"""
        true_list = ("yes", "true", "t", "1", "True", "TRUE")
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in true_list
        return bool(v)

    def fill_config_from_environment(self):
        """환경변수에서 설정 초기화"""
        default_structure = {
            "DEBUG": {
                "type": self.str2bool,
                "default": False,
            },
            "TIMEOUT": {
                "type": int,
                "default": 6000,
            },
            "CONFIG_FILE": {
                "type": str,
                "default": "config.ini",
            },
            "PATH": {
                "type": str,
                "default": str(Path(os.getcwd()))
            },
            "TIME_FORMAT": {
                "type": str,
                "default": "%H:%M:%S.%f"
            },
            "VERBOSE": {
                "type": int,
                "default": 0,
            },
            "SSL_CHECK": {
                "type": self.str2bool,
                "default": True
            }
        }

        for environment in default_structure.keys():
            environment_name = f"{self.env_prefix}_{environment}"
            environment_value = os.getenv(environment_name)
            
            if default_structure.get(environment):
                required_type = default_structure[environment].get("type")
                if environment_value in [None, 0, ""]:
                    filled_value = default_structure[environment].get("default")
                elif required_type:
                    filled_value = required_type(environment_value)
                else:
                    filled_value = environment_value
            else:
                filled_value = environment_value
                
            self._environments[environment_name] = {
                "input": environment_value,
                "value": filled_value,
            }
            self.set(**{environment_name: filled_value})

    def init_with_env(self, **kwargs):
        """환경변수로 초기화"""
        self.fill_config_from_environment()
        self.set(**kwargs)
        self._config_file = self.get('PAWN_CONFIG_FILE', 'config.ini')
        self._loaded['on_ready'] = True
        
        if self.console:
            python_version = f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            pawnstack_path = os.path.dirname(os.path.dirname(__file__))  # pawnstack 패키지 경로
            self.console.log(f"🐍 {python_version}, ♙ {self.version}, PATH={pawnstack_path}")
        
        return self

    def get(self, key: str = None, default=None):
        """키 값 반환"""
        if key is None:
            return self._config
        return self._config.get(key, default)

    def set(self, **kwargs):
        """키 값 설정 (레거시 호환)"""
        priority_keys = [f"{self.env_prefix}_PATH", f"{self.env_prefix}_TIME_FORMAT", f"{self.env_prefix}_DEBUG", f"{self.env_prefix}_VERBOSE"]
        order_dict = OrderedDict(kwargs)

        def _enforce_set_value(source_key=None, target_key=None, target_dict=None):
            """값 강제 설정 헬퍼 함수"""
            if kwargs.get(source_key):
                if isinstance(target_dict, dict) and not target_dict.get(target_key):
                    target_dict[target_key] = kwargs[source_key]
                    if hasattr(self, 'verbose') and isinstance(self.verbose, int) and self.verbose >= 3:
                        if self.console:
                            self.console.log(f'set => {target_key}={kwargs[source_key]}')

        for priority_key in priority_keys:
            if order_dict.get(priority_key):
                order_dict.move_to_end(key=priority_key, last=False)

        for key, value in order_dict.items():
            # 환경변수 우선순위 처리
            if self._environments.get(key) and self._environments[key].get("input"):
                if self._environments[key].get('value') != value:
                    if self.console:
                        self.console.log(f"[yellow][WARN] Environment variable overrides config: "
                                       f"'{key}': {self._environments[key]['value']}(ENV) != {value}(Config)")
                    value = self._environments[key]['value']

            # 특별한 키 처리 (레거시 호환)
            if key == f"{self.env_prefix}_LOGGER" and value:
                if isinstance(value, dict):
                    # 로거 설정 처리 (향후 구현)
                    if value.get('app_name') is None and kwargs.get('app_name'):
                        value['app_name'] = kwargs['app_name']
                        self.app_name = kwargs['app_name']
                    _enforce_set_value(source_key=f'{self.env_prefix}_TIME_FORMAT', target_key='stdout_log_formatter', target_dict=value)
                    # self.app_logger, self.error_logger = AppLogger(**value).get_logger()
            elif key == f"{self.env_prefix}_DEBUG":
                self.debug = self.str2bool(value)
                if self.console:
                    self.console.pawn_debug = self.str2bool(value) if hasattr(self.console, 'pawn_debug') else None
                if self.debug and not self._loaded.get('rich_traceback_installed'):
                    rich_traceback_install(show_locals=True, width=160)
                    self._loaded['rich_traceback_installed'] = True
            elif key == f"{self.env_prefix}_CONSOLE":
                _enforce_set_value(source_key=f'{self.env_prefix}_TIME_FORMAT', target_key='log_time_format', target_dict=value)
                self.console_options = value
                self._init_console()
                self._loaded['console'] = True
            elif key == f"{self.env_prefix}_TIMEOUT":
                self.timeout = value
            elif key == f"{self.env_prefix}_VERBOSE":
                self.verbose = value
            elif key == f"{self.env_prefix}_PATH":
                self._current_path = Path(value)
            elif key == f"{self.env_prefix}_CONFIG_FILE":
                self._config_file = value
            elif key == "data" and isinstance(value, dict):
                self.data = NestedNamespace(**value)
                value = self.data

            self._config[key] = value

    def increase(self, **kwargs) -> int:
        """키 값 증가"""
        return self._modify_value("increase", **kwargs)

    def decrease(self, **kwargs) -> int:
        """키 값 감소"""
        return self._modify_value("decrease", **kwargs)

    def append_list(self, **kwargs) -> list:
        """리스트에 값 추가"""
        return self._modify_value("append_list", **kwargs)

    def remove_list(self, **kwargs) -> list:
        """리스트에서 값 제거"""
        return self._modify_value("remove_list", **kwargs)

    def _modify_value(self, command: str, **kwargs):
        """값 수정 헬퍼 메서드"""
        init_values = {
            "increase": 0,
            "decrease": 0,
            "append_list": [],
            "remove_list": [],
        }
        
        for key, value in kwargs.items():
            current = self.get(key, init_values.get(command))
            
            if command == "increase" and isinstance(current, (int, float)):
                current += value
            elif command == "decrease" and isinstance(current, (int, float)):
                current -= value
            elif command == "append_list" and isinstance(current, list):
                current.append(value)
            elif command == "remove_list" and isinstance(current, list):
                if value in current:
                    current.remove(value)
            
            self._config[key] = current
            return current
        
        return init_values.get(command)

    def conf(self) -> NestedNamespace:
        """전역 설정을 NestedNamespace로 반환"""
        return NestedNamespace(**self._config)

    def to_dict(self) -> dict:
        """전역 설정을 딕셔너리로 반환"""
        return self._config.copy()

    @staticmethod
    def inspect(*args, **kwargs):
        """Rich inspect 함수"""
        return rich_inspect(*args, **kwargs)

    def __str__(self):
        return f"<{self.version}>[{self.global_name}]\n{self.to_dict()}"


# 전역 인스턴스 생성
def create_pawnstack_config() -> PawnStackConfig:
    """PawnStackConfig 인스턴스 생성"""
    return PawnStackConfig().init_with_env()


# 전역 설정 인스턴스 (레거시 호환)
def create_pawn(use_global_namespace: bool = False) -> PawnStackConfig:
    """PawnStackConfig 인스턴스 생성 (레거시 호환)"""
    return PawnStackConfig().init_with_env()

pawnstack_config: PawnStackConfig = create_pawnstack_config()
pawn = pawnstack_config  # 단축 별칭

# 레거시 호환 별칭들
from functools import partial
pconf = partial(pawn.conf)
global_verbose = pawn.get('PAWN_VERBOSE', 0)