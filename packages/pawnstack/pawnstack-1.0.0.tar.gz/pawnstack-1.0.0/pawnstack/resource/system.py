"""
시스템 리소스 모니터링 유틸리티
"""

import os
import platform
import socket
import resource
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


def get_hostname() -> str:
    """호스트명 반환"""
    return socket.gethostname()


def get_platform_info() -> Dict[str, str]:
    """플랫폼 정보 반환"""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
    }


def get_mem_info() -> Dict[str, Any]:
    """메모리 정보 반환"""
    memory = psutil.virtual_memory()
    
    return {
        "mem_total": round(memory.total / (1024**3), 2),  # GB
        "mem_available": round(memory.available / (1024**3), 2),  # GB
        "mem_used": round(memory.used / (1024**3), 2),  # GB
        "mem_percent": memory.percent,
        "mem_free": round(memory.free / (1024**3), 2),  # GB
    }


def get_rlimit_nofile(detail: bool = False) -> Dict[str, Any]:
    """파일 디스크립터 제한 정보 반환"""
    try:
        soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
        
        result = {
            "soft_limit": soft_limit,
            "hard_limit": hard_limit,
        }
        
        if detail:
            result.update({
                "current_usage": len(psutil.Process().open_files()),
                "available": soft_limit - len(psutil.Process().open_files()) if soft_limit != resource.RLIM_INFINITY else "unlimited"
            })
        
        return result
        
    except Exception as e:
        return {"error": str(e)}


def get_uptime() -> str:
    """시스템 업타임 반환"""
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"
            
    except Exception as e:
        return f"Error: {e}"


def get_swap_usage() -> str:
    """스왑 사용량 반환"""
    try:
        swap = psutil.swap_memory()
        
        if swap.total == 0:
            return "No swap configured"
        
        used_gb = swap.used / (1024**3)
        total_gb = swap.total / (1024**3)
        percent = swap.percent
        
        return f"{used_gb:.2f}GB / {total_gb:.2f}GB ({percent:.1f}%)"
        
    except Exception as e:
        return f"Error: {e}"


def get_load_average() -> str:
    """CPU 로드 평균 반환"""
    try:
        if hasattr(os, 'getloadavg'):
            load1, load5, load15 = os.getloadavg()
            return f"{load1:.2f}, {load5:.2f}, {load15:.2f}"
        else:
            # Windows의 경우 CPU 사용률로 대체
            cpu_percent = psutil.cpu_percent(interval=1)
            return f"CPU: {cpu_percent}%"
            
    except Exception as e:
        return f"Error: {e}"


def get_cpu_info() -> Dict[str, Any]:
    """CPU 정보 반환"""
    try:
        return {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
        }
    except Exception as e:
        return {"error": str(e)}


def get_process_count() -> int:
    """실행 중인 프로세스 수 반환"""
    try:
        return len(psutil.pids())
    except Exception as e:
        return 0


def get_system_temperature() -> Optional[Dict[str, float]]:
    """시스템 온도 정보 반환 (지원되는 경우)"""
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            result = {}
            for name, entries in temps.items():
                for entry in entries:
                    result[f"{name}_{entry.label or 'temp'}"] = entry.current
            return result
    except Exception:
        pass
    return None


def get_battery_info() -> Optional[Dict[str, Any]]:
    """배터리 정보 반환 (노트북의 경우)"""
    try:
        battery = psutil.sensors_battery()
        if battery:
            return {
                "percent": battery.percent,
                "power_plugged": battery.power_plugged,
                "time_left": str(timedelta(seconds=battery.secsleft)) if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "unlimited"
            }
    except Exception:
        pass
    return None