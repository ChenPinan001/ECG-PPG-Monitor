# core/spo2_calculator.py - 血氧饱和度计算

from collections import deque
from typing import List, Optional

import numpy as np

from config.settings import (
    SPO2_CALIBRATION_A, SPO2_CALIBRATION_B,
    SPO2_MIN, SPO2_MAX, SAMPLE_RATE,
)
from utils.helpers import clamp


class SpO2Calculator:
    """血氧饱和度计算（红光/红外光 AC/DC 比值法）"""

    def __init__(self):
        self._current_spo2: float = 0.0
        self._dc_red: float = 0.0
        self._dc_ir: float = 0.0
        self._ac_red: float = 0.0
        self._ac_ir: float = 0.0
        self._buffer_red: deque = deque(maxlen=SAMPLE_RATE * 4)   # 4秒缓冲
        self._buffer_ir: deque = deque(maxlen=SAMPLE_RATE * 4)
        self._spo2_history: deque = deque(maxlen=10)  # 平滑历史

    def update(self, ppg_red: float, ppg_ir: float = 0.0) -> float:
        """
        更新血氧计算
        ppg_red: 红光 PPG AC 值 (DC已去除)
        ppg_ir: 红外光 PPG AC 值 (DC已去除)
        """
        self._buffer_red.append(ppg_red)

        if ppg_ir != 0.0:
            self._buffer_ir.append(ppg_ir)

        if len(self._buffer_red) < SAMPLE_RATE:
            return self._current_spo2

        red_data = np.array(list(self._buffer_red))

        # AC 分量 (信号已是 AC, 用峰值估算)
        self._ac_red = np.std(red_data)

        if self._buffer_ir:
            ir_data = np.array(list(self._buffer_ir))
            self._ac_ir = np.std(ir_data)
        else:
            self._ac_ir = self._ac_red * 0.8

        # R 比值: 红光AC / 红外AC (DC已去除, 不再除DC)
        if self._ac_ir > 0:
            r_ratio = self._ac_red / self._ac_ir
        else:
            return self._current_spo2

        # 经验校准公式: SpO2 = A - B * R
        spo2_raw = SPO2_CALIBRATION_A - SPO2_CALIBRATION_B * r_ratio
        spo2_raw = clamp(spo2_raw, SPO2_MIN, SPO2_MAX)

        # 滑动平均平滑
        self._spo2_history.append(spo2_raw)
        self._current_spo2 = round(np.mean(list(self._spo2_history)), 1)

        return self._current_spo2

    def reset(self) -> None:
        """重置计算器"""
        self._current_spo2 = 0.0
        self._buffer_red.clear()
        self._buffer_ir.clear()
        self._spo2_history.clear()

    @property
    def spo2(self) -> float:
        return self._current_spo2
