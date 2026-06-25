# ui/control_panel.py - 控制面板

from typing import List, Tuple

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QComboBox, QCheckBox, QGroupBox, QSlider,
    QLineEdit, QTextEdit,
)

from config.settings import (
    COLOR_BG_PANEL, COLOR_BORDER, COLOR_TEXT_SECONDARY,
)


class ControlPanel(QWidget):
    """控制面板：串口连接、启停、滤波开关、导出"""

    connect_requested = pyqtSignal(str, int)    # port, baudrate
    disconnect_requested = pyqtSignal()
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    simulate_requested = pyqtSignal(bool)        # start/stop simulation
    export_csv_requested = pyqtSignal()
    export_excel_requested = pyqtSignal()
    export_pdf_requested = pyqtSignal()
    filter_hp_toggled = pyqtSignal(bool)
    filter_lp_toggled = pyqtSignal(bool)
    filter_ma_toggled = pyqtSignal(bool)
    filter_notch_toggled = pyqtSignal(bool)
    filter_ppg_hp_toggled = pyqtSignal(bool)
    filter_ppg_lp_toggled = pyqtSignal(bool)
    filter_ppg_ma_toggled = pyqtSignal(bool)
    filter_ppg_notch_toggled = pyqtSignal(bool)
    heart_rate_changed = pyqtSignal(float)       # HR BPM
    spo2_changed = pyqtSignal(float)             # SpO2 %
    send_command = pyqtSignal(str)               # 发送串口命令

    def __init__(self, parent=None):
        super().__init__(parent)
        self._connected = False
        self._simulating = False
        self._monitoring = False
        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(6)

        # ---- 串口设置 (标签+下拉框横排) ----
        serial_group = QGroupBox("串口设置")
        serial_group.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                border: 1px solid #2a2a3a;
                border-radius: 6px;
                margin-top: 6px;
                padding: 10px 8px 6px 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #aaaaaa;
            }
        """)
        serial_layout = QHBoxLayout(serial_group)
        serial_layout.setSpacing(20)
        serial_layout.setContentsMargins(12, 8, 12, 8)

        combo_style = """
            QComboBox {
                font-size: 12px;
                padding: 5px 8px;
                background: #1a1a25;
                border: 1px solid #3a3a4a;
                border-radius: 4px;
                color: #e0e0e0;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #888;
                margin-right: 6px;
            }
            QComboBox QAbstractItemView {
                background: #1a1a25;
                border: 1px solid #3a3a4a;
                color: #e0e0e0;
                selection-background-color: #2a4a6a;
            }
        """
        label_style = "color: #888899; font-size: 12px;"

        # 串口选择
        port_layout = QVBoxLayout()
        port_layout.setSpacing(4)
        lbl_port = QLabel("串口选择")
        lbl_port.setStyleSheet(label_style)
        port_layout.addWidget(lbl_port)
        self._port_combo = QComboBox()
        self._port_combo.setStyleSheet(combo_style)
        self._port_combo.setMinimumWidth(200)
        port_layout.addWidget(self._port_combo)
        serial_layout.addLayout(port_layout)

        # 波特率
        baud_layout = QVBoxLayout()
        baud_layout.setSpacing(4)
        lbl_baud = QLabel("波特率")
        lbl_baud.setStyleSheet(label_style)
        baud_layout.addWidget(lbl_baud)
        self._baudrate_combo = QComboBox()
        self._baudrate_combo.setStyleSheet(combo_style)
        self._baudrate_combo.setMinimumWidth(120)
        self._baudrate_combo.addItems([
            "9600", "19200", "38400", "57600", "115200", "230400", "460800"
        ])
        self._baudrate_combo.setCurrentText("115200")
        baud_layout.addWidget(self._baudrate_combo)
        serial_layout.addLayout(baud_layout)

        # 停止位
        stop_layout = QVBoxLayout()
        stop_layout.setSpacing(4)
        lbl_stop = QLabel("停止位")
        lbl_stop.setStyleSheet(label_style)
        stop_layout.addWidget(lbl_stop)
        self._stop_combo = QComboBox()
        self._stop_combo.setStyleSheet(combo_style)
        self._stop_combo.setMinimumWidth(80)
        self._stop_combo.addItems(["1", "1.5", "2"])
        self._stop_combo.setCurrentText("1")
        stop_layout.addWidget(self._stop_combo)
        serial_layout.addLayout(stop_layout)

        # 数据位
        data_layout = QVBoxLayout()
        data_layout.setSpacing(4)
        lbl_data = QLabel("数据位")
        lbl_data.setStyleSheet(label_style)
        data_layout.addWidget(lbl_data)
        self._data_combo = QComboBox()
        self._data_combo.setStyleSheet(combo_style)
        self._data_combo.setMinimumWidth(80)
        self._data_combo.addItems(["7", "8"])
        self._data_combo.setCurrentText("8")
        data_layout.addWidget(self._data_combo)
        serial_layout.addLayout(data_layout)

        # 校验位
        parity_layout = QVBoxLayout()
        parity_layout.setSpacing(4)
        lbl_parity = QLabel("校验位")
        lbl_parity.setStyleSheet(label_style)
        parity_layout.addWidget(lbl_parity)
        self._parity_combo = QComboBox()
        self._parity_combo.setStyleSheet(combo_style)
        self._parity_combo.setMinimumWidth(100)
        self._parity_combo.addItems(["None", "Even", "Odd"])
        self._parity_combo.setCurrentText("None")
        parity_layout.addWidget(self._parity_combo)
        serial_layout.addLayout(parity_layout)

        # 串口操作按钮
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(4)
        lbl_action = QLabel("串口操作")
        lbl_action.setStyleSheet(label_style)
        btn_layout.addWidget(lbl_action)
        
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self._btn_refresh = QPushButton("刷新")
        self._btn_refresh.setFixedHeight(30)
        self._btn_refresh.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                background: #1e1e35;
                color: #00ccff;
                border: 1px solid #3a3a5a;
                border-radius: 4px;
                padding: 4px 14px;
            }
            QPushButton:hover { background: #2a2a4a; border-color: #00ccff; }
        """)
        self._btn_refresh.clicked.connect(self._refresh_ports)
        btn_row.addWidget(self._btn_refresh)

        self._btn_connect = QPushButton("打开串口")
        self._btn_connect.setFixedHeight(30)
        self._btn_connect.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                background: #006633;
                color: #00ff88;
                border: 1px solid #00aa55;
                border-radius: 4px;
                padding: 4px 16px;
            }
            QPushButton:hover { background: #008844; }
            QPushButton:pressed { background: #004422; }
        """)
        self._btn_connect.clicked.connect(self._on_connect)
        btn_row.addWidget(self._btn_connect)

        self._btn_disconnect = QPushButton("关闭串口")
        self._btn_disconnect.setFixedHeight(30)
        self._btn_disconnect.setEnabled(False)
        self._btn_disconnect.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                background: #3a1a1a;
                color: #ff6644;
                border: 1px solid #5a2a2a;
                border-radius: 4px;
                padding: 4px 16px;
            }
            QPushButton:hover { background: #4a2a2a; }
            QPushButton:pressed { background: #2a0a0a; }
            QPushButton:disabled { background: #1a1a1a; color: #555; border-color: #333; }
        """)
        self._btn_disconnect.clicked.connect(self._on_disconnect)
        btn_row.addWidget(self._btn_disconnect)
        
        btn_layout.addLayout(btn_row)
        serial_layout.addLayout(btn_layout)

        serial_layout.addStretch(1)
        main_layout.addWidget(serial_group)

        # ---- 控制按钮 + 导出按钮 (同一行) ----
        btn_row_layout = QHBoxLayout()
        btn_row_layout.setSpacing(8)

        # 监测控制
        self._btn_start = QPushButton("▶ 开始监测")
        self._btn_start.setEnabled(False)
        self._btn_start.setStyleSheet(self._btn_style("#00aa55", "#00ff88"))
        self._btn_start.clicked.connect(self._on_start)
        btn_row_layout.addWidget(self._btn_start)

        self._btn_stop = QPushButton("■ 停止监测")
        self._btn_stop.setEnabled(False)
        self._btn_stop.setStyleSheet(self._btn_style("#aa3333", "#ff6644"))
        self._btn_stop.clicked.connect(self._on_stop)
        btn_row_layout.addWidget(self._btn_stop)

        btn_row_layout.addSpacing(12)

        # 模拟控制
        self._btn_simulate = QPushButton("▶ 模拟模式")
        self._btn_simulate.setEnabled(False)
        self._btn_simulate.setStyleSheet(self._btn_style("#0066aa", "#00ccff"))
        self._btn_simulate.setToolTip("启动 ECG/PPG 信号模拟器")
        self._btn_simulate.clicked.connect(self._on_simulate)
        btn_row_layout.addWidget(self._btn_simulate)

        self._btn_sim_stop = QPushButton("■ 停止模拟")
        self._btn_sim_stop.setEnabled(False)
        self._btn_sim_stop.setStyleSheet(self._btn_style("#aa3333", "#ff6644"))
        self._btn_sim_stop.clicked.connect(self._on_sim_stop)
        btn_row_layout.addWidget(self._btn_sim_stop)

        btn_row_layout.addSpacing(16)

        # 分隔线
        sep = QLabel("|")
        sep.setStyleSheet("color: #3a3a4a; font-size: 16px; padding: 0 4px;")
        btn_row_layout.addWidget(sep)

        btn_row_layout.addSpacing(8)

        # 导出按钮
        self._btn_export_csv = QPushButton("导出 CSV")
        self._btn_export_csv.clicked.connect(self.export_csv_requested.emit)
        btn_row_layout.addWidget(self._btn_export_csv)

        self._btn_export_excel = QPushButton("导出 Excel")
        self._btn_export_excel.clicked.connect(self.export_excel_requested.emit)
        btn_row_layout.addWidget(self._btn_export_excel)

        self._btn_export_pdf = QPushButton("生成报告 (PDF)")
        self._btn_export_pdf.clicked.connect(self.export_pdf_requested.emit)
        btn_row_layout.addWidget(self._btn_export_pdf)

        btn_row_layout.addStretch()
        main_layout.addLayout(btn_row_layout)

        # ---- 三个Group同一行水平对齐 ----
        from PyQt5.QtWidgets import QGridLayout

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(8)

        # 滤波设置
        filter_group = QGroupBox("滤波设置")
        filter_group.setStyleSheet("""
            QGroupBox { font-size: 12px; font-weight: bold; border: 1px solid #2a2a3a; border-radius: 6px; padding: 8px 6px 4px 6px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 6px; color: #aaaaaa; }
            QCheckBox { font-size: 11px; color: #cccccc; spacing: 4px; }
            QCheckBox::indicator { width: 12px; height: 12px; }
        """)
        filter_grid = QGridLayout(filter_group)
        filter_grid.setSpacing(6)
        filter_grid.setContentsMargins(6, 2, 6, 2)
        filter_grid.setVerticalSpacing(6)

        lbl_ecg = QLabel("ECG:")
        lbl_ecg.setStyleSheet("color: #00ccff; font-size: 11px; font-weight: bold;")
        filter_grid.addWidget(lbl_ecg, 0, 0)
        lbl_ppg = QLabel("PPG:")
        lbl_ppg.setStyleSheet("color: #00ff88; font-size: 11px; font-weight: bold;")
        filter_grid.addWidget(lbl_ppg, 1, 0)

        self._chk_hp = QCheckBox("高通"); self._chk_hp.setChecked(False)
        self._chk_hp.toggled.connect(self.filter_hp_toggled.emit)
        filter_grid.addWidget(self._chk_hp, 0, 1)
        self._chk_lp = QCheckBox("低通"); self._chk_lp.setChecked(False)
        self._chk_lp.toggled.connect(self.filter_lp_toggled.emit)
        filter_grid.addWidget(self._chk_lp, 0, 2)
        self._chk_ma = QCheckBox("移动平均"); self._chk_ma.setChecked(False)
        self._chk_ma.toggled.connect(self.filter_ma_toggled.emit)
        filter_grid.addWidget(self._chk_ma, 0, 3)
        self._chk_notch = QCheckBox("50Hz陷波"); self._chk_notch.setChecked(True)
        self._chk_notch.toggled.connect(self.filter_notch_toggled.emit)
        filter_grid.addWidget(self._chk_notch, 0, 4)

        self._chk_ppg_hp = QCheckBox("高通"); self._chk_ppg_hp.setChecked(True)
        self._chk_ppg_hp.toggled.connect(self.filter_ppg_hp_toggled.emit)
        filter_grid.addWidget(self._chk_ppg_hp, 1, 1)
        self._chk_ppg_lp = QCheckBox("低通"); self._chk_ppg_lp.setChecked(True)
        self._chk_ppg_lp.toggled.connect(self.filter_ppg_lp_toggled.emit)
        filter_grid.addWidget(self._chk_ppg_lp, 1, 2)
        self._chk_ppg_ma = QCheckBox("移动平均"); self._chk_ppg_ma.setChecked(True)
        self._chk_ppg_ma.toggled.connect(self.filter_ppg_ma_toggled.emit)
        filter_grid.addWidget(self._chk_ppg_ma, 1, 3)
        self._chk_ppg_notch = QCheckBox("50Hz陷波"); self._chk_ppg_notch.setChecked(True)
        self._chk_ppg_notch.toggled.connect(self.filter_ppg_notch_toggled.emit)
        filter_grid.addWidget(self._chk_ppg_notch, 1, 4)

        bottom_row.addWidget(filter_group, stretch=2)

        # 模拟心率
        hr_group = QGroupBox("模拟心率 (BPM)")
        hr_group.setStyleSheet("""
            QGroupBox { font-size: 12px; font-weight: bold; border: 1px solid #2a2a3a; border-radius: 6px; padding: 8px 8px 4px 8px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 6px; color: #aaaaaa; }
        """)
        hr_layout = QVBoxLayout(hr_group)
        hr_layout.setSpacing(2)
        self._hr_slider = QSlider(Qt.Horizontal)
        self._hr_slider.setRange(30, 220); self._hr_slider.setValue(72)
        self._hr_slider.setTickPosition(QSlider.TicksBelow); self._hr_slider.setTickInterval(10)
        self._hr_slider.valueChanged.connect(self._on_hr_changed)
        hr_layout.addWidget(self._hr_slider)
        self._hr_label = QLabel("72 BPM")
        self._hr_label.setAlignment(Qt.AlignCenter)
        self._hr_label.setStyleSheet("color: #888899; font-weight: bold; font-size: 11px;")
        hr_layout.addWidget(self._hr_label)
        bottom_row.addWidget(hr_group, stretch=2)

        # 模拟血氧
        spo2_group = QGroupBox("模拟血氧 (%)")
        spo2_group.setStyleSheet("""
            QGroupBox { font-size: 12px; font-weight: bold; border: 1px solid #2a2a3a; border-radius: 6px; padding: 8px 8px 4px 8px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 6px; color: #aaaaaa; }
        """)
        spo2_layout = QVBoxLayout(spo2_group)
        spo2_layout.setSpacing(2)
        self._spo2_slider = QSlider(Qt.Horizontal)
        self._spo2_slider.setRange(70, 100); self._spo2_slider.setValue(97)
        self._spo2_slider.setTickPosition(QSlider.TicksBelow); self._spo2_slider.setTickInterval(5)
        self._spo2_slider.valueChanged.connect(self._on_spo2_changed)
        spo2_layout.addWidget(self._spo2_slider)
        self._spo2_label = QLabel("97 %")
        self._spo2_label.setAlignment(Qt.AlignCenter)
        self._spo2_label.setStyleSheet("color: #888899; font-weight: bold; font-size: 11px;")
        spo2_layout.addWidget(self._spo2_label)
        bottom_row.addWidget(spo2_group, stretch=2)

        main_layout.addLayout(bottom_row)

        # ---- 命令发送区 ----
        cmd_group = QGroupBox("串口命令")
        cmd_group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                border: 1px solid #2a2a3a;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }
        """)
        cmd_layout = QVBoxLayout(cmd_group)
        cmd_layout.setSpacing(8)

        # 第一行: 下拉框 + 发送按钮
        cmd_input_layout = QHBoxLayout()
        cmd_input_layout.setSpacing(8)
        
        self._cmd_combo = QComboBox()
        self._cmd_combo.setEditable(True)
        self._cmd_combo.setMinimumWidth(280)
        self._cmd_combo.setStyleSheet("""
            QComboBox {
                font-size: 13px;
                padding: 6px 10px;
                background: #1a1a25;
                border: 1px solid #3a3a4a;
                border-radius: 4px;
                color: #e0e0e0;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #888;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background: #1a1a25;
                border: 1px solid #3a3a4a;
                color: #e0e0e0;
                selection-background-color: #2a4a6a;
                font-size: 13px;
            }
        """)
        # 分组显示
        self._cmd_combo.addItems([
            "【增益设置】",
            "G1  =  增益 ×1",
            "G2  =  增益 ×2",
            "G4  =  增益 ×4",
            "G8  =  增益 ×8",
            "G16 =  增益 ×16",
            "G32 =  增益 ×32",
            "【增益调节】",
            "G+  =  增益 +1档",
            "G-  =  增益 -1档",
            "GA  =  自动增益",
            "【系统查询】",
            "?   =  查询状态",
            "H   =  显示帮助",
        ])
        cmd_input_layout.addWidget(self._cmd_combo, stretch=1)
        
        self._btn_send_cmd = QPushButton("发 送")
        self._btn_send_cmd.setFixedWidth(70)
        self._btn_send_cmd.setStyleSheet("""
            QPushButton {
                font-size: 13px;
                font-weight: bold;
                padding: 6px 12px;
                background: #0066cc;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { background: #0088ff; }
            QPushButton:pressed { background: #0055aa; }
        """)
        self._btn_send_cmd.clicked.connect(self._on_send_command)
        cmd_input_layout.addWidget(self._btn_send_cmd)
        
        cmd_layout.addLayout(cmd_input_layout)

        # 第二行: 快捷按钮组
        cmd_btn_layout = QHBoxLayout()
        cmd_btn_layout.setSpacing(0)
        cmd_btn_layout.setContentsMargins(8, 0, 0, 0)

        # 增益快捷键
        gain_label = QLabel("增益:")
        gain_label.setStyleSheet("color: #888; font-size: 12px; padding-right: 8px;")
        cmd_btn_layout.addWidget(gain_label)

        for text, cmd in [("×1", "G1"), ("×2", "G2"), ("×4", "G4"), 
                          ("×8", "G8"), ("×16", "G16"), ("×32", "G32")]:
            btn = QPushButton(text)
            btn.setFixedSize(50, 30)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 13px;
                    font-weight: bold;
                    background: #1e1e35;
                    color: #00ccff;
                    border: 1px solid #3a3a5a;
                    border-radius: 4px;
                    margin: 0 5px;
                    padding: 2px 4px;
                }
                QPushButton:hover { background: #2a2a4a; border-color: #00ccff; }
                QPushButton:pressed { background: #0066aa; color: white; }
            """)
            btn.clicked.connect(lambda _, c=cmd: self._send_cmd(c))
            cmd_btn_layout.addWidget(btn)

        cmd_btn_layout.addSpacing(24)

        # 调节按钮
        adj_label = QLabel("调节:")
        adj_label.setStyleSheet("color: #888; font-size: 12px; padding-right: 8px;")
        cmd_btn_layout.addWidget(adj_label)

        for text, cmd in [("增益 +", "G+"), ("增益 -", "G-"), ("自动", "GA")]:
            btn = QPushButton(text)
            btn.setFixedSize(66, 30)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 13px;
                    background: #1e1e35;
                    color: #00ff88;
                    border: 1px solid #3a3a5a;
                    border-radius: 4px;
                    margin: 0 5px;
                    padding: 2px 4px;
                }
                QPushButton:hover { background: #2a2a4a; border-color: #00ff88; }
                QPushButton:pressed { background: #006633; color: white; }
            """)
            btn.clicked.connect(lambda _, c=cmd: self._send_cmd(c))
            cmd_btn_layout.addWidget(btn)

        cmd_btn_layout.addSpacing(24)

        # 查询按钮
        for text, cmd in [("查询", "?"), ("帮助", "H")]:
            btn = QPushButton(text)
            btn.setFixedSize(54, 30)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 13px;
                    background: #1e1e35;
                    color: #ffaa00;
                    border: 1px solid #3a3a5a;
                    border-radius: 4px;
                    margin: 0 5px;
                    padding: 2px 4px;
                }
                QPushButton:hover { background: #2a2a4a; border-color: #ffaa00; }
                QPushButton:pressed { background: #664400; color: white; }
            """)
            btn.clicked.connect(lambda _, c=cmd: self._send_cmd(c))
            cmd_btn_layout.addWidget(btn)

        cmd_btn_layout.addStretch()
        cmd_layout.addLayout(cmd_btn_layout)

        # 第三行: 命令日志
        log_label = QLabel("通信日志:")
        log_label.setStyleSheet("color: #666; font-size: 11px; margin-top: 4px;")
        cmd_layout.addWidget(log_label)

        self._cmd_log = QTextEdit()
        self._cmd_log.setMaximumHeight(70)
        self._cmd_log.setReadOnly(True)
        self._cmd_log.setStyleSheet("""
            QTextEdit {
                background: #0d0d15;
                color: #00ff88;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid #2a2a3a;
                border-radius: 4px;
                padding: 4px 8px;
            }
        """)
        self._cmd_log.setPlaceholderText("等待连接...")
        cmd_layout.addWidget(self._cmd_log)

        main_layout.addWidget(cmd_group)

        # 初始刷新串口列表
        self._refresh_ports()

    @staticmethod
    def _btn_style(bg_color: str, text_color: str) -> str:
        """生成按钮样式"""
        return f"""
            QPushButton {{
                font-size: 12px;
                font-weight: bold;
                background: {bg_color};
                color: {text_color};
                border: 1px solid {text_color};
                border-radius: 4px;
                padding: 6px 14px;
            }}
            QPushButton:hover {{ opacity: 0.85; }}
            QPushButton:pressed {{ opacity: 0.7; }}
            QPushButton:disabled {{ background: #1a1a1a; color: #444; border-color: #333; }}
        """

    def _refresh_ports(self) -> None:
        """刷新串口列表"""
        from core.serial_reader import SerialReader
        self._port_combo.clear()
        ports = SerialReader.list_ports()
        for device, desc in ports:
            self._port_combo.addItem(f"{device} - {desc}", device)
        if not ports:
            self._port_combo.addItem("无可用串口")

    def _on_connect(self) -> None:
        """连接按钮点击"""
        port = self._port_combo.currentData()
        baudrate = self._baudrate_combo.currentText()
        print(f"[DEBUG] Port: {port}, Baudrate: {baudrate}")
        if port:
            self.connect_requested.emit(port, int(baudrate))
        else:
            print("[DEBUG] No port selected!")

    def _on_disconnect(self) -> None:
        """断开按钮点击"""
        self.disconnect_requested.emit()

    def _on_start(self) -> None:
        """开始监测"""
        self.start_requested.emit()

    def _on_stop(self) -> None:
        """停止监测"""
        self.stop_requested.emit()

    def _on_simulate(self) -> None:
        """开始模拟"""
        self.simulate_requested.emit(True)

    def _on_sim_stop(self) -> None:
        """停止模拟"""
        self.simulate_requested.emit(False)

    def _on_hr_changed(self, value: int) -> None:
        """心率滑块变化"""
        self._hr_label.setText(f"{value} BPM")
        self.heart_rate_changed.emit(float(value))

    def _on_spo2_changed(self, value: int) -> None:
        """血氧滑块变化"""
        self._spo2_label.setText(f"{value} %")
        self.spo2_changed.emit(float(value))

    def set_connected(self, connected: bool) -> None:
        """更新连接状态"""
        self._connected = connected
        self._btn_disconnect.setEnabled(connected and not self._simulating)
        self._btn_start.setEnabled(connected and not self._simulating)
        self._btn_simulate.setEnabled(not self._simulating)
        self._port_combo.setEnabled(not connected and not self._simulating)
        self._baudrate_combo.setEnabled(not connected and not self._simulating)
        
        if connected:
            # 已连接: 打开串口变灰, 关闭串口可用
            self._btn_connect.setEnabled(False)
            self._btn_connect.setStyleSheet("""
                QPushButton {
                    font-size: 12px;
                    font-weight: bold;
                    background: #1a1a1a;
                    color: #555;
                    border: 1px solid #333;
                    border-radius: 4px;
                    padding: 4px 16px;
                }
            """)
            self._btn_disconnect.setStyleSheet("""
                QPushButton {
                    font-size: 12px;
                    font-weight: bold;
                    background: #3a1a1a;
                    color: #ff6644;
                    border: 1px solid #5a2a2a;
                    border-radius: 4px;
                    padding: 4px 16px;
                }
                QPushButton:hover { background: #4a2a2a; }
                QPushButton:pressed { background: #2a0a0a; }
                QPushButton:disabled { background: #1a1a1a; color: #555; border-color: #333; }
            """)
        else:
            # 未连接: 打开串口可用, 关闭串口变灰
            self._btn_connect.setEnabled(True)
            self._btn_connect.setStyleSheet("""
                QPushButton {
                    font-size: 12px;
                    font-weight: bold;
                    background: #006633;
                    color: #00ff88;
                    border: 1px solid #00aa55;
                    border-radius: 4px;
                    padding: 4px 16px;
                }
                QPushButton:hover { background: #008844; }
                QPushButton:pressed { background: #004422; }
            """)
            self._btn_disconnect.setStyleSheet("""
                QPushButton {
                    font-size: 12px;
                    background: #1a1a1a;
                    color: #555;
                    border: 1px solid #333;
                    border-radius: 4px;
                    padding: 4px 16px;
                }
                QPushButton:disabled { background: #1a1a1a; color: #555; border-color: #333; }
            """)

    def set_monitoring(self, monitoring: bool) -> None:
        """更新监测状态"""
        self._monitoring = monitoring
        if monitoring:
            self._btn_start.setEnabled(False)
            self._btn_start.setStyleSheet(self._btn_style("#1a1a1a", "#444"))
            self._btn_stop.setEnabled(True)
            self._btn_stop.setStyleSheet(self._btn_style("#aa3333", "#ff6644"))
        else:
            self._btn_start.setEnabled(self._connected and not self._simulating)
            self._btn_start.setStyleSheet(self._btn_style("#00aa55", "#00ff88") if self._connected and not self._simulating else self._btn_style("#1a1a1a", "#444"))
            self._btn_stop.setEnabled(False)
            self._btn_stop.setStyleSheet(self._btn_style("#1a1a1a", "#444"))

    def set_simulating(self, simulating: bool) -> None:
        """更新模拟状态"""
        self._simulating = simulating
        if simulating:
            self._btn_simulate.setEnabled(False)
            self._btn_simulate.setStyleSheet(self._btn_style("#1a1a1a", "#444"))
            self._btn_sim_stop.setEnabled(True)
            self._btn_sim_stop.setStyleSheet(self._btn_style("#aa3333", "#ff6644"))
            self._btn_connect.setEnabled(False)
            self._btn_connect.setStyleSheet(self._btn_style("#1a1a1a", "#444"))
            self._btn_disconnect.setEnabled(False)
            self._btn_disconnect.setStyleSheet(self._btn_style("#1a1a1a", "#444"))
            self._port_combo.setEnabled(False)
            self._baudrate_combo.setEnabled(False)
        else:
            self._btn_simulate.setEnabled(not self._connected)
            self._btn_simulate.setStyleSheet(self._btn_style("#0066aa", "#00ccff") if not self._connected else self._btn_style("#1a1a1a", "#444"))
            self._btn_sim_stop.setEnabled(False)
            self._btn_sim_stop.setStyleSheet(self._btn_style("#1a1a1a", "#444"))
            if not self._connected:
                self._btn_connect.setEnabled(True)
                self._btn_connect.setStyleSheet(self._btn_style("#006633", "#00ff88"))
            self._port_combo.setEnabled(not self._connected)
            self._baudrate_combo.setEnabled(not self._connected)

    def _on_send_command(self) -> None:
        """发送选中的命令"""
        text = self._cmd_combo.currentText().strip()
        if not text:
            return
        
        # 从下拉选项中提取命令码 (如 "G8  - 增益×8" → "G8")
        if " - " in text:
            cmd = text.split(" - ")[0].strip()
        elif text.startswith("---"):
            return  # 分隔行，不发送
        else:
            cmd = text  # 用户手动输入的
        
        if cmd:
            self._send_cmd(cmd)

    def _send_cmd(self, cmd: str) -> None:
        """发送命令并记录日志"""
        self._cmd_log.append(f"> {cmd}")
        self.send_command.emit(cmd + "\r\n")

    def append_cmd_log(self, text: str) -> None:
        """追加命令响应日志"""
        self._cmd_log.append(f"< {text}")
        # 自动滚动到底部
        scrollbar = self._cmd_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
