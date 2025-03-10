# 🎮 Uproject Autoshortcut
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![GitHub Stars](https://img.shields.io/github/stars/MrEluzium/Uproject-Autoshortcut.svg?style=social)](https://github.com/MrEluzium/Uproject-Autoshortcut/stargazers)

A lightweight Python daemon for automatic management of Unreal Engine project shortcuts in the Windows Start Menu.

## 🎯 Project Goal
Automatically maintain Start Menu shortcuts for Unreal Engine projects by:
- Maintaining sync between project directory and Start Menu
- Creating shortcuts when new projects are added
- Removing shortcuts when projects are deleted
- Running efficiently in background as Windows service

## 📋 Prerequisites
- **Windows 10/11**
- **Python 3.13** ([Download](https://www.python.org/downloads/))
  - Must be added to system PATH during installation

## 🚀 Installation & Usage

### 1. Clone Repository
```bash
git clone https://github.com/MrEluzium/Uproject-Autoshortcut.git
cd Uproject-Autoshortcut
```

### 2. Configure Settings

Edit `run_once.bat` and `run_daemon.bat:`
```bash
set ROOT_DIR="F:\Unreal Projects"  👈 Your UE projects directory
set FOLDER_NAME="Unreal Projects" 👈 Start Menu folder name
```

### 3. Start a shortcut manager
##### 3.2 Update shortcuts once
```bash
run_once.bat
```

#### 3.2 Run as Daemon
```bash
run_daemon.bat
```

### 4. Stop a daemon
Only way to stop a working daemon is to kill its process with Task Manager.
Look up for a python process. If there are several of them, find one with a project's venv in properties menu.

## 🔌 Run at System Startup

### Method 1: Task Scheduler (Recommended)
**Create task with included script:**
```batch
create_task.bat
```
This will:
- Create hidden task running at user login
- Run with the highest privileges
- Survive sleep/hibernate cycles
- Start minimized without any visible window
- Retry automatically on failures

**Manual Verification**:
1. Open `taskschd.msc`
2. Look for "Uproject Autoshortcut" in Task Scheduler Library
3. Ensure status shows "Ready"

**To Remove**:
```batch
schtasks /Delete /TN "Uproject Autoshortcut" /F
```

### Method 2: Startup Folder

Press `Win + R` and type:
```
shell:startup
```
Create shortcut to run_daemon.bat

## 🛠️ Technical Notes
- Python 3.13 Required - Not tested with other versions
- Network Drives - Supported through polling observer
- Resource Usage - Typically <20MB RAM, 0% CPU idle

## 🔧 Developer's Log
During a 30-minute pause from polishing my Unreal Engine game, I prototyped this utility using DeepSeek-R1. Even this note, by this point, was written by DeepSeek. The result? A focused demonstration of how brief, intentional breaks can yield production-grade tools when paired with intelligent systems.  (PS Yes, this bastard likes to overly praise himself) 