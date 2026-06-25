# core/serial_reader.py - 串口数据接收线程

import struct
from typing import Optional

import serial
import serial.tools.list_ports
from PyQt5.QtCore import QThread, pyqtSignal

from config.settings import (
    SERIAL_PORT, SERIAL_BAUDRATE, SERIAL_TIMEOUT,
    SERIAL_BYTESIZE, SERIAL_PARITY, SERIAL_STOPBITS,
    FRAME_HEADER, FRAME_LENGTH,
    FRAME_TYPE_ECG_PPG, FRAME_TYPE_ECG_ONLY, FRAME_TYPE_PPG_ONLY,
    FRAME_TYPE_PPG_RED_IR,
)
from utils.helpers import validate_frame_checksum, timestamp_now


class SerialReader(QThread):
    """串口数据读取线程，解析 12 字节数据帧"""

    data_received = pyqtSignal(int, int, str)   # ecg_raw, ppg_raw, timestamp
    ppg_ir_received = pyqtSignal(int, str)       # ppg_ir, timestamp
    connection_status = pyqtSignal(bool, str)    # connected, message
    error_occurred = pyqtSignal(str)             # error message
    text_received = pyqtSignal(str)              # 文本响应 (命令回复)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._serial: Optional[serial.Serial] = None
        self._running = False
        self._port = SERIAL_PORT
        self._baudrate = SERIAL_BAUDRATE
        self._buffer = bytearray()

    def set_port(self, port: str) -> None:
        self._port = port

    def set_baudrate(self, baudrate: int) -> None:
        self._baudrate = baudrate

    @staticmethod
    def list_ports() -> list:
        """枚举可用串口，按串口号排序"""
        ports = serial.tools.list_ports.comports()
        port_list = [(p.device, p.description) for p in ports]
        # 按COM口号排序 (COM3, COM7, COM8...)
        def sort_key(item):
            device = item[0]
            if device.startswith("COM"):
                try:
                    return int(device[3:])
                except ValueError:
                    return 9999
            return 9999
        port_list.sort(key=sort_key)
        return port_list

    def connect(self) -> bool:
        """打开串口连接"""
        try:
            self._serial = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                timeout=SERIAL_TIMEOUT,
                bytesize=SERIAL_BYTESIZE,
                parity=SERIAL_PARITY,
                stopbits=SERIAL_STOPBITS,
            )
            self.connection_status.emit(True, f"已连接 {self._port} @ {self._baudrate}")
            return True
        except Exception as e:
            self.connection_status.emit(False, f"连接失败: {str(e)}")
            return False

    def disconnect(self) -> None:
        """关闭串口连接"""
        self._running = False
        if self._serial and self._serial.is_open:
            self._serial.close()
        self.connection_status.emit(False, "已断开连接")

    def write(self, data: str) -> None:
        """发送数据到串口"""
        if self._serial and self._serial.is_open:
            try:
                encoded = data.encode('utf-8')
                print(f"[SERIAL_WRITE] Writing {len(encoded)} bytes: {encoded.hex()}")
                self._serial.write(encoded)
                print(f"[SERIAL_WRITE] Write OK")
            except Exception as e:
                print(f"[SERIAL_WRITE] Error: {e}")
                self.error_occurred.emit(f"发送失败: {str(e)}")

    def run(self) -> None:
        """线程主循环：读取串口数据并解析帧"""
        if not self._serial or not self._serial.is_open:
            self.error_occurred.emit("串口未打开")
            return

        self._running = True
        self._buffer.clear()

        while self._running:
            try:
                if self._serial.in_waiting > 0:
                    data = self._serial.read(self._serial.in_waiting)
                    self._buffer.extend(data)
                    self._parse_frames()
                else:
                    self.msleep(1)
            except serial.SerialException as e:
                self.error_occurred.emit(f"串口错误: {str(e)}")
                self._running = False
                break
            except Exception as e:
                self.error_occurred.emit(f"读取错误: {str(e)}")

    def _parse_frames(self) -> None:
        """从缓冲区解析完整数据帧"""
        # 先检查是否有文本数据 (非帧头开头的数据)
        header_idx = self._buffer.find(FRAME_HEADER)
        if header_idx > 0:
            text_data = self._buffer[:header_idx]
            try:
                text = text_data.decode('utf-8', errors='ignore').strip()
                if text:
                    self.text_received.emit(text)
            except:
                pass
            del self._buffer[:header_idx]

        while len(self._buffer) >= FRAME_LENGTH:
            header_idx = self._buffer.find(FRAME_HEADER)
            if header_idx == -1:
                self._buffer = self._buffer[-len(FRAME_HEADER):]
                break

            if header_idx > 0:
                del self._buffer[:header_idx]

            if len(self._buffer) < FRAME_LENGTH:
                break

            frame = self._buffer[:FRAME_LENGTH]

            if not validate_frame_checksum(frame):
                del self._buffer[:1]
                continue

            try:
                frame_type = frame[2]
                ecg_val = struct.unpack("<i", frame[3:7])[0]
                ppg_val = struct.unpack("<i", frame[7:11])[0]

                # 发送解析后的数据到串口数据区显示
                ts = timestamp_now()

                if frame_type == FRAME_TYPE_PPG_RED_IR:
                    data_str = f"[{ts}] RED={ecg_val} IR={ppg_val}"
                    self.text_received.emit(data_str)
                    self.ppg_ir_received.emit(ppg_val, ts)
                else:
                    data_str = f"[{ts}] ECG={ecg_val} PPG={ppg_val}"
                    self.text_received.emit(data_str)

                    if frame_type == FRAME_TYPE_ECG_PPG:
                        self.data_received.emit(ecg_val, ppg_val, ts)
                    elif frame_type == FRAME_TYPE_ECG_ONLY:
                        self.data_received.emit(ecg_val, 0, ts)
                    elif frame_type == FRAME_TYPE_PPG_ONLY:
                        self.data_received.emit(0, ppg_val, ts)

            except (struct.error, IndexError):
                pass

            del self._buffer[:FRAME_LENGTH]

    def stop(self) -> None:
        """停止线程"""
        self._running = False
        self.wait(1000)
