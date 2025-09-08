"""타입 검증 유틸리티"""

import re
import json
from typing import Any, Union
from urllib.parse import urlparse


def is_json(data: Any) -> bool:
    """JSON 형식인지 확인"""
    if isinstance(data, (dict, list)):
        return True

    if isinstance(data, str):
        try:
            json.loads(data)
            return True
        except (json.JSONDecodeError, ValueError):
            return False

    return False


def is_int(value: Any) -> bool:
    """정수인지 확인"""
    if isinstance(value, int) and not isinstance(value, bool):
        return True

    if isinstance(value, str):
        try:
            # 앞에 0이 있는 경우는 제외 (예: "01", "001")
            if value.startswith('0') and len(value) > 1:
                return False
            int(value)
            return True
        except ValueError:
            return False

    return False


def is_float(value: Any) -> bool:
    """실수인지 확인"""
    if isinstance(value, float):
        return True

    if isinstance(value, str):
        try:
            float(value)
            return '.' in value  # 소수점이 있어야 float로 인정
        except ValueError:
            return False

    return False


def is_number(value: Any) -> bool:
    """숫자인지 확인 (정수 또는 실수)"""
    return is_int(value) or is_float(value)


def is_hex(value: Any) -> bool:
    """16진수 문자열인지 확인"""
    if not isinstance(value, str):
        return False

    # 0x 접두사가 있는 경우
    if value.startswith('0x') or value.startswith('0X'):
        try:
            int(value, 16)
            return True
        except ValueError:
            return False

    return False


def is_valid_ipv4(ip: str) -> bool:
    """유효한 IPv4 주소인지 확인"""
    if not isinstance(ip, str):
        return False

    # 정규식 패턴
    pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

    if not re.match(pattern, ip):
        return False

    # 각 옥텟이 0으로 시작하지 않는지 확인 (예: 01.02.03.04는 유효하지 않음)
    octets = ip.split('.')
    for octet in octets:
        if len(octet) > 1 and octet.startswith('0'):
            return False

    return True


def is_valid_ipv6(ip: str) -> bool:
    """유효한 IPv6 주소인지 확인"""
    if not isinstance(ip, str):
        return False

    # 간단한 IPv6 패턴 (완전하지 않지만 기본적인 검증)
    pattern = r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    return bool(re.match(pattern, ip))


def is_valid_url(url: str) -> bool:
    """유효한 URL인지 확인"""
    if not isinstance(url, str):
        return False

    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def is_valid_email(email: str) -> bool:
    """유효한 이메일 주소인지 확인"""
    if not isinstance(email, str):
        return False

    # 연속된 점이 있는지 확인
    if '..' in email:
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """유효한 전화번호인지 확인 (국제 형식)"""
    if not isinstance(phone, str):
        return False

    # 간단한 국제 전화번호 패턴
    pattern = r'^\+[1-9]\d{10,14}$'
    return bool(re.match(pattern, phone))


def is_valid_postal_code(code: str) -> bool:
    """유효한 우편번호인지 확인 (5자리 숫자)"""
    if not isinstance(code, str):
        return False

    pattern = r'^\d{5}$'
    return bool(re.match(pattern, code))


def is_valid_credit_card(card: str) -> bool:
    """유효한 신용카드 번호인지 확인 (Luhn 알고리즘)"""
    if not isinstance(card, str):
        return False

    # 숫자만 추출
    digits = [int(d) for d in card if d.isdigit()]

    if len(digits) < 13 or len(digits) > 19:
        return False

    # Luhn 알고리즘
    checksum = 0
    reverse_digits = digits[::-1]

    for i, digit in enumerate(reverse_digits):
        if i % 2 == 1:  # 짝수 번째 자리 (오른쪽에서부터)
            digit *= 2
            if digit > 9:
                digit = digit // 10 + digit % 10
        checksum += digit

    return checksum % 10 == 0


def is_valid_html_tag(text: str) -> bool:
    """HTML 태그가 포함되어 있는지 확인"""
    if not isinstance(text, str):
        return False

    pattern = r'<[^>]+>'
    return bool(re.search(pattern, text))


def is_valid_slug(slug: str) -> bool:
    """유효한 슬러그인지 확인 (URL에 사용 가능한 형식)"""
    if not isinstance(slug, str):
        return False

    pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
    return bool(re.match(pattern, slug))


def is_valid_date(date_str: str) -> bool:
    """유효한 날짜 형식인지 확인 (YYYY-MM-DD)"""
    if not isinstance(date_str, str):
        return False

    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return bool(re.match(pattern, date_str))


def is_valid_time(time_str: str) -> bool:
    """유효한 시간 형식인지 확인 (HH:MM:SS)"""
    if not isinstance(time_str, str):
        return False

    pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$'
    return bool(re.match(pattern, time_str))


def guess_type(value: Any) -> str:
    """값의 타입을 추측"""
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "boolean"
    elif isinstance(value, int):
        return "integer"
    elif isinstance(value, float):
        return "float"
    elif isinstance(value, str):
        if is_json(value):
            return "json_string"
        elif is_hex(value):
            return "hex_string"
        elif is_valid_url(value):
            return "url"
        elif is_valid_email(value):
            return "email"
        elif is_valid_ipv4(value):
            return "ipv4"
        elif is_valid_ipv6(value):
            return "ipv6"
        elif is_number(value):
            return "numeric_string"
        else:
            return "string"
    elif isinstance(value, (list, tuple)):
        return "array"
    elif isinstance(value, dict):
        return "object"
    else:
        return "unknown"
