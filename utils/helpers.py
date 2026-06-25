# utils/helpers.py - 通用工具函数

from datetime import datetime
from typing import Optional


def timestamp_now() -> str:
    """返回当前时间戳字符串，格式 YYYY-MM-DD HH:MM:SS.fff"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def timestamp_short() -> str:
    """返回短时间戳，格式 HH:MM:SS"""
    return datetime.now().strftime("%H:%M:%S")


def xor_checksum(data: bytes) -> int:
    """计算异或校验和"""
    result = 0
    for b in data:
        result ^= b
    return result


def validate_frame_checksum(frame: bytes) -> bool:
    """验证数据帧校验和"""
    if len(frame) < 2:
        return False
    payload = frame[:-1]
    expected = frame[-1]
    return xor_checksum(payload) == expected


def clamp(value: float, min_val: float, max_val: float) -> float:
    """将值限制在 [min_val, max_val] 范围内"""
    return max(min_val, min(max_val, value))


def moving_average(data: list, window: int) -> list:
    """简单移动平均滤波"""
    if len(data) < window:
        return list(data)
    result = []
    for i in range(len(data)):
        start = max(0, i - window + 1)
        result.append(sum(data[start:i + 1]) / (i - start + 1))
    return result


def format_duration(seconds: float) -> str:
    """格式化时长为 HH:MM:SS"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """安全除法，避免除零"""
    return a / b if b != 0 else default
