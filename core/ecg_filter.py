# core/ecg_filter.py - ECG 数字滤波器

from typing import List, Optional, Tuple

import numpy as np
from scipy.signal import butter, filtfilt, lfilter

from config.settings import (
    SAMPLE_RATE,
    ECG_HP_CUTOFF, ECG_HP_ORDER,
    ECG_LP_CUTOFF, ECG_LP_ORDER,
    ECG_MA_WINDOW,
)


class ECGFilter:
    """ECG 数字滤波器：高通 + 低通 + 50Hz陷波 + 移动平均"""

    def __init__(self):
        self._hp_enabled = False
        self._lp_enabled = False
        self._ma_enabled = False
        self._notch_enabled = True
        self._hp_b: Optional[np.ndarray] = None
        self._hp_a: Optional[np.ndarray] = None
        self._lp_b: Optional[np.ndarray] = None
        self._lp_a: Optional[np.ndarray] = None
        self._notch_b: Optional[np.ndarray] = None
        self._notch_a: Optional[np.ndarray] = None
        self._design_filters()

    def _design_filters(self) -> None:
        """设计 Butterworth 滤波器系数"""
        nyquist = SAMPLE_RATE / 2.0

        # 高通滤波器
        hp_normal = ECG_HP_CUTOFF / nyquist
        self._hp_b, self._hp_a = butter(
            ECG_HP_ORDER, hp_normal, btype="high", analog=False
        )

        # 低通滤波器
        lp_normal = ECG_LP_CUTOFF / nyquist
        self._lp_b, self._lp_a = butter(
            ECG_LP_ORDER, lp_normal, btype="low", analog=False
        )

        # 50Hz陷波滤波器 (二阶IIR陷波)
        self._notch_b, self._notch_a = self._design_notch(50.0, SAMPLE_RATE, Q=30.0)

    @staticmethod
    def _design_notch(freq: float, fs: float, Q: float = 30.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        设计50Hz陷波滤波器 (二阶IIR)
        freq: 陷波频率 (50Hz)
        fs: 采样率
        Q: 品质因数 (越大陷波越窄)
        """
        w0 = 2 * np.pi * freq / fs
        alpha = np.sin(w0) / (2 * Q)

        b = np.array([1.0, -2.0 * np.cos(w0), 1.0])
        a = np.array([1.0 + alpha, -2.0 * np.cos(w0), 1.0 - alpha])

        # 归一化
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
        """对数据依次应用滤波"""
        if len(data) < 10:
            return list(data)

        signal = np.array(data, dtype=np.float64)

        # 高通滤波
        if self._hp_enabled and self._hp_b is not None:
            try:
                signal = lfilter(self._hp_b, self._hp_a, signal)
            except ValueError:
                pass

        # 低通滤波
        if self._lp_enabled and self._lp_b is not None:
            try:
                signal = lfilter(self._lp_b, self._lp_a, signal)
            except ValueError:
                pass

        # 50Hz陷波滤波
        if self._notch_enabled and self._notch_b is not None:
            try:
                signal = lfilter(self._notch_b, self._notch_a, signal)
            except ValueError:
                pass

        # 移动平均
        if self._ma_enabled:
            signal = self._moving_average(signal, ECG_MA_WINDOW)

        return signal.tolist()

    @staticmethod
    def _moving_average(data: np.ndarray, window: int) -> np.ndarray:
        """移动平均滤波"""
        if len(data) < window:
            return data
        kernel = np.ones(window) / window
        return np.convolve(data, kernel, mode="same")

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
