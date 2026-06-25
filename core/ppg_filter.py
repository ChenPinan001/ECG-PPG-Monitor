# core/ppg_filter.py - PPG 数字滤波器

from typing import List, Optional, Tuple

import numpy as np
from scipy.signal import butter, filtfilt, lfilter

from config.settings import SAMPLE_RATE


class PPGFilter:
    """PPG 数字滤波器：高通 + 低通 + 50Hz陷波 + 移动平均"""

    def __init__(self):
        self._hp_enabled = True
        self._lp_enabled = True
        self._ma_enabled = True
        self._notch_enabled = True
        
        # PPG专用参数
        self._hp_cutoff = 0.3    # 高通截止频率
        self._hp_order = 2
        self._lp_cutoff = 10.0   # 低通截止频率 (PPG主能量0.5-10Hz)
        self._lp_order = 2       # 降低阶数，减少lfilter延迟和瞬态
        self._ma_window = 3      # 移动平均窗口
        
        self._hp_b: Optional[np.ndarray] = None
        self._hp_a: Optional[np.ndarray] = None
        self._lp_b: Optional[np.ndarray] = None
        self._lp_a: Optional[np.ndarray] = None
        self._notch_b: Optional[np.ndarray] = None
        self._notch_a: Optional[np.ndarray] = None
        self._design_filters()

    def _design_filters(self) -> None:
        """设计滤波器系数"""
        nyquist = SAMPLE_RATE / 2.0

        # 高通滤波器
        hp_normal = self._hp_cutoff / nyquist
        self._hp_b, self._hp_a = butter(
            self._hp_order, hp_normal, btype="high", analog=False
        )

        # 低通滤波器
        lp_normal = self._lp_cutoff / nyquist
        self._lp_b, self._lp_a = butter(
            self._lp_order, lp_normal, btype="low", analog=False
        )

        # 50Hz陷波滤波器
        self._notch_b, self._notch_a = self._design_notch(50.0, SAMPLE_RATE, Q=15.0)

    @staticmethod
    def _design_notch(freq: float, fs: float, Q: float = 30.0) -> Tuple[np.ndarray, np.ndarray]:
        """设计陷波滤波器"""
        w0 = 2 * np.pi * freq / fs
        alpha = np.sin(w0) / (2 * Q)

        b = np.array([1.0, -2.0 * np.cos(w0), 1.0])
        a = np.array([1.0 + alpha, -2.0 * np.cos(w0), 1.0 - alpha])

        b = b / a[0]
        a = a / a[0]

        return b, a

    def set_hp_enabled(self, enabled: bool) -> None:
        self._hp_enabled = enabled

    def set_lp_enabled(self, enabled: bool) -> None:
        self._lp_enabled = enabled

    def set_ma_enabled(self, enabled: bool) -> None:
        self._ma_enabled = enabled

    def set_notch_enabled(self, enabled: bool) -> None:
        self._notch_enabled = enabled

    def apply(self, data: List[float]) -> List[float]:
        """对PPG数据应用滤波"""
        if len(data) < 10:
            return list(data)

        signal = np.array(data, dtype=np.float64)

        # 高通滤波 (去除低频漂移)
        if self._hp_enabled and self._hp_b is not None:
            try:
                signal = lfilter(self._hp_b, self._hp_a, signal)
            except ValueError:
                pass

        # 50Hz陷波 (去除工频干扰)
        if self._notch_enabled and self._notch_b is not None:
            try:
                signal = lfilter(self._notch_b, self._notch_a, signal)
            except ValueError:
                pass

        # 低通滤波
        if self._lp_enabled and self._lp_b is not None:
            try:
                signal = lfilter(self._lp_b, self._lp_a, signal)
            except ValueError:
                pass

        # 移动平均
        if self._ma_enabled and len(signal) >= self._ma_window:
            kernel = np.ones(self._ma_window) / self._ma_window
            signal = np.convolve(signal, kernel, mode="same")

        return signal.tolist()

    @property
    def hp_enabled(self) -> bool:
        return self._hp_enabled

    @property
    def lp_enabled(self) -> bool:
        return self._lp_enabled

    @property
    def ma_enabled(self) -> bool:
        return self._ma_enabled

    @property
    def notch_enabled(self) -> bool:
        return self._notch_enabled
