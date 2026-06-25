# core/r_peak_detector.py - R 峰检测

from typing import List, Tuple

import numpy as np

from config.settings import (
    SAMPLE_RATE,
    RPEAK_REFRACTORY,
    RPEAK_SEARCH_BACK,
)


class RPeakDetector:
    """R 峰检测算法 (带基线矫正)"""

    def __init__(self):
        self._last_rr_intervals: List[float] = []
        self._last_r_index: int = 0
        self._dc_avg: float = 0.0
        self._dc_initialized: bool = False
        self._threshold: float = 0.0

    def detect(self, signal: List[float]) -> Tuple[List[int], List[float]]:
        """
        检测 R 峰位置
        返回: (R峰索引列表, 对应的幅值列表)
        """
        if len(signal) < SAMPLE_RATE:
            return [], []

        sig = np.array(signal, dtype=np.float64)

        # 基线矫正: 指数滑动平均
        if not self._dc_initialized:
            self._dc_avg = np.mean(sig)
            self._dc_initialized = True

        dc_new = np.mean(sig[-400:]) if len(sig) >= 400 else np.mean(sig)
        self._dc_avg = self._dc_avg * 0.95 + dc_new * 0.05
        sig = sig - self._dc_avg

        # 差分 + 平方 (增强R峰)
        diff_sig = np.diff(sig)
        diff_sig = np.append(diff_sig, 0)
        squared = diff_sig ** 2

        # 滑动窗口积分
        window = int(0.15 * SAMPLE_RATE)  # 150ms
        kernel = np.ones(window) / window
        integrated = np.convolve(squared, kernel, mode="same")

        # 动态阈值: 滑动窗口内最大值的 40%
        win = min(SAMPLE_RATE * 2, len(integrated))
        recent_max = np.max(integrated[-win:])
        self._threshold = recent_max * 0.4

        if self._threshold < 1e-6:
            return [], []

        # 搜索 R 峰
        r_peaks = []
        r_amplitudes = []
        i = 0
        while i < len(integrated):
            if integrated[i] > self._threshold:
                # 找局部最大值
                search_end = min(i + window, len(integrated))
                segment = integrated[i:search_end]
                local_max_idx = i + np.argmax(segment)

                # 在原始信号中微调
                refine_start = max(0, local_max_idx - 5)
                refine_end = min(len(signal), local_max_idx + 5)
                refine_segment = sig[refine_start:refine_end]
                if len(refine_segment) > 0:
                    refined_idx = refine_start + np.argmax(refine_segment)
                else:
                    refined_idx = local_max_idx

                # 不应期检查
                if not r_peaks or (refined_idx - r_peaks[-1]) > RPEAK_REFRACTORY:
                    r_peaks.append(refined_idx)
                    r_amplitudes.append(signal[refined_idx])
                    i = refined_idx + RPEAK_REFRACTORY
                    continue

            i += 1

        # 回溯搜索: 如果距离上次R峰太远，降低阈值重搜
        if r_peaks and (len(signal) - r_peaks[-1]) > RPEAK_SEARCH_BACK:
            search_start = r_peaks[-1] + RPEAK_REFRACTORY
            backtrack_threshold = self._threshold * 0.5
            for j in range(search_start, len(integrated)):
                if integrated[j] > backtrack_threshold:
                    search_end = min(j + window, len(integrated))
                    segment = integrated[j:search_end]
                    local_max_idx = j + np.argmax(segment)

                    if not r_peaks or (local_max_idx - r_peaks[-1]) > RPEAK_REFRACTORY:
                        r_peaks.append(local_max_idx)
                        r_amplitudes.append(signal[local_max_idx])
                    break

        return r_peaks, r_amplitudes

    def reset(self) -> None:
        """重置检测器状态"""
        self._last_r_index = 0
        self._dc_avg = 0.0
        self._dc_initialized = False
        self._threshold = 0.0
