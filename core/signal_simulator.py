# core/signal_simulator.py - ECG/PPG 信号模拟器

import math
import random
from typing import Optional

import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from config.settings import SAMPLE_RATE, FRAME_TYPE_ECG_PPG
from utils.helpers import timestamp_now


class SignalSimulator(QObject):
    """
    ECG/PPG 信号模拟器，在无硬件时生成逼真的人体信号。
    ECG: PQRST 复合波 + 基线漂移 + 肌电噪声 + 工频干扰
    PPG: 脉搏波 + 重搏切迹 + 呼吸调制
    """

    data_received = pyqtSignal(int, int, str)
    simulation_status = pyqtSignal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._timer = QTimer(self)
        self._timer.setInterval(4)  # 4ms -> ~250Hz
        self._timer.timeout.connect(self._tick)

        self._running = False
        self._sample_index = 0

        # 生理参数
        self._heart_rate = 72.0
        self._respiratory_rate = 16.0
        self._spo2_base = 97.0

        # 预生成模板
        self._ecg_template = self._generate_ecg_template()
        self._ppg_template = self._generate_ppg_template()

    def set_heart_rate(self, hr: float) -> None:
        self._heart_rate = max(30.0, min(220.0, hr))
        self._ecg_template = self._generate_ecg_template()
        self._ppg_template = self._generate_ppg_template()

    def set_spo2(self, spo2: float) -> None:
        self._spo2_base = max(70.0, min(100.0, spo2))

    def start(self) -> None:
        self._running = True
        self._sample_index = 0
        self._ecg_template = self._generate_ecg_template()
        self._ppg_template = self._generate_ppg_template()
        self._timer.start()
        self.simulation_status.emit(True, f"模拟模式 | HR={self._heart_rate:.0f}bpm SpO2={self._spo2_base:.0f}%")

    def stop(self) -> None:
        self._running = False
        self._timer.stop()
        self.simulation_status.emit(False, "模拟已停止")

    @property
    def is_running(self) -> bool:
        return self._running

    def _generate_ecg_template(self) -> np.ndarray:
        """生成一个完整心搏周期的 PQRST 模板"""
        samples_per_beat = int(SAMPLE_RATE * 60.0 / self._heart_rate)
        t = np.linspace(0, 1.0, samples_per_beat, endpoint=False)

        # P 波：正弦半波
        p_wave = np.zeros(samples_per_beat)
        p_start = int(0.0 * samples_per_beat)
        p_end = int(0.12 * samples_per_beat)
        p_len = p_end - p_start
        if p_len > 0:
            p_t = np.linspace(0, math.pi, p_len)
            p_wave[p_start:p_end] = 0.12 * np.sin(p_t)

        # Q 波：窄负向尖峰
        q_wave = np.zeros(samples_per_beat)
        q_center = int(0.16 * samples_per_beat)
        q_half = int(0.008 * samples_per_beat)
        q_start = max(0, q_center - q_half)
        q_end = min(samples_per_beat, q_center + q_half)
        q_len = q_end - q_start
        if q_len > 0:
            q_t = np.linspace(0, math.pi, q_len)
            q_wave[q_start:q_end] = -0.08 * np.sin(q_t)

        # R 波：尖锐正向峰值
        r_wave = np.zeros(samples_per_beat)
        r_center = int(0.20 * samples_per_beat)
        r_half = int(0.016 * samples_per_beat)
        r_start = max(0, r_center - r_half)
        r_end = min(samples_per_beat, r_center + r_half)
        r_len = r_end - r_start
        if r_len > 0:
            r_t = np.linspace(0, math.pi, r_len)
            r_wave[r_start:r_end] = 1.2 * np.sin(r_t)

        # S 波：负向尖峰
        s_wave = np.zeros(samples_per_beat)
        s_center = int(0.24 * samples_per_beat)
        s_half = int(0.016 * samples_per_beat)
        s_start = max(0, s_center - s_half)
        s_end = min(samples_per_beat, s_center + s_half)
        s_len = s_end - s_start
        if s_len > 0:
            s_t = np.linspace(0, math.pi, s_len)
            s_wave[s_start:s_end] = -0.25 * np.sin(s_t)

        # T 波：宽正弦波
        t_wave = np.zeros(samples_per_beat)
        t_start = int(0.36 * samples_per_beat)
        t_end = int(0.56 * samples_per_beat)
        t_len = t_end - t_start
        if t_len > 0:
            t_t = np.linspace(0, math.pi, t_len)
            t_wave[t_start:t_end] = 0.30 * np.sin(t_t)

        # U 波：微小正弦波
        u_wave = np.zeros(samples_per_beat)
        u_start = int(0.58 * samples_per_beat)
        u_end = int(0.66 * samples_per_beat)
        u_len = u_end - u_start
        if u_len > 0:
            u_t = np.linspace(0, math.pi, u_len)
            u_wave[u_start:u_end] = 0.03 * np.sin(u_t)

        template = p_wave + q_wave + r_wave + s_wave + t_wave + u_wave

        # 转为 μV 量级 (1000 μV ≈ 1mV)
        template *= 1000.0

        return template

    def _generate_ppg_template(self) -> np.ndarray:
        """生成一个完整心搏周期的 PPG 脉搏波模板"""
        samples_per_beat = int(SAMPLE_RATE * 60.0 / self._heart_rate)
        t = np.linspace(0, 1.0, samples_per_beat, endpoint=False)

        # 主收缩波（systolic peak）
        systolic = np.zeros(samples_per_beat)
        sys_start = int(0.08 * samples_per_beat)
        sys_end = int(0.35 * samples_per_beat)
        sys_len = sys_end - sys_start
        if sys_len > 0:
            half = sys_len // 2
            rise = np.linspace(0, 1.0, half)
            fall = np.linspace(1.0, 0.0, sys_len - half)
            systolic[sys_start:sys_end] = np.concatenate([rise, fall]) ** 1.5

        # 重搏切迹 (dicrotic notch) + 舒张波
        diastolic = np.zeros(samples_per_beat)
        dia_start = int(0.35 * samples_per_beat)
        dia_end = int(0.70 * samples_per_beat)
        dia_len = dia_end - dia_start
        if dia_len > 0:
            # 先降后升再降
            notch = int(0.05 * samples_per_beat)
            dia_rise = np.linspace(0.3, 0.5, notch)
            dia_fall = np.linspace(0.5, 0.0, dia_len - notch)
            diastolic[dia_start:dia_end] = np.concatenate([dia_rise, dia_fall])

        template = systolic + diastolic

        # 缩放到 ADC 范围 (~500-2000)
        template *= 800.0
        template += 1000.0

        return template

    def _tick(self) -> None:
        """每个采样点生成一个 ECG+PPG 值"""
        if not self._running:
            return

        beat_samples = len(self._ecg_template)
        if beat_samples == 0:
            return

        # 当前心搏内的位置
        beat_phase = self._sample_index % beat_samples
        t_seconds = self._sample_index / SAMPLE_RATE

        # ---- ECG ----
        ecg_clean = self._ecg_template[beat_phase]

        # 基线漂移 (0.15-0.3 Hz 呼吸相关) - 减小幅度
        baseline_wander = 30.0 * math.sin(2.0 * math.pi * 0.2 * t_seconds)
        baseline_wander += 10.0 * math.sin(2.0 * math.pi * 0.35 * t_seconds)

        # 肌电噪声 (随机高斯) - 大幅减小
        muscle_noise = random.gauss(0, 3)

        # 工频干扰 (50Hz) - 大幅减小
        powerline = 2.0 * math.sin(2.0 * math.pi * 50.0 * t_seconds)

        ecg_value = ecg_clean + baseline_wander + muscle_noise + powerline

        # ---- PPG ----
        ppg_clean = self._ppg_template[beat_phase]

        # PPG 基线漂移 (呼吸调制) - 减小幅度
        ppg_baseline = 20.0 * math.sin(2.0 * math.pi * 0.25 * t_seconds)

        # 随机噪声 - 大幅减小
        ppg_noise = random.gauss(0, 2)

        ppg_value = ppg_clean + ppg_baseline + ppg_noise

        # 心跳间变异 (HRV): 微小心率波动
        hrv_offset = 0.3 * math.sin(2.0 * math.pi * 0.1 * t_seconds)

        # SpO2 调制: 通过 PPG AC/DC 比反映 SpO2 水平
        spo2_mod = self._spo2_base / 100.0
        ppg_value *= (0.5 + 0.5 * spo2_mod)

        # 发射信号 (转为 int 与串口协议兼容)
        ecg_int = int(ecg_value)
        ppg_int = int(ppg_value)
        ts = timestamp_now()

        self.data_received.emit(ecg_int, ppg_int, ts)
        self._sample_index += 1

    def reset(self) -> None:
        """重置模拟器"""
        self.stop()
        self._sample_index = 0
