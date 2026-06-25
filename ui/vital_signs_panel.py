# ui/vital_signs_panel.py - 生命体征数值面板

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame,
)

from config.settings import (
    COLOR_BG_PANEL, COLOR_BORDER, COLOR_HR, COLOR_SPO2, COLOR_PR,
    COLOR_ALARM_EMERGENCY, COLOR_ALARM_HIGH, COLOR_TEXT_SECONDARY,
)


class VitalSignCard(QFrame):
    """单个生命体征卡片"""

    def __init__(self, title: str, unit: str, color: str, parent=None):
        super().__init__(parent)
        self._color = color
        self._alarm_color = color
        self._is_alarming = False
        self._blink_state = False

        self.setStyleSheet(f"""
            VitalSignCard {{
                background-color: {COLOR_BG_PANEL};
                border: 1px solid {COLOR_BORDER};
                border-radius: 10px;
                padding: 8px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        # 标题
        self._title_label = QLabel(title)
        self._title_label.setAlignment(Qt.AlignCenter)
        self._title_label.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px;"
        )
        layout.addWidget(self._title_label)

        # 数值
        self._value_label = QLabel("--")
        self._value_label.setAlignment(Qt.AlignCenter)
        self._value_label.setStyleSheet(
            f"color: {color}; font-size: 36px; font-weight: bold;"
        )
        layout.addWidget(self._value_label)

        # 单位
        self._unit_label = QLabel(unit)
        self._unit_label.setAlignment(Qt.AlignCenter)
        self._unit_label.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;"
        )
        layout.addWidget(self._unit_label)

        # 闪烁定时器
        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._toggle_blink)
        self._blink_timer.setInterval(500)

    def set_value(self, value: float) -> None:
        """设置数值"""
        if value <= 0:
            self._value_label.setText("--")
            return
        self._value_label.setText(f"{value:.0f}")

    def set_alarm(self, active: bool, level: str = "") -> None:
        """设置报警状态"""
        if active and not self._is_alarming:
            self._is_alarming = True
            if level == "emergency":
                self._alarm_color = COLOR_ALARM_EMERGENCY
            elif level == "high":
                self._alarm_color = COLOR_ALARM_HIGH
            else:
                self._alarm_color = COLOR_ALARM_EMERGENCY
            self._blink_timer.start()
        elif not active and self._is_alarming:
            self._is_alarming = False
            self._blink_timer.stop()
            self._value_label.setStyleSheet(
                f"color: {self._color}; font-size: 36px; font-weight: bold;"
            )

    def _toggle_blink(self) -> None:
        """闪烁切换"""
        self._blink_state = not self._blink_state
        color = self._alarm_color if self._blink_state else self._color
        self._value_label.setStyleSheet(
            f"color: {color}; font-size: 36px; font-weight: bold;"
        )


class VitalSignsPanel(QWidget):
    """生命体征数值面板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        self._hr_card = VitalSignCard("❤ 心率", "BPM", COLOR_HR)
        self._spo2_card = VitalSignCard("SpO₂", "%", COLOR_SPO2)
        self._pr_card = VitalSignCard("脉搏率", "bpm", COLOR_PR)

        layout.addWidget(self._hr_card)
        layout.addWidget(self._spo2_card)
        layout.addWidget(self._pr_card)

    def update_hr(self, value: float) -> None:
        self._hr_card.set_value(value)

    def update_spo2(self, value: float) -> None:
        self._spo2_card.set_value(value)

    def update_pr(self, value: float) -> None:
        self._pr_card.set_value(value)

    def set_hr_alarm(self, active: bool, level: str = "") -> None:
        self._hr_card.set_alarm(active, level)

    def set_spo2_alarm(self, active: bool, level: str = "") -> None:
        self._spo2_card.set_alarm(active, level)

    def set_pr_alarm(self, active: bool, level: str = "") -> None:
        self._pr_card.set_alarm(active, level)
