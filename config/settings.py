# config/settings.py - 全局配置参数

from dataclasses import dataclass, field
from typing import List, Tuple

# ==================== 串口配置 ====================
SERIAL_PORT = "COM3"
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 0.01
SERIAL_BYTESIZE = 8
SERIAL_PARITY = "N"
SERIAL_STOPBITS = 1

# 数据帧协议
FRAME_HEADER = bytes([0xAA, 0x55])
FRAME_LENGTH = 12
FRAME_TYPE_ECG_PPG = 0x01
FRAME_TYPE_ECG_ONLY = 0x02
FRAME_TYPE_PPG_ONLY = 0x03
FRAME_TYPE_PPG_RED_IR = 0x04

# ==================== 采样配置 ====================
SAMPLE_RATE = 200          # Hz
DISPLAY_WINDOW = 5         # 显示窗口秒数
BUFFER_SIZE = SAMPLE_RATE * 30  # 环形缓冲区大小（30秒）

# ==================== ECG 滤波参数 ====================
ECG_HP_CUTOFF = 0.5        # 高通截止频率 Hz
ECG_HP_ORDER = 2           # 高通阶数
ECG_LP_CUTOFF = 40.0       # 低通截止频率 Hz
ECG_LP_ORDER = 4           # 低通阶数
ECG_MA_WINDOW = 5          # 移动平均窗口大小

# ==================== R 峰检测参数 ====================
RPEAK_REFRACTORY = int(0.3 * SAMPLE_RATE)   # 不应期 300ms
RPEAK_SEARCH_BACK = int(1.5 * SAMPLE_RATE)  # 回溯窗口 1.5s
RPEAK_INTEGRATION_WINDOW = int(0.15 * SAMPLE_RATE)  # 积分窗口 150ms
RPEAK_THRESHOLD_FACTOR = 0.4  # 自适应阈值因子

# ==================== 心率计算参数 ====================
HR_AVERAGING_BEATS = 8      # 滑动平均拍数
HR_MIN = 30                 # 最低合理心率 BPM
HR_MAX = 250                # 最高合理心率 BPM

# ==================== SpO2 参数 ====================
SPO2_CALIBRATION_A = 110.0  # 经验校准系数 A
SPO2_CALIBRATION_B = 25.0   # 经验校准系数 B
SPO2_MIN = 70.0             # 最低合理血氧 %
SPO2_MAX = 100.0            # 最高合理血氧 %

# ==================== 脉搏率参数 ====================
PR_MIN = 30                 # 最低合理脉搏率 bpm
PR_MAX = 250                # 最高合理脉搏率 bpm

# ==================== 报警阈值 ====================
@dataclass
class AlarmThresholds:
    hr_low: float = 50.0        # 心率过低 BPM
    hr_high: float = 120.0      # 心率过高 BPM
    spo2_low: float = 90.0      # 血氧过低 %
    pr_low: float = 50.0        # 脉搏率过低 bpm
    pr_high: float = 120.0      # 脉搏率过高 bpm
    signal_loss_seconds: float = 3.0  # 信号丢失报警时间

ALARM_THRESHOLDS = AlarmThresholds()

# ==================== 报警优先级 ====================
ALARM_LEVEL_EMERGENCY = "emergency"  # 红色
ALARM_LEVEL_HIGH = "high"            # 橙色
ALARM_LEVEL_MEDIUM = "medium"        # 黄色

# ==================== 数据记录 ====================
CSV_DELIMITER = ","
CSV_HEADERS = ["timestamp", "ecg_raw", "ecg_filtered", "ppg_raw",
               "ppg_filtered", "heart_rate", "spo2", "pulse_rate"]
EXPORT_DIR = "./exports"
RECORD_INTERVAL_MS = 1000    # 数据记录间隔 ms

# ==================== UI 颜色方案 ====================
COLOR_BG_DARK = "#0a0a0f"
COLOR_BG_PANEL = "#12121a"
COLOR_BG_WIDGET = "#1a1a25"
COLOR_ECG = "#00ff88"
COLOR_PPG = "#4488ff"
COLOR_HR = "#00ff88"
COLOR_SPO2 = "#4488ff"
COLOR_PR = "#00ccff"
COLOR_ALARM_EMERGENCY = "#ff2244"
COLOR_ALARM_HIGH = "#ff6644"
COLOR_ALARM_MEDIUM = "#ffaa22"
COLOR_GRID = "#1e1e30"
COLOR_TEXT_PRIMARY = "#e0e0e0"
COLOR_TEXT_SECONDARY = "#888899"
COLOR_BORDER = "#2a2a3a"
COLOR_BUTTON = "#1e1e35"
COLOR_BUTTON_HOVER = "#2a2a45"
COLOR_BUTTON_PRESSED = "#15152a"
COLOR_SUCCESS = "#00cc66"
COLOR_WARNING = "#ffaa00"
COLOR_DANGER = "#ff3344"
