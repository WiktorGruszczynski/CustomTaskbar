# Custom Taskbar

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

> [!IMPORTANT]
> **Project Status: Obsolete** > This project was developed for Windows 10 and older environments. Since Windows 11 now includes native taskbar centering as a built-in feature, this application is no longer necessary for modern systems but remains here as a showcase of Python system-level scripting.
>



## Description

A lightweight console application written in Python that allows users to align the Windows Taskbar icons to the center of the screen, providing a modern

## 🌟 Features

* **Center Alignment:** Automatically calculates and sets the taskbar icons to the center of your primary monitor.
* **Console-Based:** Low resource usage and straightforward execution.

## 🛠️ Built With

* **Python:** Core logic and system interactions.
* **Windows API:** Used for manipulating taskbar position and alignment.

## 🚀 Getting Started

### Prerequisites
* Windows 10.
* Python 3.8 or higher installed on your system.

### How to use
1. Enter following command in terminal - `python main.py`

### Configuration

The application stores user preferences in a dedicated configuration file with a `.cfg` extension. This allows for persistent settings that are loaded every time the application starts.

| Key | Default | Description |
| :--- | :--- | :--- |
| `animation` | `1` | Enables (1) or disables (0) smooth icon movement. |
| `align_center` | `1` | Centers taskbar icons. |
| `align_primary` | `1` | Applies centering to the primary monitor. |
| `align_secondary` | `1` | Applies centering to secondary monitors. |
| `refresh_rate` | `0.2` | Interval in seconds between position updates. |
| `speed` | `200` | Velocity of the centering animation. |
| `offset` | `0` | Manual pixel adjustment (horizontal shift). |
| `win_button` | `1` | Includes the Start button in centering logic. |
   
