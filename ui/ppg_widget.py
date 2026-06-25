# ui/ppg_widget.py - PPG 波形实时绘制组件

from typing import List

import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from config.settings import (
    SAMPLE_RATE, DISPLAY_WINDOW, COLOR_PPG, COLOR_BG_DARK,
)


class PPGWidget(QWidget):
    """PPG 波形实时绘制组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._data: List[float] = []

    def _init_ui(self) -> None:
        """初始化 PyQtGraph 绘图"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setBackground(COLOR_BG_DARK)
        self._plot_widget.setLabel("left", "PPG", units="ADC")
        self._plot_widget.setLabel("bottom", "Time", units="s")
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self._plot_widget.setMenuEnabled(False)

        self._plot_widget.setXRange(0, DISPLAY_WINDOW)
        self._plot_widget.setYRange(-500, 500)

        # 坐标轴样式
        axis_pen = pg.mkPen(color="#444466", width=1)
        for axis_name in ("left", "bottom"):
            axis = self._plot_widget.getAxis(axis_name)
            axis.setPen(axis_pen)
            axis.setTextPen(pg.mkPen(color="#888899"))

        self._curve = self._plot_widget.plot(
            pen=pg.mkPen(color=COLOR_PPG, width=1.5),
            antialias=True,
        )

        layout.addWidget(self._plot_widget)

    def update_data(self, data: List[float]) -> None:
        """更新波形数据"""
        if not data:
            return

        self._data = list(data)
        display_samples = DISPLAY_WINDOW * SAMPLE_RATE

        if len(self._data) > display_samples:
            plot_data = self._data[-display_samples:]
        else:
            plot_data = self._data

        # 显示抽样: 每4个点取1个
        step = 4
        plot_data = plot_data[::step]

        # Y轴自适应: 根据数据范围动态调整
        if len(plot_data) > 0:
            data_min = np.min(plot_data)
            data_max = np.max(plot_data)
            data_range = data_max - data_min
            if data_range < 10:
                data_range = 10
            margin = data_range * 0.2
            self._plot_widget.setYRange(data_min - margin, data_max + margin)

        time_axis = np.linspace(0, len(plot_data) * step / SAMPLE_RATE, len(plot_data))
        self._curve.setData(time_axis, plot_data)

    def clear(self) -> None:
        """清除波形"""
        self._data.clear()
        self._curve.clear()
