# core/pulse_rate.py - 脉搏率计算

from collections import deque
from typing import List

import numpy as np

from config.settings import SAMPLE_RATE, PR_MIN, PR_MAX


class PulseRateCalculator:
    """PPG 峰值检测与脉搏率计算"""

    def __init__(self):
        self._current_pr: float = 0.0
        self._peak_intervals: deque = deque(maxlen=8)
        self._last_peak_idx: int = 0
        self._initialized = False
        self._refractory = int(0.4 * SAMPLE_RATE)  # 400ms 不应期
        self._dc_avg: float = 0.0
        self._dc_initialized: bool = False

    def update(self, ppg_data: List[float]) -> float:
        """根据 PPG 数据更新脉搏率"""
        if len(ppg_data) < SAMPLE_RATE:
            return self._current_pr

        peaks = self._detect_ppg_peaks(ppg_data)

        if not self._initialized and peaks:
            self._last_peak_idx = peaks[-1]
            self._initialized = True
            return 0.0

        if not peaks:
            return self._current_pr

        for peak in peaks:
            if peak > self._last_peak_idx:
                interval_samples = peak - self._last_peak_idx
                interval_seconds = interval_samples / SAMPLE_RATE

                if interval_seconds > 0:
                    pr_instant = 60.0 / interval_seconds
                    if PR_MIN <= pr_instant <= PR_MAX:
                        self._peak_intervals.append(interval_seconds)

                self._last_peak_idx = peak

        if self._peak_intervals:
            mean_interval = np.mean(list(self._peak_intervals))
            if mean_interval > 0:
                self._current_pr = round(60.0 / mean_interval, 1)

        return self._current_pr

    def _detect_ppg_peaks(self, data: List[float]) -> List[int]:
        """
        三级峰值检测: 斜率 + 幅度阈值 + 不应期
        """
        if len(data) < 3:
            return []

        sig = np.array(data, dtype=np.float64)

        # 基线矫正
        if not self._dc_initialized:
            self._dc_avg = np.mean(sig)
            self._dc_initialized = True
        dc_new = np.mean(sig[-400:]) if len(sig) >= 400 else np.mean(sig)
        self._dc_avg = self._dc_avg * 0.95 + dc_new * 0.05
        sig = sig - self._dc_avg

        # --- 第一级: 一阶差分找上升沿转下降沿 ---
        diff = np.diff(sig)
        candidates = []
        for i in range(1, len(diff)):
            if diff[i - 1] > 0 and diff[i] <= 0:
                candidates.append(i)

        if not candidates:
            return []

        # --- 第二级: 幅度阈值筛选 (中位数的70%) ---
        peak_values = [sig[c] for c in candidates]
        threshold = np.median(peak_values) * 0.7
        if threshold < 1.0:
            return []

        candidates = [c for c in candidates if sig[c] > threshold]

        if not candidates:
            return []

        # --- 第三级: 不应期过滤 + 区间内只保留最高峰 ---
        peaks = []
        for c in candidates:
            if not peaks:
                peaks.append(c)
            else:
                gap = c - peaks[-1]
                if gap > self._refractory:
                    peaks.append(c)
                elif sig[c] > sig[peaks[-1]]:
                    peaks[-1] = c  # 替换为更高的峰

        return peaks

    def reset(self) -> None:
        """重置计算器"""
        self._current_pr = 0.0
        self._peak_intervals.clear()
        self._last_peak_idx = 0
        self._initialized = False
        self._dc_avg = 0.0
        self._dc_initialized = False

    @property
    def pulse_rate(self) -> float:
        return self._current_pr
