"""타이핑 상수 모듈"""


class Constants:
    """상수 클래스"""

    DEFAULT_ENCODING = "utf-8"
    DEFAULT_TIMEOUT = 30
    DEFAULT_RETRIES = 3
    MAX_RETRIES = 10
    MIN_RETRIES = 0
    DEFAULT_CHUNK_SIZE = 8192
    DEFAULT_BUFFER_SIZE = 1024
    DEFAULT_PAGE_SIZE = 100
    MAX_PAGE_SIZE = 1000
    MIN_PAGE_SIZE = 1
    DEFAULT_DELAY = 1.0
    MAX_DELAY = 60.0
    MIN_DELAY = 0.1

    @staticmethod
    def get_http_methods(lowercase=False):
        """HTTP 메서드 목록을 반환합니다."""
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        if lowercase:
            return [method.lower() for method in methods]
        return methods


# 전역 상수 인스턴스
const = Constants()
