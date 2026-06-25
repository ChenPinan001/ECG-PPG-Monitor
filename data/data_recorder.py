# data/data_recorder.py - 数据保存（CSV + Excel）

import csv
import os
from datetime import datetime
from threading import Lock
from typing import List, Dict, Any

import pandas as pd

from config.settings import CSV_HEADERS, CSV_DELIMITER, EXPORT_DIR


class DataRecorder:
    """数据记录器，支持 CSV 增量写入和 Excel 导出"""

    def __init__(self):
        self._lock = Lock()
        self._records: List[Dict[str, Any]] = []
        self._csv_file: str = ""
        self._csv_writer = None
        self._csv_handle = None
        self._recording = False
        self._start_time = ""

    def start_recording(self, directory: str = EXPORT_DIR) -> str:
        """开始记录，创建 CSV 文件"""
        with self._lock:
            os.makedirs(directory, exist_ok=True)
            self._start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._csv_file = os.path.join(directory, f"ecg_data_{self._start_time}.csv")
            self._csv_handle = open(self._csv_file, "w", newline="", encoding="utf-8")
            self._csv_writer = csv.DictWriter(
                self._csv_handle, fieldnames=CSV_HEADERS, delimiter=CSV_DELIMITER
            )
            self._csv_writer.writeheader()
            self._recording = True
            self._records.clear()
            return self._csv_file

    def stop_recording(self) -> None:
        """停止记录"""
        with self._lock:
            self._recording = False
            if self._csv_handle:
                self._csv_handle.close()
                self._csv_handle = None
                self._csv_writer = None

    def record(self, timestamp: str, ecg_raw: float, ecg_filtered: float,
               ppg_raw: float, ppg_filtered: float, heart_rate: float,
               spo2: float, pulse_rate: float) -> None:
        """记录一行数据"""
        row = {
            "timestamp": timestamp,
            "ecg_raw": ecg_raw,
            "ecg_filtered": ecg_filtered,
            "ppg_raw": ppg_raw,
            "ppg_filtered": ppg_filtered,
            "heart_rate": heart_rate,
            "spo2": spo2,
            "pulse_rate": pulse_rate,
        }
        with self._lock:
            self._records.append(row)
            if self._recording and self._csv_writer:
                self._csv_writer.writerow(row)
                self._csv_handle.flush()

    def export_excel(self, filepath: str = "") -> str:
        """导出全部记录为 Excel 文件"""
        with self._lock:
            if not self._records:
                return ""
            if not filepath:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                os.makedirs(EXPORT_DIR, exist_ok=True)
                filepath = os.path.join(EXPORT_DIR, f"ecg_report_{timestamp}.xlsx")
            df = pd.DataFrame(self._records)
            df.to_excel(filepath, index=False, engine="openpyxl")
            return filepath

    def get_records(self) -> List[Dict[str, Any]]:
        """获取全部记录"""
        with self._lock:
            return list(self._records)

    @property
    def is_recording(self) -> bool:
        return self._recording

    @property
    def record_count(self) -> int:
        with self._lock:
            return len(self._records)
