"""
디스크 리소스 모니터링 유틸리티
"""

import os
import psutil
from typing import Dict, Any, List, Optional
from pathlib import Path


class DiskUsage:
    """디스크 사용량 모니터링 클래스"""
    
    def __init__(self):
        self.units = {
            "B": 1,
            "KB": 1024,
            "MB": 1024**2,
            "GB": 1024**3,
            "TB": 1024**4,
            "PB": 1024**5
        }
    
    def _format_bytes(self, bytes_value: int, unit: str = "auto") -> tuple:
        """바이트를 지정된 단위로 변환"""
        if unit == "auto":
            # 자동으로 적절한 단위 선택
            for unit_name in ["PB", "TB", "GB", "MB", "KB", "B"]:
                unit_value = self.units[unit_name]
                if bytes_value >= unit_value:
                    return round(bytes_value / unit_value, 2), unit_name
            return bytes_value, "B"
        else:
            unit = unit.upper()
            if unit in self.units:
                return round(bytes_value / self.units[unit], 2), unit
            else:
                return bytes_value, "B"
    
    def get_disk_usage(self, path: str = "all", unit: str = "auto") -> Dict[str, Any]:
        """디스크 사용량 정보 반환"""
        result = {}
        
        try:
            if path == "all":
                # 모든 마운트 포인트 조회
                partitions = psutil.disk_partitions()
                
                for partition in partitions:
                    try:
                        # 시스템 파티션이나 접근 불가능한 파티션 건너뛰기
                        if partition.fstype == '' or 'cdrom' in partition.opts:
                            continue
                        
                        usage = psutil.disk_usage(partition.mountpoint)
                        
                        total, total_unit = self._format_bytes(usage.total, unit)
                        used, used_unit = self._format_bytes(usage.used, unit)
                        free, free_unit = self._format_bytes(usage.free, unit)
                        
                        # 단위 통일 (가장 큰 값의 단위 사용)
                        if unit == "auto":
                            max_unit = total_unit
                            total, _ = self._format_bytes(usage.total, max_unit)
                            used, _ = self._format_bytes(usage.used, max_unit)
                            free, _ = self._format_bytes(usage.free, max_unit)
                            display_unit = max_unit
                        else:
                            display_unit = unit.upper()
                        
                        result[partition.mountpoint] = {
                            "device": partition.device,
                            "fstype": partition.fstype,
                            "total": total,
                            "used": used,
                            "free": free,
                            "percent": round((usage.used / usage.total) * 100, 1) if usage.total > 0 else 0,
                            "unit": display_unit
                        }
                    
                    except (PermissionError, OSError):
                        # 접근 권한이 없거나 마운트되지 않은 파티션 건너뛰기
                        continue
            
            else:
                # 특정 경로의 디스크 사용량
                if not os.path.exists(path):
                    return {"error": f"Path does not exist: {path}"}
                
                usage = psutil.disk_usage(path)
                
                total, total_unit = self._format_bytes(usage.total, unit)
                used, used_unit = self._format_bytes(usage.used, unit)
                free, free_unit = self._format_bytes(usage.free, unit)
                
                if unit == "auto":
                    max_unit = total_unit
                    total, _ = self._format_bytes(usage.total, max_unit)
                    used, _ = self._format_bytes(usage.used, max_unit)
                    free, _ = self._format_bytes(usage.free, max_unit)
                    display_unit = max_unit
                else:
                    display_unit = unit.upper()
                
                result[path] = {
                    "total": total,
                    "used": used,
                    "free": free,
                    "percent": round((usage.used / usage.total) * 100, 1) if usage.total > 0 else 0,
                    "unit": display_unit
                }
        
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def get_disk_io_stats(self) -> Dict[str, Any]:
        """디스크 I/O 통계 반환"""
        try:
            disk_io = psutil.disk_io_counters()
            
            if disk_io:
                return {
                    "read_count": disk_io.read_count,
                    "write_count": disk_io.write_count,
                    "read_bytes": disk_io.read_bytes,
                    "write_bytes": disk_io.write_bytes,
                    "read_time": disk_io.read_time,
                    "write_time": disk_io.write_time
                }
            else:
                return {"error": "Disk I/O stats not available"}
        
        except Exception as e:
            return {"error": str(e)}
    
    def get_disk_io_per_device(self) -> Dict[str, Dict[str, Any]]:
        """디바이스별 디스크 I/O 통계 반환"""
        try:
            disk_io_per_device = psutil.disk_io_counters(perdisk=True)
            
            result = {}
            for device, stats in disk_io_per_device.items():
                result[device] = {
                    "read_count": stats.read_count,
                    "write_count": stats.write_count,
                    "read_bytes": stats.read_bytes,
                    "write_bytes": stats.write_bytes,
                    "read_time": stats.read_time,
                    "write_time": stats.write_time
                }
            
            return result
        
        except Exception as e:
            return {"error": str(e)}
    
    def get_directory_size(self, path: str, unit: str = "auto") -> Dict[str, Any]:
        """디렉토리 크기 계산"""
        try:
            if not os.path.exists(path):
                return {"error": f"Path does not exist: {path}"}
            
            if not os.path.isdir(path):
                # 파일인 경우
                size = os.path.getsize(path)
                formatted_size, size_unit = self._format_bytes(size, unit)
                
                return {
                    "path": path,
                    "type": "file",
                    "size": formatted_size,
                    "unit": size_unit,
                    "files": 1,
                    "directories": 0
                }
            
            # 디렉토리인 경우
            total_size = 0
            file_count = 0
            dir_count = 0
            
            for dirpath, dirnames, filenames in os.walk(path):
                dir_count += len(dirnames)
                for filename in filenames:
                    try:
                        filepath = os.path.join(dirpath, filename)
                        total_size += os.path.getsize(filepath)
                        file_count += 1
                    except (OSError, IOError):
                        # 접근 권한이 없는 파일 건너뛰기
                        continue
            
            formatted_size, size_unit = self._format_bytes(total_size, unit)
            
            return {
                "path": path,
                "type": "directory",
                "size": formatted_size,
                "unit": size_unit,
                "files": file_count,
                "directories": dir_count
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    def get_largest_files(self, path: str, count: int = 10, unit: str = "auto") -> List[Dict[str, Any]]:
        """디렉토리에서 가장 큰 파일들 반환"""
        try:
            if not os.path.exists(path) or not os.path.isdir(path):
                return [{"error": f"Directory does not exist: {path}"}]
            
            files = []
            
            for dirpath, _, filenames in os.walk(path):
                for filename in filenames:
                    try:
                        filepath = os.path.join(dirpath, filename)
                        size = os.path.getsize(filepath)
                        files.append((filepath, size))
                    except (OSError, IOError):
                        continue
            
            # 크기순으로 정렬
            files.sort(key=lambda x: x[1], reverse=True)
            
            result = []
            for filepath, size in files[:count]:
                formatted_size, size_unit = self._format_bytes(size, unit)
                result.append({
                    "path": filepath,
                    "size": formatted_size,
                    "unit": size_unit,
                    "relative_path": os.path.relpath(filepath, path)
                })
            
            return result
        
        except Exception as e:
            return [{"error": str(e)}]


def get_color_by_threshold(percent: float, return_tuple: bool = False):
    """사용률에 따른 색상 반환"""
    if percent >= 90:
        color = "red"
    elif percent >= 80:
        color = "yellow"
    elif percent >= 70:
        color = "orange"
    else:
        color = "green"
    
    if return_tuple:
        return color, percent
    return color