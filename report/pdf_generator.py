# report/pdf_generator.py - PDF 监测报告自动生成

import os
from datetime import datetime
from typing import List, Dict, Any

import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image,
)
from reportlab.graphics.shapes import Drawing, Line, String, Rect
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.widgets.markers import makeMarker

from config.settings import (
    COLOR_ECG, COLOR_PPG, COLOR_ALARM_EMERGENCY,
    COLOR_ALARM_HIGH, COLOR_ALARM_MEDIUM,
)


class PDFGenerator:
    """PDF 监测报告生成器"""

    def __init__(self):
        self._styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self) -> None:
        """设置自定义样式"""
        self._styles.add(ParagraphStyle(
            name="ChineseTitle",
            parent=self._styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1a1a2e"),
        ))
        self._styles.add(ParagraphStyle(
            name="ChineseHeading",
            parent=self._styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#2a2a4e"),
        ))
        self._styles.add(ParagraphStyle(
            name="ChineseBody",
            parent=self._styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
        ))

    def generate(self, filepath: str, records: List[Dict[str, Any]],
                 alarms: List[Any], patient_name: str = "",
                 patient_id: str = "") -> str:
        """
        生成 PDF 报告
        records: 数据记录列表
        alarms: 报警事件列表
        """
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )

        story = []

        # ========== 封面 ==========
        story.append(Spacer(1, 40 * mm))
        story.append(Paragraph("多参数生命体征监护报告", self._styles["ChineseTitle"]))
        story.append(Spacer(1, 10 * mm))

        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(
            f"生成时间: {report_time}",
            self._styles["ChineseBody"]
        ))
        story.append(Spacer(1, 5 * mm))

        if patient_name:
            story.append(Paragraph(
                f"患者姓名: {patient_name}",
                self._styles["ChineseBody"]
            ))
        if patient_id:
            story.append(Paragraph(
                f"患者ID: {patient_id}",
                self._styles["ChineseBody"]
            ))

        story.append(PageBreak())

        # ========== 监测统计 ==========
        story.append(Paragraph("一、监测统计", self._styles["ChineseHeading"]))
        story.append(Spacer(1, 5 * mm))

        # 提取数据
        hr_values = [r["heart_rate"] for r in records if r["heart_rate"] > 0]
        spo2_values = [r["spo2"] for r in records if r["spo2"] > 0]
        pr_values = [r["pulse_rate"] for r in records if r["pulse_rate"] > 0]

        stats_data = self._compute_statistics(hr_values, spo2_values, pr_values)

        # 统计表格
        stats_table = Table([
            ["参数", "均值", "最小值", "最大值", "标准差", "有效数据点"],
            [
                "心率 (BPM)",
                f"{stats_data['hr_mean']:.1f}",
                f"{stats_data['hr_min']:.1f}",
                f"{stats_data['hr_max']:.1f}",
                f"{stats_data['hr_std']:.1f}",
                str(stats_data['hr_count']),
            ],
            [
                "血氧 (%)",
                f"{stats_data['spo2_mean']:.1f}",
                f"{stats_data['spo2_min']:.1f}",
                f"{stats_data['spo2_max']:.1f}",
                f"{stats_data['spo2_std']:.1f}",
                str(stats_data['spo2_count']),
            ],
            [
                "脉搏率 (bpm)",
                f"{stats_data['pr_mean']:.1f}",
                f"{stats_data['pr_min']:.1f}",
                f"{stats_data['pr_max']:.1f}",
                f"{stats_data['pr_std']:.1f}",
                str(stats_data['pr_count']),
            ],
        ], colWidths=[80, 70, 70, 70, 70, 80])

        stats_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2a2a4e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5fa")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 10 * mm))

        # 监测时段
        if records:
            first_ts = records[0].get("timestamp", "")
            last_ts = records[-1].get("timestamp", "")
            story.append(Paragraph(
                f"监测时段: {first_ts} 至 {last_ts}",
                self._styles["ChineseBody"]
            ))
            story.append(Paragraph(
                f"总记录数: {len(records)}",
                self._styles["ChineseBody"]
            ))

        story.append(Spacer(1, 10 * mm))

        # ========== 报警事件汇总 ==========
        story.append(Paragraph("二、报警事件汇总", self._styles["ChineseHeading"]))
        story.append(Spacer(1, 5 * mm))

        if alarms:
            alarm_table_data = [["时间", "级别", "参数", "数值", "描述"]]
            for alarm in alarms:
                level_display = {"emergency": "紧急", "high": "高", "medium": "中"}
                param_display = {
                    "heart_rate": "心率", "spo2": "血氧",
                    "pulse_rate": "脉搏率", "signal_loss": "信号丢失"
                }
                alarm_table_data.append([
                    alarm.timestamp,
                    level_display.get(alarm.level, alarm.level),
                    param_display.get(alarm.parameter, alarm.parameter),
                    f"{alarm.value:.0f}",
                    alarm.message,
                ])

            alarm_table = Table(alarm_table_data, colWidths=[120, 50, 60, 50, 160])
            alarm_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#cc2222")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, colors.HexColor("#fff5f5")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(alarm_table)
        else:
            story.append(Paragraph("本次监测无报警事件", self._styles["ChineseBody"]))

        story.append(Spacer(1, 10 * mm))

        # ========== 趋势图 ==========
        story.append(Paragraph("三、趋势图", self._styles["ChineseHeading"]))
        story.append(Spacer(1, 5 * mm))

        # 心率趋势图
        if hr_values:
            hr_chart = self._create_trend_chart(
                hr_values, "心率趋势 (BPM)", COLOR_ECG, 400, 150
            )
            story.append(hr_chart)
            story.append(Spacer(1, 5 * mm))

        # 血氧趋势图
        if spo2_values:
            spo2_chart = self._create_trend_chart(
                spo2_values, "血氧趋势 (%)", "#4488ff", 400, 150
            )
            story.append(spo2_chart)

        story.append(Spacer(1, 15 * mm))

        # ========== 页脚 ==========
        story.append(Paragraph(
            "--- 报告结束 ---",
            ParagraphStyle(
                "Footer", parent=self._styles["ChineseBody"],
                alignment=TA_CENTER, textColor=colors.gray,
            )
        ))

        # 生成 PDF
        doc.build(story)
        return filepath

    def _compute_statistics(self, hr: List[float], spo2: List[float],
                            pr: List[float]) -> Dict[str, Any]:
        """计算统计指标"""
        def stats(arr):
            if not arr:
                return {"mean": 0, "min": 0, "max": 0, "std": 0, "count": 0}
            a = np.array(arr)
            return {
                "mean": float(np.mean(a)),
                "min": float(np.min(a)),
                "max": float(np.max(a)),
                "std": float(np.std(a)),
                "count": len(a),
            }

        hr_s = stats(hr)
        spo2_s = stats(spo2)
        pr_s = stats(pr)

        return {
            "hr_mean": hr_s["mean"], "hr_min": hr_s["min"],
            "hr_max": hr_s["max"], "hr_std": hr_s["std"],
            "hr_count": hr_s["count"],
            "spo2_mean": spo2_s["mean"], "spo2_min": spo2_s["min"],
            "spo2_max": spo2_s["max"], "spo2_std": spo2_s["std"],
            "spo2_count": spo2_s["count"],
            "pr_mean": pr_s["mean"], "pr_min": pr_s["min"],
            "pr_max": pr_s["max"], "pr_std": pr_s["std"],
            "pr_count": pr_s["count"],
        }

    def _create_trend_chart(self, data: List[float], title: str,
                            color: str, width: int, height: int) -> Drawing:
        """创建趋势折线图"""
        if len(data) < 2:
            return Drawing(width, height)

        # 降采样以提高性能
        if len(data) > 1000:
            step = len(data) // 1000
            data = data[::step]

        d = Drawing(width, height)

        # 背景
        d.add(Rect(0, 0, width, height,
                   fillColor=colors.HexColor("#f8f8fc"),
                   strokeColor=colors.HexColor("#dddddd")))

        # 标题
        d.add(String(10, height - 15, title,
                     fontName="Helvetica-Bold", fontSize=9,
                     fillColor=colors.HexColor("#333333")))

        # 折线图
        lp = LinePlot()
        lp.x = 50
        lp.y = 20
        lp.width = width - 60
        lp.height = height - 45
        lp.data = [list(zip(range(len(data)), data))]
        lp.lines[0].strokeColor = colors.HexColor(color)
        lp.lines[0].strokeWidth = 1
        lp.lines[0].symbol = None

        lp.xValueAxis.visible = True
        lp.xValueAxis.labels.fontSize = 6
        lp.yValueAxis.visible = True
        lp.yValueAxis.labels.fontSize = 6

        d.add(lp)
        return d
