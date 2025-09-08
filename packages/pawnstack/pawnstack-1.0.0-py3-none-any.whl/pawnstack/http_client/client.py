"""
PawnStack HTTP 클라이언트

비동기 HTTP 요청을 위한 클라이언트
"""

import httpx
from dataclasses import dataclass
from typing import Dict, Any, Optional, Union


@dataclass
class HttpResponse:
    """HTTP 응답 데이터 클래스"""
    status_code: int
    headers: Dict[str, str]
    content: bytes
    text: str
    url: str
    
    def json(self) -> Dict[str, Any]:
        """JSON 응답 파싱"""
        import json
        return json.loads(self.text)
    
    def is_success(self) -> bool:
        """성공 응답인지 확인"""
        return 200 <= self.status_code < 300


class HttpClient:
    """비동기 HTTP 클라이언트"""
    
    def __init__(
        self,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        default_headers: Optional[Dict[str, str]] = None
    ):
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.default_headers = default_headers or {}
    
    async def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes, Dict[str, Any]]] = None,
        timeout: Optional[float] = None,
        verify_ssl: Optional[bool] = None,
        **kwargs
    ) -> HttpResponse:
        """HTTP 요청 실행"""
        # 헤더 병합
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)
        
        # 타임아웃 설정
        request_timeout = timeout if timeout is not None else self.timeout
        
        # SSL 검증 설정
        request_verify = verify_ssl if verify_ssl is not None else self.verify_ssl
        
        async with httpx.AsyncClient(
            timeout=request_timeout,
            verify=request_verify,
            headers=request_headers
        ) as client:
            # 요청 파라미터 준비
            request_kwargs = kwargs.copy()
            
            if json is not None:
                request_kwargs['json'] = json
            elif data is not None:
                request_kwargs['data'] = data
            
            response = await client.request(method, url, **request_kwargs)
            
            return HttpResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                content=response.content,
                text=response.text,
                url=str(response.url)
            )
    
    async def get(self, url: str, **kwargs) -> HttpResponse:
        """GET 요청"""
        return await self.request('GET', url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> HttpResponse:
        """POST 요청"""
        return await self.request('POST', url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> HttpResponse:
        """PUT 요청"""
        return await self.request('PUT', url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> HttpResponse:
        """DELETE 요청"""
        return await self.request('DELETE', url, **kwargs)
    
    async def patch(self, url: str, **kwargs) -> HttpResponse:
        """PATCH 요청"""
        return await self.request('PATCH', url, **kwargs)
    
    async def head(self, url: str, **kwargs) -> HttpResponse:
        """HEAD 요청"""
        return await self.request('HEAD', url, **kwargs)
    
    async def options(self, url: str, **kwargs) -> HttpResponse:
        """OPTIONS 요청"""
        return await self.request('OPTIONS', url, **kwargs)