# data/data_buffer.py - 线程安全环形缓冲区

from collections import deque
from threading import Lock
from typing import List, Tuple

from config.settings import BUFFER_SIZE


class DataBuffer:
    """线程安全的环形缓冲区，存储 ECG/PPG 原始数据"""

    def __init__(self, maxlen: int = BUFFER_SIZE):
        self._lock = Lock()
        self._ecg_buffer: deque = deque(maxlen=maxlen)
        self._ppg_buffer: deque = deque(maxlen=maxlen)
        self._timestamps: deque = deque(maxlen=maxlen)
        self._sample_count: int = 0

    def push(self, ecg: float, ppg: float, timestamp: str = "") -> None:
        """压入一组 ECG/PPG 数据"""
        with self._lock:
            self._ecg_buffer.append(ecg)
            self._ppg_buffer.append(ppg)
            self._timestamps.append(timestamp)
            self._sample_count += 1

    def get_recent(self, n: int) -> Tuple[List[float], List[float]]:
        """获取最近 n 个 ECG 和 PPG 数据点"""
        with self._lock:
            ecg = list(self._ecg_buffer)[-n:] if n < len(self._ecg_buffer) else list(self._ecg_buffer)
            ppg = list(self._ppg_buffer)[-n:] if n < len(self._ppg_buffer) else list(self._ppg_buffer)
            return ecg, ppg

    def get_all(self) -> Tuple[List[float], List[float], List[str]]:
        """获取全部缓冲数据"""
        with self._lock:
            return (
                list(self._ecg_buffer),
                list(self._ppg_buffer),
                list(self._timestamps),
            )

    def get_ecg(self) -> List[float]:
        """获取全部 ECG 数据"""
        with self._lock:
            return list(self._ecg_buffer)

    def get_ppg(self) -> List[float]:
        """获取全部 PPG 数据"""
        with self._lock:
            return list(self._ppg_buffer)

    @property
    def sample_count(self) -> int:
        with self._lock:
            return self._sample_count

    @property
    def length(self) -> int:
        with self._lock:
            return len(self._ecg_buffer)

    def clear(self) -> None:
        """清空缓冲区"""
        with self._lock:
            self._ecg_buffer.clear()
            self._ppg_buffer.clear()
            self._timestamps.clear()
            self._sample_count = 0
