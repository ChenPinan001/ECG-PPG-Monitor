<div align="center">

# ECG-PPG-Monitor

## Dual-channel ECG & PPG Physiological Signal Acquisition System

### Multi-parameter Vital Signs Real-time Monitoring Platform based on STM32 + PyQt5

[English](./README.md) | [简体中文](./README_CN.md)

![STM32](https://img.shields.io/badge/STM32-HAL-blue)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI-green)
![MIT](https://img.shields.io/badge/License-MIT-lightgrey)

</div>

---

# 📖 Project Introduction

This project is a complete **embedded hardware + host software** dual-channel physiological signal acquisition solution, designed for biomedical engineering teaching, embedded development, and physiological signal verification scenarios.

The **hardware side** is developed based on the STM32 HAL library, integrating ECG electrocardiogram and PPG photoplethysmography signal acquisition circuits. The **host software** is built with Python + PyQt5 to provide a graphical interactive interface, communicating with the lower computer via serial port, and实现完整功能包括 real-time waveform drawing, digital filtering preprocessing, vital sign parameter calculation, hardware gain control, analog signal generation, multi-format data export, and alarm logging.

---

# 🖥️ System Demo

<img width="1918" height="1020" alt="063d9880843635abe8d57eca6846c112" src="https://github.com/user-attachments/assets/537d532c-24a2-49af-b7af-58e084fe3484" />


---

# 📋 Table of Contents

1. Project Introduction
2. Core Features
3. System Architecture
4. Tech Stack & Dependencies
5. Project Structure
6. Quick Start
7. Function Description
8. License

---

# ✨ Core Features

## 🔌 Hardware Acquisition (STM32)

- Developed based on STM32 HAL library
- ECG analog front-end acquisition
- PPG photoplethysmography sensor driver
- Dual-channel synchronous ADC sampling
- Programmable Gain Amplifier (PGA) control
- Serial data transmission (UART)
- Low-power design and power management

## 📡 Serial Communication

- COM port auto-detection and manual selection
- Adjustable baud rate (default 115200)
- Data bits, stop bits, parity configuration
- Real-time serial status display and one-click switch

## 📈 Dual-channel Waveform Display

- ECG real-time waveform drawing
- PPG pulse wave real-time waveform drawing
- Dual-channel independent canvas with grid background
- Auto-range adaptation and scrolling waveform refresh

## 🧹 Digital Filtering System

### ECG Channel

- High-pass filtering
- Low-pass filtering
- Notch filtering
- 50Hz power frequency filtering

### PPG Channel

- High-pass filtering
- Low-pass filtering
- Notch filtering
- 50Hz power frequency filtering

Both channels can be independently switched on/off, flexibly adapting to different acquisition environments.

## 💓 Vital Sign Calculation

- Real-time heart rate (BPM) calculation
- Real-time blood oxygen saturation (SpO₂) calculation
- Real-time pulse rate monitoring
- Dynamic numerical panel display

## 🎚️ Hardware Gain Control

- Supports x1 / x2 / x4 / x8 / x16 / x32 multi-level gain adjustment
- Serial commands directly control lower computer hardware
- Real-time response, dynamic signal amplitude adjustment

## 🔬 Analog Signal Mode

- Built-in analog signal generator
- Analog heart rate slider adjustment (BPM)
- Analog blood oxygen slider adjustment (%)
- Function debugging and demonstration without hardware

## 📤 Data Export

- Export raw data in CSV format
- Export structured data in Excel format
- One-click PDF test report generation
- Support complete sampling data and parameter recording

## 🚨 Alarm & Log System

- Physiological parameter abnormal event recording
- Complete timestamp retention for alarm events
- Raw serial communication data log
- Status bar real-time display of baud rate, runtime, data volume

---

# 🏗️ System Architecture

<img width="1188" height="1324" alt="78ea071800d2387f5a70110120c94f1b" src="https://github.com/user-attachments/assets/541ef44f-63e7-4091-a9f0-5b1104c43488" />


---

# 🛠️ Tech Stack & Dependencies

## Hardware Side

- STM32 HAL Library      # STM32 Hardware Abstraction Layer
- Keil MDK               # Integrated Development Environment
- C Language             # Embedded Development

## Software Side

- Python >= 3.8
- PyQt5                  # GUI Graphical Interface
- pyqtgraph              # Real-time Waveform Drawing
- numpy                  # Numerical Calculation & Signal Processing
- scipy                  # Digital Filtering Algorithm
- pandas                 # Data Processing & Export
- pyserial               # Serial Communication
- openpyxl               # Excel File Export
- reportlab              # PDF Report Generation

---

# 📂 Project Structure

```
ecg-ppg-monitor
│
├── Hardware/               # Hardware code (STM32 HAL / Keil C)
│   ├── Core/               # Core code (main.c, interrupt handling, etc.)
│   ├── Drivers/            # HAL library drivers
│   ├── Inc/                # Header files
│   ├── Src/                # Source files
│   └── MDK-ARM/            # Keil project files
│
├── config/                 # Configuration files
│   └── config.py           # System parameter configuration
│
├── core/                   # Core business logic
│   ├── signal_manager.py   # Signal management & scheduling
│   └── algorithm.py        # Core algorithm implementation
│
├── data/                   # Data storage directory
│   └── sample_data/        # Sample data
│
├── exports/                # Export file directory
│   ├── csv/                # CSV exports
│   ├── excel/              # Excel exports
│   └── pdf/                # PDF reports
│
├── report/                 # Report templates & documents
│   └── templates/          # PDF report templates
│
├── ui/                     # Interface related files
│   ├── main_window.py      # Main window logic
│   └── ui_main_window.py   # UI interface definition
│
├── utils/                  # Utility functions
│   ├── logger.py           # Logging utility
│   └── helpers.py          # Helper functions
│
├── main.py                 # Program entry
├── requirements.txt        # Python dependency list
├── README.md
└── README_CN.md
```

---

# 🚀 Quick Start

## Clone the Project

```bash
git clone https://github.com/ChenPinan001/ECG-PPG-Monitor.git
cd ecg-ppg-monitor
```

## Hardware Compilation & Flashing

1. Open the project file in the `Hardware/` directory using Keil MDK
2. Configure target chip model and debugger
3. Compile the project and flash it to the STM32 development board
4. Connect ECG electrodes and PPG sensor

## Software Dependency Installation

```bash
pip install -r requirements.txt
```

## Connect Hardware

Connect the STM32 development board to the computer via USB-to-serial module, and confirm the COM port number.

> **Analog mode** is available for function experience without hardware.

## Launch the Host Software

```bash
python main.py
```

## Operation Steps

1. Select the corresponding COM port and baud rate in the "Serial Settings" area
2. Click "Open Serial Port" to start data acquisition
3. Enable filtering options for ECG / PPG channels as needed
4. Adjust gain level to adapt to signal amplitude
5. Click "Export CSV / Export Excel / Generate PDF" to save data

---

# 📝 Function Description

## Filter Parameter Description

| Filter Type | Function | Application Scenario |
| ----------- | -------- | -------------------- |
| High-pass Filter | Remove baseline drift and low-frequency interference | Baseline shift caused by movement and breathing |
| Low-pass Filter | Suppress high-frequency noise and glitches | EMG interference, environmental high-frequency noise |
| Notch Filter | Remove specific frequency interference | Power frequency interference, power supply noise |
| 50Hz Filter | Dedicated power frequency notch | Domestic mains 50Hz interference suppression |

## Gain Level Description

| Gain Level | Magnification | Signal Strength |
| ---------- | ------------- | --------------- |
| x1 | 1x | Strong signal scenarios |
| x2 ~ x8 | 2 ~ 8x | Regular acquisition scenarios |
| x16 ~ x32 | 16 ~ 32x | Weak signal, low perfusion scenarios |

## Analog Mode Usage

After enabling analog mode, you can adjust the simulated heart rate and blood oxygen values via sliders, and the system will generate analog signals with corresponding parameters for:
- Function debugging without hardware environment
- Interface demonstration and teaching display
- Algorithm logic verification and testing

---

# 📄 License

This project is for academic research, teaching, and personal development only, and follows the MIT License open source agreement.
