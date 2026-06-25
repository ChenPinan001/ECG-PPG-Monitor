# ui/alarm_panel.py - 报警事件 + 串口数据面板

from typing import List

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QTextEdit,
)

from config.settings import (
    COLOR_BG_PANEL, COLOR_BORDER,
    COLOR_ALARM_EMERGENCY, COLOR_ALARM_HIGH, COLOR_ALARM_MEDIUM,
    COLOR_TEXT_SECONDARY,
)


class AlarmPanel(QWidget):
    """报警事件 + 串口数据面板"""

    alarm_count_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._alarm_count = 0

    def _init_ui(self) -> None:
        self.setStyleSheet("""
            AlarmPanel {
                background: #12121a;
                border: 1px solid #2a2a3a;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        # ---- 报警事件标题 ----
        alarm_header = QHBoxLayout()
        alarm_header.setSpacing(6)

        self._dot = QLabel("●")
        self._dot.setStyleSheet("color: #444; font-size: 10px;")
        alarm_header.addWidget(self._dot)

        alarm_title = QLabel("报警事件")
        alarm_title.setStyleSheet("color: #ff6644; font-size: 14px; font-weight: bold;")
        alarm_header.addWidget(alarm_title)

        self._count_label = QLabel("0")
        self._count_label.setStyleSheet("""
            color: #ffaa00; font-size: 11px; font-weight: bold;
            background: #1a1a25; border: 1px solid #3a3a4a;
            border-radius: 8px; padding: 1px 6px; min-width: 18px;
        """)
        self._count_label.setAlignment(Qt.AlignCenter)
        alarm_header.addWidget(self._count_label)

        alarm_header.addStretch()

        self._btn_clear = QPushButton("清除")
        self._btn_clear.setFixedSize(44, 22)
        self._btn_clear.setStyleSheet("""
            QPushButton {
                font-size: 11px; color: #888; background: #1a1a25;
                border: 1px solid #3a3a4a; border-radius: 3px; padding: 1px 6px;
            }
            QPushButton:hover { color: #ff6644; border-color: #ff6644; }
        """)
        self._btn_clear.clicked.connect(self.clear_alarms)
        alarm_header.addWidget(self._btn_clear)

        layout.addLayout(alarm_header)

        # ---- 报警列表 (小) ----
        self._alarm_list = QListWidget()
        self._alarm_list.setMaximumHeight(80)
        self._alarm_list.setStyleSheet("""
            QListWidget {
                background: #0a0a12; border: 1px solid #2a3a5a;
                border-radius: 6px; font-size: 12px; color: #cccccc; padding: 3px;
            }
            QListWidget::item { padding: 3px 6px; border-radius: 2px; margin: 1px 0; }
            QListWidget::item:selected { background: #1a2a3a; }
        """)
        self._alarm_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self._alarm_list)

        # ---- 分隔线 ----
        sep = QLabel("─" * 30)
        sep.setStyleSheet("color: #2a2a3a; font-size: 8px;")
        sep.setAlignment(Qt.AlignCenter)
        layout.addWidget(sep)

        # ---- 串口数据标题 ----
        data_header = QHBoxLayout()
        data_header.setSpacing(6)

        self._data_dot = QLabel("●")
        self._data_dot.setStyleSheet("color: #444; font-size: 10px;")
        data_header.addWidget(self._data_dot)

        data_title = QLabel("串口数据")
        data_title.setStyleSheet("color: #00ccff; font-size: 14px; font-weight: bold;")
        data_header.addWidget(data_title)

        self._data_count_label = QLabel("0")
        self._data_count_label.setStyleSheet("""
            color: #00ccff; font-size: 11px; font-weight: bold;
            background: #1a1a25; border: 1px solid #3a3a4a;
            border-radius: 8px; padding: 1px 6px; min-width: 18px;
        """)
        self._data_count_label.setAlignment(Qt.AlignCenter)
        data_header.addWidget(self._data_count_label)

        data_header.addStretch()

        self._btn_clear_data = QPushButton("清空")
        self._btn_clear_data.setFixedSize(44, 22)
        self._btn_clear_data.setStyleSheet("""
            QPushButton {
                font-size: 11px; color: #888; background: #1a1a25;
                border: 1px solid #3a3a4a; border-radius: 3px; padding: 1px 6px;
            }
            QPushButton:hover { color: #00ccff; border-color: #00ccff; }
        """)
        self._btn_clear_data.clicked.connect(self.clear_data)
        data_header.addWidget(self._btn_clear_data)

        layout.addLayout(data_header)

        # ---- 串口数据内容 ----
        self._data_text = QTextEdit()
        self._data_text.setReadOnly(True)
        self._data_text.setAlignment(Qt.AlignCenter)
        self._data_text.setStyleSheet("""
            QTextEdit {
                background: #0a0a12; border: 1px solid #2a3a5a;
                border-radius: 6px; font-size: 12px;
                font-family: 'Consolas', 'Courier New', monospace;
                color: #00ff88; padding: 4px;
            }
            QTextEdit QScrollBar:vertical {
                width: 6px; background: transparent;
            }
            QTextEdit QScrollBar::handle:vertical {
                background: #3a3a4a; border-radius: 3px; min-height: 20px;
            }
        """)
        # 手动设置居中占位文字
        self._placeholder_label = QLabel("等待串口数据...")
        self._placeholder_label.setAlignment(Qt.AlignCenter)
        self._placeholder_label.setStyleSheet("""
            color: #555; font-size: 16px; font-weight: bold;
            background: #0a0a12; border: 1px solid #2a3a5a;
            border-radius: 6px; padding: 40px 0;
        """)
        self._data_text.setVisible(False)
        layout.addWidget(self._placeholder_label)
        layout.addWidget(self._data_text)

        # ---- 底部状态 ----
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(4, 0, 4, 0)

        self._status_label = QLabel("● 正常")
        self._status_label.setStyleSheet("color: #00cc66; font-size: 10px;")
        status_layout.addWidget(self._status_label)

        status_layout.addStretch()

        self._time_label = QLabel("--:--:--")
        self._time_label.setStyleSheet("color: #555; font-size: 10px;")
        status_layout.addWidget(self._time_label)

        layout.addLayout(status_layout)

    def add_alarm(self, level: str, parameter: str, value: float,
                  timestamp: str) -> None:
        """添加报警事件"""
        param_names = {
            "heart_rate": "心率",
            "spo2": "血氧",
            "pulse_rate": "脉搏率",
            "signal_loss": "信号丢失",
        }
        param_display = param_names.get(parameter, parameter)

        level_styles = {
            "emergency": (COLOR_ALARM_EMERGENCY, "紧急"),
            "high": (COLOR_ALARM_HIGH, "高"),
            "medium": (COLOR_ALARM_MEDIUM, "中"),
        }
        color, level_display = level_styles.get(level, (COLOR_ALARM_MEDIUM, "中"))

        text = f"[{level_display}] {timestamp}  {param_display}: {value:.0f}"

        item = QListWidgetItem(text)
        item.setForeground(Qt.GlobalColor.white)
        from PyQt5.QtGui import QColor
        bg_color = QColor(color)
        bg_color.setAlpha(50)
        item.setBackground(bg_color)

        self._alarm_list.insertItem(0, item)
        self._alarm_count += 1
        self._count_label.setText(str(self._alarm_count))

        if self._alarm_count > 0:
            self._dot.setStyleSheet("color: #ff4444; font-size: 10px;")
            self._status_label.setText(f"● 报警中 ({self._alarm_count})")
            self._status_label.setStyleSheet("color: #ff6644; font-size: 10px;")

        self.alarm_count_changed.emit(self._alarm_count)

        while self._alarm_list.count() > 50:
            self._alarm_list.takeItem(self._alarm_list.count() - 1)

    def clear_alarms(self) -> None:
        """清除所有报警"""
        self._alarm_list.clear()
        self._alarm_count = 0
        self._count_label.setText("0")
        self._dot.setStyleSheet("color: #444; font-size: 10px;")
        self._status_label.setText("● 正常")
        self._status_label.setStyleSheet("color: #00cc66; font-size: 10px;")
        self.alarm_count_changed.emit(0)

    def add_data(self, text: str) -> None:
        """添加串口数据"""
        self._placeholder_label.setVisible(False)
        self._data_text.setVisible(True)
        self._data_text.append(text)
        self._data_count_label.setText(str(self._data_text.document().blockCount()))
        self._data_dot.setStyleSheet("color: #00cc66; font-size: 10px;")
        scrollbar = self._data_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_data(self) -> None:
        """清空串口数据"""
        self._data_text.clear()
        self._data_text.setVisible(False)
        self._placeholder_label.setVisible(True)
        self._data_count_label.setText("0")
        self._data_dot.setStyleSheet("color: #444; font-size: 10px;")

    @property
    def alarm_count(self) -> int:
        return self._alarm_count
