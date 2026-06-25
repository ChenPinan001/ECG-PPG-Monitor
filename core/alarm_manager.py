# core/alarm_manager.py - 异常报警管理

from datetime import datetime
from typing import List, Dict, Any, Optional

from PyQt5.QtCore import QObject, pyqtSignal

from config.settings import (
    ALARM_THRESHOLDS,
    ALARM_LEVEL_EMERGENCY,
    ALARM_LEVEL_HIGH,
    ALARM_LEVEL_MEDIUM,
)


class AlarmEvent:
    """报警事件"""

    def __init__(self, level: str, parameter: str, value: float,
                 threshold: float, message: str):
        self.level = level
        self.parameter = parameter
        self.value = value
        self.threshold = threshold
        self.message = message
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "parameter": self.parameter,
            "value": self.value,
            "threshold": self.threshold,
            "message": self.message,
            "timestamp": self.timestamp,
        }


class AlarmManager(QObject):
    """报警管理器：阈值判断 + 分级报警 + 去抖动"""

    alarm_triggered = pyqtSignal(str, str, float, str)  # level, param, value, timestamp
    alarm_cleared = pyqtSignal(str)  # parameter

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thresholds = ALARM_THRESHOLDS
        self._active_alarms: Dict[str, AlarmEvent] = {}
        self._alarm_history: List[AlarmEvent] = []
        self._last_signal_time: float = 0.0
        self._signal_loss_count: int = 0
        self._debounce_counters: Dict[str, int] = {}
        self._debounce_threshold = 3  # 连续3次超阈值才报警

    def check_heart_rate(self, hr: float) -> Optional[AlarmEvent]:
        """检查心率"""
        if hr <= 0:
            return None

        if hr < self._thresholds.hr_low:
            return self._raise_alarm(
                ALARM_LEVEL_HIGH, "heart_rate", hr,
                self._thresholds.hr_low, f"心率过低: {hr} BPM"
            )
        elif hr > self._thresholds.hr_high:
            return self._raise_alarm(
                ALARM_LEVEL_HIGH, "heart_rate", hr,
                self._thresholds.hr_high, f"心率过高: {hr} BPM"
            )
        else:
            self._clear_alarm("heart_rate")
            return None

    def check_spo2(self, spo2: float) -> Optional[AlarmEvent]:
        """检查血氧"""
        if spo2 <= 0:
            return None

        if spo2 < self._thresholds.spo2_low:
            return self._raise_alarm(
                ALARM_LEVEL_EMERGENCY, "spo2", spo2,
                self._thresholds.spo2_low, f"血氧过低: {spo2}%"
            )
        else:
            self._clear_alarm("spo2")
            return None

    def check_pulse_rate(self, pr: float) -> Optional[AlarmEvent]:
        """检查脉搏率"""
        if pr <= 0:
            return None

        if pr < self._thresholds.pr_low:
            return self._raise_alarm(
                ALARM_LEVEL_MEDIUM, "pulse_rate", pr,
                self._thresholds.pr_low, f"脉搏率过低: {pr} bpm"
            )
        elif pr > self._thresholds.pr_high:
            return self._raise_alarm(
                ALARM_LEVEL_MEDIUM, "pulse_rate", pr,
                self._thresholds.pr_high, f"脉搏率过高: {pr} bpm"
            )
        else:
            self._clear_alarm("pulse_rate")
            return None

    def check_signal_loss(self, has_signal: bool, elapsed: float) -> Optional[AlarmEvent]:
        """检查信号丢失"""
        if not has_signal:
            self._signal_loss_count += 1
        else:
            self._signal_loss_count = 0

        if self._signal_loss_count > self._thresholds.signal_loss_seconds * 250:
            return self._raise_alarm(
                ALARM_LEVEL_HIGH, "signal_loss", 0,
                0, f"信号丢失超过 {self._thresholds.signal_loss_seconds} 秒"
            )
        else:
            self._clear_alarm("signal_loss")
            return None

    def _raise_alarm(self, level: str, parameter: str, value: float,
                     threshold: float, message: str) -> Optional[AlarmEvent]:
        """触发报警（带去抖动）"""
        # 去抖动计数
        key = parameter
        self._debounce_counters[key] = self._debounce_counters.get(key, 0) + 1

        if self._debounce_counters[key] < self._debounce_threshold:
            return None

        # 检查是否已经激活
        if parameter in self._active_alarms:
            return None

        event = AlarmEvent(level, parameter, value, threshold, message)
        self._active_alarms[parameter] = event
        self._alarm_history.append(event)

        self.alarm_triggered.emit(level, parameter, value, event.timestamp)
        return event

    def _clear_alarm(self, parameter: str) -> None:
        """清除报警"""
        if parameter in self._debounce_counters:
            self._debounce_counters[parameter] = 0
        if parameter in self._active_alarms:
            del self._active_alarms[parameter]
            self.alarm_cleared.emit(parameter)

    def get_active_alarms(self) -> List[AlarmEvent]:
        """获取当前活跃报警"""
        return list(self._active_alarms.values())

    def get_alarm_history(self) -> List[AlarmEvent]:
        """获取报警历史"""
        return list(self._alarm_history)

    def reset(self) -> None:
        """重置报警管理器"""
        self._active_alarms.clear()
        self._alarm_history.clear()
        self._debounce_counters.clear()
        self._signal_loss_count = 0
