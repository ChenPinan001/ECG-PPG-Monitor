# ui/main_window.py - 主窗口

import os
from datetime import datetime

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QStatusBar, QMenuBar, QAction, QMessageBox,
    QFileDialog, QLabel, QSplitter,
)

from config.settings import (
    SAMPLE_RATE, EXPORT_DIR, COLOR_BG_DARK,
)
from core.serial_reader import SerialReader
from core.signal_simulator import SignalSimulator
from core.data_processor import DataProcessor
from ui.styles import get_stylesheet
from ui.ecg_widget import ECGWidget
from ui.ppg_widget import PPGWidget
from ui.vital_signs_panel import VitalSignsPanel
from ui.alarm_panel import AlarmPanel
from ui.control_panel import ControlPanel
from report.pdf_generator import PDFGenerator
from utils.helpers import timestamp_now, format_duration


class MainWindow(QMainWindow):
    """主窗口：编排所有 UI 组件和信号连接"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("多参数生命体征监护系统")
        self.setMinimumSize(1280, 800)
        self.resize(1400, 900)

        # 核心模块
        self._serial_reader = SerialReader()
        self._simulator = SignalSimulator()
        self._data_processor = DataProcessor()
        self._pdf_generator = PDFGenerator()

        # 监测计时
        self._monitor_start_time: float = 0.0
        self._elapsed_timer = QTimer(self)
        self._elapsed_timer.timeout.connect(self._update_elapsed)
        self._elapsed_timer.setInterval(1000)

        # 初始化 UI
        self._init_ui()
        self._apply_style()
        self._connect_signals()

    def _init_ui(self) -> None:
        """初始化 UI 布局"""
        # 菜单栏
        self._init_menu()

        # 中央控件
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(4)

        # ---- 波形区域 ----
        wave_splitter = QSplitter(Qt.Horizontal)

        self._ecg_widget = ECGWidget()
        wave_splitter.addWidget(self._ecg_widget)

        self._ppg_widget = PPGWidget()
        wave_splitter.addWidget(self._ppg_widget)

        wave_splitter.setSizes([700, 700])
        main_layout.addWidget(wave_splitter, stretch=3)

        # ---- 生命体征面板 ----
        self._vitals_panel = VitalSignsPanel()
        main_layout.addWidget(self._vitals_panel)

        # ---- 控制面板 + 报警面板 (左右布局) ----
        bottom_splitter = QSplitter(Qt.Horizontal)
        
        self._control_panel = ControlPanel()
        bottom_splitter.addWidget(self._control_panel)
        
        self._alarm_panel = AlarmPanel()
        self._alarm_panel.setMaximumWidth(340)
        self._alarm_panel.setMinimumWidth(260)
        bottom_splitter.addWidget(self._alarm_panel)
        
        bottom_splitter.setSizes([900, 320])
        bottom_splitter.setStretchFactor(0, 3)
        bottom_splitter.setStretchFactor(1, 1)
        main_layout.addWidget(bottom_splitter, stretch=2)

        # ---- 状态栏 ----
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

        self._status_connection = QLabel("未连接")
        self._status_connection.setStyleSheet("color: #ff6644; padding: 0 8px;")
        self._status_bar.addWidget(self._status_connection)

        self._status_samplerate = QLabel(f"采样率: {SAMPLE_RATE}Hz")
        self._status_samplerate.setStyleSheet("color: #888899; padding: 0 8px;")
        self._status_bar.addWidget(self._status_samplerate)

        self._status_elapsed = QLabel("运行时间: 00:00:00")
        self._status_elapsed.setStyleSheet("color: #888899; padding: 0 8px;")
        self._status_bar.addWidget(self._status_elapsed)

        self._status_data_count = QLabel("数据: 0")
        self._status_data_count.setStyleSheet("color: #888899; padding: 0 8px;")
        self._status_bar.addWidget(self._status_data_count)

    def _init_menu(self) -> None:
        """初始化菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        export_csv_action = QAction("导出 CSV...", self)
        export_csv_action.triggered.connect(self._export_csv)
        file_menu.addAction(export_csv_action)

        export_excel_action = QAction("导出 Excel...", self)
        export_excel_action.triggered.connect(self._export_excel)
        file_menu.addAction(export_excel_action)

        file_menu.addSeparator()

        export_pdf_action = QAction("生成 PDF 报告...", self)
        export_pdf_action.triggered.connect(self._export_pdf)
        file_menu.addAction(export_pdf_action)

        file_menu.addSeparator()

        exit_action = QAction("退出(&X)", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 设置菜单
        settings_menu = menubar.addMenu("设置(&S)")

        reset_action = QAction("重置所有模块", self)
        reset_action.triggered.connect(self._reset_all)
        settings_menu.addAction(reset_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _apply_style(self) -> None:
        """应用深色主题样式"""
        self.setStyleSheet(get_stylesheet())

    def _connect_signals(self) -> None:
        """连接所有信号/槽"""
        # 串口读取器
        self._serial_reader.data_received.connect(self._on_data_received)
        self._serial_reader.ppg_ir_received.connect(self._on_ppg_ir_received)
        self._serial_reader.connection_status.connect(self._on_connection_status)
        self._serial_reader.error_occurred.connect(self._on_error)
        self._serial_reader.text_received.connect(self._alarm_panel.add_data)

        # 信号模拟器
        self._simulator.data_received.connect(self._on_data_received)
        self._simulator.simulation_status.connect(self._on_simulation_status)

        # 数据处理器
        self._data_processor.vitals_updated.connect(self._on_vitals_updated)
        self._data_processor.ecg_filtered_ready.connect(self._ecg_widget.update_data)
        self._data_processor.ppg_filtered_ready.connect(self._ppg_widget.update_data)

        # 报警管理器
        self._data_processor.alarm_manager.alarm_triggered.connect(
            self._on_alarm_triggered
        )
        self._data_processor.alarm_manager.alarm_cleared.connect(
            self._on_alarm_cleared
        )

        # 控制面板
        self._control_panel.connect_requested.connect(self._on_connect)
        self._control_panel.disconnect_requested.connect(self._on_disconnect)
        self._control_panel.start_requested.connect(self._on_start_monitoring)
        self._control_panel.stop_requested.connect(self._on_stop_monitoring)
        self._control_panel.simulate_requested.connect(self._on_simulate)
        self._control_panel.export_csv_requested.connect(self._export_csv)
        self._control_panel.export_excel_requested.connect(self._export_excel)
        self._control_panel.export_pdf_requested.connect(self._export_pdf)
        self._control_panel.filter_hp_toggled.connect(
            self._data_processor.ecg_filter.set_hp_enabled
        )
        self._control_panel.filter_lp_toggled.connect(
            self._data_processor.ecg_filter.set_lp_enabled
        )
        self._control_panel.filter_ma_toggled.connect(
            self._data_processor.ecg_filter.set_ma_enabled
        )
        self._control_panel.filter_notch_toggled.connect(
            self._data_processor.ecg_filter.set_notch_enabled
        )
        self._control_panel.filter_ppg_hp_toggled.connect(
            self._data_processor.ppg_filter.set_hp_enabled
        )
        self._control_panel.filter_ppg_lp_toggled.connect(
            self._data_processor.ppg_filter.set_lp_enabled
        )
        self._control_panel.filter_ppg_ma_toggled.connect(
            self._data_processor.ppg_filter.set_ma_enabled
        )
        self._control_panel.filter_ppg_notch_toggled.connect(
            self._data_processor.ppg_filter.set_notch_enabled
        )
        
        # 模拟参数调节
        self._control_panel.heart_rate_changed.connect(self._simulator.set_heart_rate)
        self._control_panel.spo2_changed.connect(self._simulator.set_spo2)
        
        # 命令发送
        self._control_panel.send_command.connect(self._on_send_command)

    # ==================== 槽函数 ====================

    def _on_data_received(self, ecg: int, ppg: int, timestamp: str) -> None:
        """接收原始数据"""
        self._data_processor.push_raw_data(ecg, ppg, timestamp)

        # 更新数据计数
        count = self._data_processor.buffer.sample_count
        if count % 250 == 0:
            self._status_data_count.setText(f"数据: {count}")

    def _on_ppg_ir_received(self, ir: int, timestamp: str) -> None:
        """接收 PPG IR 数据"""
        self._data_processor.push_ppg_ir(ir, timestamp)

    def _on_connection_status(self, connected: bool, message: str) -> None:
        """连接状态更新"""
        self._control_panel.set_connected(connected)
        if connected:
            self._status_connection.setText(message)
            self._status_connection.setStyleSheet("color: #00cc66; padding: 0 8px;")
        else:
            self._status_connection.setText("未连接")
            self._status_connection.setStyleSheet("color: #ff6644; padding: 0 8px;")

    def _on_simulation_status(self, running: bool, message: str) -> None:
        """模拟状态更新"""
        self._control_panel.set_simulating(running)
        if running:
            self._status_connection.setText(message)
            self._status_connection.setStyleSheet("color: #00ccff; padding: 0 8px;")
        else:
            self._status_connection.setText("模拟已停止")
            self._status_connection.setStyleSheet("color: #ff6644; padding: 0 8px;")

    def _on_error(self, message: str) -> None:
        """错误处理"""
        self._status_connection.setText(f"错误: {message}")
        self._status_connection.setStyleSheet("color: #ff3344; padding: 0 8px;")

    def _on_vitals_updated(self, vitals: dict) -> None:
        """生命体征更新"""
        hr = vitals.get("heart_rate", 0)
        spo2 = vitals.get("spo2", 0)
        pr = vitals.get("pulse_rate", 0)

        self._vitals_panel.update_hr(hr)
        self._vitals_panel.update_spo2(spo2)
        self._vitals_panel.update_pr(pr)

    def _on_alarm_triggered(self, level: str, parameter: str,
                            value: float, timestamp: str) -> None:
        """报警触发"""
        self._alarm_panel.add_alarm(level, parameter, value, timestamp)

        # 更新生命体征面板报警状态
        if parameter == "heart_rate":
            self._vitals_panel.set_hr_alarm(True, level)
        elif parameter == "spo2":
            self._vitals_panel.set_spo2_alarm(True, level)
        elif parameter == "pulse_rate":
            self._vitals_panel.set_pr_alarm(True, level)

    def _on_alarm_cleared(self, parameter: str) -> None:
        """报警清除"""
        if parameter == "heart_rate":
            self._vitals_panel.set_hr_alarm(False)
        elif parameter == "spo2":
            self._vitals_panel.set_spo2_alarm(False)
        elif parameter == "pulse_rate":
            self._vitals_panel.set_pr_alarm(False)

    def _on_connect(self, port: str, baudrate: int) -> None:
        """连接串口"""
        print(f"[DEBUG] Connecting to {port} @ {baudrate}")
        self._serial_reader.set_port(port)
        self._serial_reader.set_baudrate(baudrate)
        if self._serial_reader.connect():
            print(f"[DEBUG] Connected successfully!")
            self._serial_reader.start()
        else:
            print(f"[DEBUG] Connection failed!")

    def _on_disconnect(self) -> None:
        """断开串口"""
        self._on_stop_monitoring()
        self._serial_reader.stop()
        self._serial_reader.disconnect()

    def _on_simulate(self, start: bool) -> None:
        """模拟模式切换"""
        if start:
            self._simulator.start()
            self._on_start_monitoring()
        else:
            self._simulator.stop()
            self._on_stop_monitoring()

    def _on_start_monitoring(self) -> None:
        """开始监测"""
        self._data_processor.start_processing()
        self._data_processor.start_recording()
        self._control_panel.set_monitoring(True)

        # 启动计时
        import time
        self._monitor_start_time = time.time()
        self._elapsed_timer.start()

    def _on_stop_monitoring(self) -> None:
        """停止监测"""
        self._data_processor.stop_processing()
        self._data_processor.stop_recording()
        self._control_panel.set_monitoring(False)
        self._elapsed_timer.stop()

    def _update_elapsed(self) -> None:
        """更新运行时间"""
        import time
        elapsed = time.time() - self._monitor_start_time
        self._status_elapsed.setText(f"运行时间: {format_duration(elapsed)}")

    def _export_csv(self) -> None:
        """导出 CSV"""
        records = self._data_processor.recorder.get_records()
        if not records:
            QMessageBox.information(self, "提示", "没有可导出的数据")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "导出 CSV", EXPORT_DIR, "CSV Files (*.csv)"
        )
        if filepath:
            import csv
            from config.settings import CSV_HEADERS
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
                writer.writeheader()
                writer.writerows(records)
            QMessageBox.information(self, "导出成功", f"已保存到:\n{filepath}")

    def _export_excel(self) -> None:
        """导出 Excel"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "导出 Excel", EXPORT_DIR, "Excel Files (*.xlsx)"
        )
        if filepath:
            result = self._data_processor.recorder.export_excel(filepath)
            if result:
                QMessageBox.information(self, "导出成功", f"已保存到:\n{result}")
            else:
                QMessageBox.warning(self, "导出失败", "没有可导出的数据")

    def _export_pdf(self) -> None:
        """生成 PDF 报告"""
        records = self._data_processor.recorder.get_records()
        alarms = self._data_processor.alarm_manager.get_alarm_history()

        if not records:
            QMessageBox.information(self, "提示", "没有可生成报告的数据")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "生成 PDF 报告", EXPORT_DIR, "PDF Files (*.pdf)"
        )
        if filepath:
            try:
                self._pdf_generator.generate(
                    filepath=filepath,
                    records=records,
                    alarms=alarms,
                )
                QMessageBox.information(self, "报告生成成功", f"已保存到:\n{filepath}")
            except Exception as e:
                QMessageBox.critical(self, "生成失败", f"PDF 生成错误:\n{str(e)}")

    def _reset_all(self) -> None:
        """重置所有模块"""
        self._simulator.stop()
        self._data_processor.reset()
        self._ecg_widget.clear()
        self._ppg_widget.clear()
        self._alarm_panel.clear_alarms()
        self._vitals_panel.update_hr(0)
        self._vitals_panel.update_spo2(0)
        self._vitals_panel.update_pr(0)
        self._status_data_count.setText("数据: 0")

    def _show_about(self) -> None:
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            "多参数生命体征监护系统 v1.0\n\n"
            "基于 Python + PyQt5 + PyQtGraph\n"
            "支持 ECG/PPG 实时监测、心率/血氧/脉搏率计算\n"
            "异常报警、数据存储与 PDF 报告生成\n"
            "内置信号模拟器，无需硬件即可演示"
        )

    def _on_send_command(self, cmd: str) -> None:
        """发送串口命令"""
        if self._serial_reader._serial and self._serial_reader._serial.is_open:
            print(f"[SEND] Sending: {repr(cmd)}")
            self._serial_reader.write(cmd)
            print(f"[SEND] Sent OK")
        else:
            print(f"[SEND] Serial port not open!")
            self._control_panel.append_cmd_log("未连接串口!")

    def closeEvent(self, event) -> None:
        """关闭窗口时清理资源"""
        self._simulator.stop()
        self._on_stop_monitoring()
        self._serial_reader.stop()
        self._serial_reader.disconnect()
        self._data_processor.stop_processing()
        event.accept()
