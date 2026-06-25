# core/data_processor.py - 数据处理管线调度器

from typing import List, Optional

from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from config.settings import SAMPLE_RATE, DISPLAY_WINDOW, RECORD_INTERVAL_MS
from core.ecg_filter import ECGFilter
from core.ppg_filter import PPGFilter
from core.r_peak_detector import RPeakDetector
from core.heart_rate import HeartRateCalculator
from core.spo2_calculator import SpO2Calculator
from core.pulse_rate import PulseRateCalculator
from core.alarm_manager import AlarmManager
from data.data_buffer import DataBuffer
from data.data_recorder import DataRecorder
from utils.helpers import timestamp_now


class DataProcessor(QObject):
    """数据处理管线：接收原始数据 → 滤波/检测/计算 → 聚合发射"""

    vitals_updated = pyqtSignal(dict)   # 生命体征更新
    ecg_filtered_ready = pyqtSignal(list)  # 滤波后 ECG 数据
    ppg_filtered_ready = pyqtSignal(list)  # 滤波后 PPG 数据

    def __init__(self, parent=None):
        super().__init__(parent)
        self._buffer = DataBuffer()
        self._ecg_filter = ECGFilter()
        self._ppg_filter = PPGFilter()
        self._r_peak_detector = RPeakDetector()
        self._hr_calculator = HeartRateCalculator()
        self._spo2_calculator = SpO2Calculator()
        self._pr_calculator = PulseRateCalculator()
        self._alarm_manager = AlarmManager()
        self._recorder = DataRecorder()

        self._last_ecg_raw: float = 0.0
        self._last_ppg_raw: float = 0.0
        self._last_ppg_ir: float = 0.0
        self._last_ecg_filtered: float = 0.0
        self._last_ppg_filtered: float = 0.0
        self._processing_interval = 40  # ms (25Hz 处理频率)

        # 定时处理
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._process)
        self._timer.setInterval(self._processing_interval)

        # 定时记录
        self._record_timer = QTimer(self)
        self._record_timer.timeout.connect(self._record_data)
        self._record_timer.setInterval(RECORD_INTERVAL_MS)

        self._running = False
        self._recording = False

    def push_raw_data(self, ecg: int, ppg: int, timestamp: str = "") -> None:
        """接收原始数据"""
        self._last_ecg_raw = float(ecg)
        self._last_ppg_raw = float(ppg)
        self._buffer.push(float(ecg), float(ppg), timestamp or timestamp_now())

    def push_ppg_ir(self, ir: int, timestamp: str = "") -> None:
        """接收 PPG IR 数据"""
        self._last_ppg_ir = float(ir)

    def start_processing(self) -> None:
        """开始数据处理"""
        self._running = True
        self._timer.start()
        # 自动开始记录数据
        if not self._recording:
            self.start_recording()

    def stop_processing(self) -> None:
        """停止数据处理"""
        self._running = False
        self._timer.stop()
        # 自动停止记录
        if self._recording:
            self.stop_recording()

    def start_recording(self, directory: str = "") -> str:
        """开始数据记录"""
        self._recording = True
        filepath = self._recorder.start_recording(directory) if directory else self._recorder.start_recording()
        self._record_timer.start()
        return filepath

    def stop_recording(self) -> None:
        """停止数据记录"""
        self._recording = False
        self._record_timer.stop()
        self._recorder.stop_recording()

    def _process(self) -> None:
        """定时处理管线"""
        if not self._running:
            return

        ecg_data = self._buffer.get_ecg()
        ppg_data = self._buffer.get_ppg()

        if len(ecg_data) < SAMPLE_RATE:
            return

        # 1. ECG 滤波
        ecg_filtered = self._ecg_filter.apply(ecg_data)
        self._last_ecg_filtered = ecg_filtered[-1] if ecg_filtered else 0.0

        # 2. R 峰检测
        r_peaks, r_amplitudes = self._r_peak_detector.detect(ecg_filtered)

        # 3. 心率计算
        hr = self._hr_calculator.update(r_peaks)

        # 4. PPG 滤波
        ppg_filtered = self._ppg_filter.apply(ppg_data)
        self._last_ppg_filtered = ppg_filtered[-1] if ppg_filtered else 0.0

        # 5. SpO2 计算
        spo2 = self._spo2_calculator.update(self._last_ppg_raw, self._last_ppg_ir)

        # 6. 脉搏率计算
        pr = self._pr_calculator.update(ppg_filtered)

        # 7. 报警检查
        self._alarm_manager.check_heart_rate(hr)
        self._alarm_manager.check_spo2(spo2)
        self._alarm_manager.check_pulse_rate(pr)

        # 8. 发射更新信号
        vitals = {
            "heart_rate": hr,
            "spo2": spo2,
            "pulse_rate": pr,
            "r_peaks": r_peaks,
            "r_amplitudes": r_amplitudes,
        }
        self.vitals_updated.emit(vitals)

        # 发射滤波后波形数据（最近显示窗口）
        display_samples = DISPLAY_WINDOW * SAMPLE_RATE
        self.ecg_filtered_ready.emit(ecg_filtered[-display_samples:])
        self.ppg_filtered_ready.emit(ppg_filtered[-display_samples:])

    def _record_data(self) -> None:
        """定时记录数据"""
        if not self._recording:
            return
        self._recorder.record(
            timestamp=timestamp_now(),
            ecg_raw=self._last_ecg_raw,
            ecg_filtered=self._last_ecg_filtered,
            ppg_raw=self._last_ppg_raw,
            ppg_filtered=self._last_ppg_filtered,
            heart_rate=self._hr_calculator.heart_rate,
            spo2=self._spo2_calculator.spo2,
            pulse_rate=self._pr_calculator.pulse_rate,
        )

    # ---- 属性访问 ----
    @property
    def buffer(self) -> DataBuffer:
        return self._buffer

    @property
    def ecg_filter(self) -> ECGFilter:
        return self._ecg_filter

    @property
    def ppg_filter(self) -> PPGFilter:
        return self._ppg_filter

    @property
    def alarm_manager(self) -> AlarmManager:
        return self._alarm_manager

    @property
    def recorder(self) -> DataRecorder:
        return self._recorder

    @property
    def heart_rate(self) -> float:
        return self._hr_calculator.heart_rate

    @property
    def spo2(self) -> float:
        return self._spo2_calculator.spo2

    @property
    def pulse_rate(self) -> float:
        return self._pr_calculator.pulse_rate

    @property
    def is_recording(self) -> bool:
        return self._recording

    def reset(self) -> None:
        """重置所有模块"""
        self._buffer.clear()
        self._r_peak_detector.reset()
        self._hr_calculator.reset()
        self._spo2_calculator.reset()
        self._pr_calculator.reset()
        self._alarm_manager.reset()
