# ui/ecg_widget.py - ECG 波形实时绘制组件

from typing import List, Optional

import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from config.settings import (
    SAMPLE_RATE, DISPLAY_WINDOW, COLOR_ECG, COLOR_BG_DARK, COLOR_GRID,
)


class ECGWidget(QWidget):
    """ECG 波形实时绘制组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._data: List[float] = []
        self._time_axis: List[float] = []
        self._sample_count = 0

    def _init_ui(self) -> None:
        """初始化 PyQtGraph 绘图"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建绘图控件
        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setBackground(COLOR_BG_DARK)
        self._plot_widget.setLabel("left", "ECG", units="μV")
        self._plot_widget.setLabel("bottom", "Time", units="s")
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)

        # 隐藏右键菜单
        self._plot_widget.setMenuEnabled(False)

        # 设置坐标轴范围
        self._plot_widget.setXRange(0, DISPLAY_WINDOW)
        self._plot_widget.setYRange(-2000, 2000)

        # 坐标轴样式
        self._style_axes()

        # 创建曲线
        self._curve = self._plot_widget.plot(
            pen=pg.mkPen(color=COLOR_ECG, width=1.5),
            antialias=True,
        )

        layout.addWidget(self._plot_widget)

    def _style_axes(self) -> None:
        """设置坐标轴样式"""
        axis_pen = pg.mkPen(color="#444466", width=1)
        for axis_name in ("left", "bottom"):
            axis = self._plot_widget.getAxis(axis_name)
            axis.setPen(axis_pen)
            axis.setTextPen(pg.mkPen(color="#888899"))

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

        # 显示抽样: 每2个点取1个 (200Hz→100Hz, Nyquist=50Hz, 保留ECG)
        step = 2
        plot_data = plot_data[::step]
        self._time_axis = np.linspace(0, len(plot_data) * step / SAMPLE_RATE, len(plot_data))
        self._curve.setData(self._time_axis, plot_data)

    def clear(self) -> None:
        """清除波形"""
        self._data.clear()
        self._curve.clear()
