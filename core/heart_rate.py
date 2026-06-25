# core/heart_rate.py - 心率计算

from collections import deque
from typing import List, Optional

import numpy as np

from config.settings import SAMPLE_RATE, HR_AVERAGING_BEATS, HR_MIN, HR_MAX


class HeartRateCalculator:
    """基于 RR 间期计算心率（BPM）"""

    def __init__(self):
        self._rr_intervals: deque = deque(maxlen=HR_AVERAGING_BEATS)
        self._current_hr: float = 0.0
        self._last_r_index: int = 0
        self._initialized = False

    def update(self, r_peaks: List[int]) -> float:
        """
        根据新检测到的 R 峰更新心率
        返回: 当前心率 BPM
        """
        if not r_peaks:
            return self._current_hr

        if not self._initialized:
            self._last_r_index = r_peaks[-1]
            self._initialized = True
            return 0.0

        # 计算新的 RR 间期
        for peak in r_peaks:
            if peak > self._last_r_index:
                rr_samples = peak - self._last_r_index
                rr_seconds = rr_samples / SAMPLE_RATE

                # 合理性检查
                if rr_seconds > 0:
                    hr_instant = 60.0 / rr_seconds
                    if HR_MIN <= hr_instant <= HR_MAX:
                        self._rr_intervals.append(rr_seconds)

                self._last_r_index = peak

        # 滑动平均计算心率
        if self._rr_intervals:
            mean_rr = np.mean(list(self._rr_intervals))
            if mean_rr > 0:
                self._current_hr = round(60.0 / mean_rr, 1)

        return self._current_hr

    def reset(self) -> None:
        """重置计算器"""
        self._rr_intervals.clear()
        self._current_hr = 0.0
        self._last_r_index = 0
        self._initialized = False

    @property
    def heart_rate(self) -> float:
        return self._current_hr

    @property
    def rr_interval(self) -> float:
        """返回最近 RR 间期（秒）"""
        if self._rr_intervals:
            return self._rr_intervals[-1]
        return 0.0
