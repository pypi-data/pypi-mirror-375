"""시스템 모니터링"""

from __future__ import annotations

import asyncio
import time
from typing import Dict, List, Optional

import psutil
from pydantic import BaseModel

from pawnstack.config.settings import SystemConfig
from pawnstack.core.mixins import LoggerMixin


class SystemInfo(BaseModel):
    """시스템 정보 모델"""
    
    timestamp: float
    cpu_percent: float
    memory_total: int
    memory_used: int
    memory_percent: float
    disk_total: int
    disk_used: int
    disk_percent: float
    network_sent: int
    network_recv: int
    process_count: int
    load_average: Optional[List[float]] = None


class SystemMonitor(LoggerMixin):
    """시스템 리소스 모니터"""
    
    def __init__(self, config: SystemConfig) -> None:
        """
        시스템 모니터 초기화
        
        Args:
            config: 시스템 모니터링 설정
        """
        super().__init__()
        self.config = config
        self._monitoring = False
        self._history: List[SystemInfo] = []
    
    def get_current_info(self) -> SystemInfo:
        """현재 시스템 정보 수집"""
        
        # CPU 정보
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # 메모리 정보
        memory = psutil.virtual_memory()
        
        # 디스크 정보
        disk = psutil.disk_usage('/')
        
        # 네트워크 정보
        try:
            network = psutil.net_io_counters()
            network_sent = network.bytes_sent
            network_recv = network.bytes_recv
        except Exception:
            network_sent = network_recv = 0
        
        # 프로세스 수
        process_count = len(psutil.pids())
        
        # 로드 평균 (Unix 계열에서만 사용 가능)
        load_average = None
        try:
            load_average = list(psutil.getloadavg())
        except AttributeError:
            # Windows에서는 지원하지 않음
            pass
        
        return SystemInfo(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_total=memory.total,
            memory_used=memory.used,
            memory_percent=memory.percent,
            disk_total=disk.total,
            disk_used=disk.used,
            disk_percent=(disk.used / disk.total) * 100,
            network_sent=network_sent,
            network_recv=network_recv,
            process_count=process_count,
            load_average=load_average,
        )
    
    def check_thresholds(self, info: SystemInfo) -> Dict[str, bool]:
        """임계값 체크"""
        
        alerts = {}
        
        # CPU 임계값 체크
        if info.cpu_percent > self.config.cpu_threshold:
            alerts['cpu'] = True
            self.logger.warning(f"CPU 사용률 임계값 초과: {info.cpu_percent:.1f}%")
        
        # 메모리 임계값 체크
        if info.memory_percent > self.config.memory_threshold:
            alerts['memory'] = True
            self.logger.warning(f"메모리 사용률 임계값 초과: {info.memory_percent:.1f}%")
        
        # 디스크 임계값 체크
        if info.disk_percent > self.config.disk_threshold:
            alerts['disk'] = True
            self.logger.warning(f"디스크 사용률 임계값 초과: {info.disk_percent:.1f}%")
        
        return alerts
    
    async def start_monitoring(
        self,
        duration: Optional[float] = None,
        callback: Optional[callable] = None,
    ) -> None:
        """
        모니터링 시작
        
        Args:
            duration: 모니터링 지속 시간 (초). None이면 무제한
            callback: 각 수집 시점에서 호출할 콜백 함수
        """
        
        self._monitoring = True
        start_time = time.time()
        
        self.logger.info("시스템 모니터링 시작")
        
        try:
            while self._monitoring:
                # 시스템 정보 수집
                info = self.get_current_info()
                
                # 히스토리에 추가
                self._history.append(info)
                
                # 히스토리 크기 제한 (최근 1000개만 유지)
                if len(self._history) > 1000:
                    self._history = self._history[-1000:]
                
                # 임계값 체크
                self.check_thresholds(info)
                
                # 콜백 호출
                if callback:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(info)
                        else:
                            callback(info)
                    except Exception as e:
                        self.logger.error(f"콜백 함수 실행 중 오류: {e}")
                
                # 지속 시간 체크
                if duration and (time.time() - start_time) >= duration:
                    break
                
                # 다음 수집까지 대기
                await asyncio.sleep(self.config.monitor_interval)
                
        except Exception as e:
            self.logger.error(f"모니터링 중 오류 발생: {e}")
        finally:
            self._monitoring = False
            self.logger.info("시스템 모니터링 종료")
    
    def stop_monitoring(self) -> None:
        """모니터링 중지"""
        self._monitoring = False
        self.logger.info("모니터링 중지 요청됨")
    
    def get_history(self, limit: Optional[int] = None) -> List[SystemInfo]:
        """모니터링 히스토리 조회"""
        if limit:
            return self._history[-limit:]
        return self._history.copy()
    
    def get_average_stats(self, minutes: int = 5) -> Optional[Dict[str, float]]:
        """지정된 시간 동안의 평균 통계"""
        
        if not self._history:
            return None
        
        # 지정된 시간 이후의 데이터만 필터링
        cutoff_time = time.time() - (minutes * 60)
        recent_data = [
            info for info in self._history 
            if info.timestamp >= cutoff_time
        ]
        
        if not recent_data:
            return None
        
        # 평균 계산
        avg_cpu = sum(info.cpu_percent for info in recent_data) / len(recent_data)
        avg_memory = sum(info.memory_percent for info in recent_data) / len(recent_data)
        avg_disk = sum(info.disk_percent for info in recent_data) / len(recent_data)
        
        return {
            'cpu_percent': avg_cpu,
            'memory_percent': avg_memory,
            'disk_percent': avg_disk,
            'sample_count': len(recent_data),
        }
    
    def get_top_processes(self, limit: int = 10, sort_by: str = 'cpu') -> List[Dict]:
        """상위 프로세스 목록 조회"""
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # 정렬
        if sort_by == 'cpu':
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        elif sort_by == 'memory':
            processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
        
        return processes[:limit]