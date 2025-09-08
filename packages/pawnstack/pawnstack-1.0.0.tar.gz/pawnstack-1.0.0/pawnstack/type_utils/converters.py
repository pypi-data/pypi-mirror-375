"""
타입 변환 유틸리티
"""

from typing import Any, Dict, List, Optional, Union


def dict_to_line(data: Dict[str, Any], separator: str = "=", end_separator: str = ", ") -> str:
    """딕셔너리를 한 줄 문자열로 변환"""
    if not isinstance(data, dict):
        return str(data)
    
    items = []
    for key, value in data.items():
        items.append(f"{key}{separator}{value}")
    
    return end_separator.join(items)


def flatten_dict(data: Dict[str, Any], parent_key: str = "", separator: str = ".") -> Dict[str, Any]:
    """중첩된 딕셔너리를 평탄화"""
    items = []
    
    for key, value in data.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, separator).items())
        else:
            items.append((new_key, value))
    
    return dict(items)


def unflatten_dict(data: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
    """평탄화된 딕셔너리를 중첩 구조로 복원"""
    result = {}
    
    for key, value in data.items():
        keys = key.split(separator)
        current = result
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    return result


def list_to_dict(data: List[Any], key_func: callable = None) -> Dict[str, Any]:
    """리스트를 딕셔너리로 변환"""
    if key_func is None:
        # 인덱스를 키로 사용
        return {str(i): item for i, item in enumerate(data)}
    
    return {key_func(item): item for item in data}


def dict_to_list(data: Dict[str, Any], include_keys: bool = False) -> List[Any]:
    """딕셔너리를 리스트로 변환"""
    if include_keys:
        return [{"key": k, "value": v} for k, v in data.items()]
    
    return list(data.values())


def safe_convert(value: Any, target_type: type, default: Any = None) -> Any:
    """안전한 타입 변환"""
    try:
        if target_type == bool:
            if isinstance(value, str):
                return value.lower() in ('true', 'yes', '1', 'on')
            return bool(value)
        
        return target_type(value)
    
    except (ValueError, TypeError):
        return default


def normalize_keys(data: Dict[str, Any], case: str = "lower") -> Dict[str, Any]:
    """딕셔너리 키 정규화"""
    if case == "lower":
        return {k.lower(): v for k, v in data.items()}
    elif case == "upper":
        return {k.upper(): v for k, v in data.items()}
    elif case == "title":
        return {k.title(): v for k, v in data.items()}
    
    return data


def merge_dicts(*dicts: Dict[str, Any], deep: bool = False) -> Dict[str, Any]:
    """여러 딕셔너리 병합"""
    result = {}
    
    for d in dicts:
        if not isinstance(d, dict):
            continue
        
        if deep:
            for key, value in d.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dicts(result[key], value, deep=True)
                else:
                    result[key] = value
        else:
            result.update(d)
    
    return result


def filter_dict(data: Dict[str, Any], keys: List[str] = None, exclude_keys: List[str] = None) -> Dict[str, Any]:
    """딕셔너리 필터링"""
    if keys is not None:
        return {k: v for k, v in data.items() if k in keys}
    
    if exclude_keys is not None:
        return {k: v for k, v in data.items() if k not in exclude_keys}
    
    return data.copy()


def convert_size_units(size: Union[int, float], from_unit: str = "B", to_unit: str = "MB") -> float:
    """크기 단위 변환"""
    units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3,
        "TB": 1024**4,
        "PB": 1024**5
    }
    
    from_multiplier = units.get(from_unit.upper(), 1)
    to_multiplier = units.get(to_unit.upper(), 1)
    
    bytes_value = size * from_multiplier
    return bytes_value / to_multiplier


def format_duration(seconds: Union[int, float]) -> str:
    """초를 사람이 읽기 쉬운 형태로 변환"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.1f}m"
    
    hours = minutes / 60
    if hours < 24:
        return f"{hours:.1f}h"
    
    days = hours / 24
    return f"{days:.1f}d"


def parse_duration(duration_str: str) -> Optional[float]:
    """문자열 형태의 기간을 초로 변환"""
    import re
    
    pattern = r'(\d+(?:\.\d+)?)\s*([smhd]?)'
    match = re.match(pattern, duration_str.lower().strip())
    
    if not match:
        return None
    
    value, unit = match.groups()
    value = float(value)
    
    multipliers = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
        '': 1  # 기본값은 초
    }
    
    return value * multipliers.get(unit, 1)