# ui/styles.py - 深色医疗监护仪风格 QSS 样式表

from config.settings import (
    COLOR_BG_DARK, COLOR_BG_PANEL, COLOR_BG_WIDGET,
    COLOR_ECG, COLOR_PPG, COLOR_HR, COLOR_SPO2, COLOR_PR,
    COLOR_ALARM_EMERGENCY, COLOR_ALARM_HIGH, COLOR_ALARM_MEDIUM,
    COLOR_GRID, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_BORDER, COLOR_BUTTON, COLOR_BUTTON_HOVER,
    COLOR_BUTTON_PRESSED, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
)


def get_stylesheet() -> str:
    """返回完整的 QSS 样式表"""
    return f"""
    /* ========== 全局 ========== */
    QMainWindow {{
        background-color: {COLOR_BG_DARK};
    }}

    QWidget {{
        color: {COLOR_TEXT_PRIMARY};
        font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
        font-size: 13px;
    }}

    /* ========== 菜单栏 ========== */
    QMenuBar {{
        background-color: {COLOR_BG_PANEL};
        border-bottom: 1px solid {COLOR_BORDER};
        padding: 2px;
    }}

    QMenuBar::item {{
        padding: 4px 12px;
        background: transparent;
        border-radius: 4px;
    }}

    QMenuBar::item:selected {{
        background-color: {COLOR_BUTTON_HOVER};
    }}

    QMenu {{
        background-color: {COLOR_BG_PANEL};
        border: 1px solid {COLOR_BORDER};
        padding: 4px;
    }}

    QMenu::item {{
        padding: 6px 24px;
        border-radius: 4px;
    }}

    QMenu::item:selected {{
        background-color: {COLOR_BUTTON_HOVER};
    }}

    /* ========== 按钮 ========== */
    QPushButton {{
        background-color: {COLOR_BUTTON};
        border: 1px solid {COLOR_BORDER};
        border-radius: 6px;
        padding: 8px 16px;
        color: {COLOR_TEXT_PRIMARY};
        font-weight: bold;
        min-height: 20px;
    }}

    QPushButton:hover {{
        background-color: {COLOR_BUTTON_HOVER};
        border-color: {COLOR_TEXT_SECONDARY};
    }}

    QPushButton:pressed {{
        background-color: {COLOR_BUTTON_PRESSED};
    }}

    QPushButton:disabled {{
        background-color: {COLOR_BG_DARK};
        color: {COLOR_TEXT_SECONDARY};
    }}

    QPushButton#btnConnect {{
        background-color: #1a3a2a;
        border-color: #2a5a3a;
    }}

    QPushButton#btnConnect:hover {{
        background-color: #2a4a3a;
    }}

    QPushButton#btnDisconnect {{
        background-color: #3a1a1a;
        border-color: #5a2a2a;
    }}

    QPushButton#btnDisconnect:hover {{
        background-color: #4a2a2a;
    }}

    QPushButton#btnStart {{
        background-color: #1a3a2a;
        border-color: {COLOR_SUCCESS};
        color: {COLOR_SUCCESS};
    }}

    QPushButton#btnStart:hover {{
        background-color: #2a4a3a;
    }}

    QPushButton#btnStop {{
        background-color: #3a1a1a;
        border-color: {COLOR_DANGER};
        color: {COLOR_DANGER};
    }}

    QPushButton#btnStop:hover {{
        background-color: #4a2a2a;
    }}

    /* ========== 下拉框 ========== */
    QComboBox {{
        background-color: {COLOR_BG_WIDGET};
        border: 1px solid {COLOR_BORDER};
        border-radius: 4px;
        padding: 6px 12px;
        color: {COLOR_TEXT_PRIMARY};
        min-width: 100px;
    }}

    QComboBox:hover {{
        border-color: {COLOR_TEXT_SECONDARY};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {COLOR_BG_PANEL};
        border: 1px solid {COLOR_BORDER};
        selection-background-color: {COLOR_BUTTON_HOVER};
        color: {COLOR_TEXT_PRIMARY};
    }}

    /* ========== 复选框 ========== */
    QCheckBox {{
        spacing: 8px;
        color: {COLOR_TEXT_PRIMARY};
    }}

    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {COLOR_BORDER};
        border-radius: 3px;
        background-color: {COLOR_BG_WIDGET};
    }}

    QCheckBox::indicator:checked {{
        background-color: {COLOR_ECG};
        border-color: {COLOR_ECG};
    }}

    /* ========== 标签 ========== */
    QLabel {{
        color: {COLOR_TEXT_PRIMARY};
        background: transparent;
    }}

    /* ========== 分组框 ========== */
    QGroupBox {{
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 16px;
        font-weight: bold;
        color: {COLOR_TEXT_SECONDARY};
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
    }}

    /* ========== 列表 ========== */
    QListWidget {{
        background-color: {COLOR_BG_WIDGET};
        border: 1px solid {COLOR_BORDER};
        border-radius: 6px;
        padding: 4px;
        color: {COLOR_TEXT_PRIMARY};
    }}

    QListWidget::item {{
        padding: 6px 8px;
        border-radius: 4px;
    }}

    QListWidget::item:selected {{
        background-color: {COLOR_BUTTON_HOVER};
    }}

    /* ========== 状态栏 ========== */
    QStatusBar {{
        background-color: {COLOR_BG_PANEL};
        border-top: 1px solid {COLOR_BORDER};
        color: {COLOR_TEXT_SECONDARY};
        padding: 2px;
    }}

    /* ========== 滚动条 ========== */
    QScrollBar:vertical {{
        background: {COLOR_BG_DARK};
        width: 8px;
        border-radius: 4px;
    }}

    QScrollBar::handle:vertical {{
        background: {COLOR_BORDER};
        border-radius: 4px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {COLOR_TEXT_SECONDARY};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    /* ========== 工具提示 ========== */
    QToolTip {{
        background-color: {COLOR_BG_PANEL};
        border: 1px solid {COLOR_BORDER};
        color: {COLOR_TEXT_PRIMARY};
        padding: 4px 8px;
        border-radius: 4px;
    }}
    """
