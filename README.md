# 🏠 IoT Home Security System

A distributed **home security simulation system** built in Python, demonstrating client-server TCP socket communication, multi-threading, and a custom application-layer protocol — developed as a university **Computer Networks** project.

---

## 🏗️ Architecture

The system consists of two independent applications that communicate over a TCP network:

```
┌─────────────────────────────┐            TCP Socket       ┌──────────────────────────────┐
│      dashboard.py           │◄───────────port 5000───────►│        sensor.py             │
│   Security Command Center   │                             │   Hardware Simulator         │
│        (SERVER)             │                             │       (CLIENT)               │
└─────────────────────────────┘                             └──────────────────────────────┘
```

- **`dashboard.py`** — Runs as the **TCP server**. Accepts multiple concurrent sensor connections, processes incoming events, and broadcasts alarm commands back to all connected clients.
- **`sensor.py`** — Runs as the **TCP client**. Simulates physical IoT hardware (door/window/motion sensors + PIN keypad) and auto-reconnects to the server every 3 seconds if disconnected.

Multiple instances of `sensor.py` can connect simultaneously, simulating a real distributed sensor network.

---

## ✨ Features

### Security Command Center (`dashboard.py`)
- 🔐 Operator login screen with credential validation
- 🛡️ Manual ARM / DISARM system toggle
- 📋 Real-time timestamped event log
- 🌐 Cloud uplink / internet connectivity monitoring
- 📡 Multi-threaded TCP server — handles multiple sensor clients concurrently
- 🚨 Visual INTRUDER ALERT on alarm trigger

### Hardware Simulator (`sensor.py`)
- 🚪 3 simulated security zones:
  - Zone 1: Front Door
  - Zone 2: Kitchen Window
  - Zone 3: Garage Motion
- 🔢 PIN keypad — correct code disarms the system, wrong code triggers alarm panic
- 🔴 Visual alarm feedback (full red screen + siren activated message)
- 🔄 Auto-reconnect logic — reconnects to server every 3 seconds if connection drops

---

## 📡 Custom Communication Protocol

The two applications communicate using a **custom text-based TCP protocol**:

| Message | Direction | Meaning |
|---|---|---|
| `ZONE:Front Door:OPEN` | Sensor → Server | Front door opened |
| `ZONE:Kitchen Window:CLOSED` | Sensor → Server | Kitchen window closed |
| `AUTH:SUCCESS` | Sensor → Server | Correct PIN entered — disarm |
| `AUTH:FAIL` | Sensor → Server | Wrong PIN entered — trigger panic |
| `ALARM_TRIGGER` | Server → All Sensors | Alarm activated — turn red |
| `ALARM_CLEAR` | Server → All Sensors | Alarm cleared — return to normal |

---

## 🛠️ Tech Stack

| Technology | Usage |
|---|---|
| **Python** | Core language |
| **`socket`** | TCP client-server communication |
| **`threading`** | Concurrent client handling + background tasks |
| **`tkinter`** | GUI for both applications |
| **`urllib`** | Internet/cloud uplink monitoring |

> ✅ **No external dependencies** — uses Python standard library only.

---

## 🚀 How to Run

**Requirements:** Python 3.x (no `pip install` needed)

### Step 1 — Start the server (dashboard)
```bash
python dashboard.py
```
Log in with: **Operator ID:** `admin` | **Password:** `1234`

### Step 2 — Start the sensor simulator (in a separate terminal)
```bash
python sensor.py
```
The sensor will automatically connect to `127.0.0.1:5000`.

> To simulate a distributed network, open multiple terminals and run `sensor.py` in each one.

---

## 📁 Repository Structure

```
IoT-Home-Security-System/
├── dashboard.py        # TCP server — Security Command Center GUI
├── sensor.py           # TCP client — Hardware Simulator GUI
└── docs/
    ├── project-report.pdf    # Full project documentation
    └── presentation.pptx     # Project presentation slides
```

---

## 📚 Academic Context

Developed as a **Computer Networks** university project at the Technical University of Cluj-Napoca, Romania.
Demonstrates: TCP socket programming, client-server architecture, multi-threading, custom application-layer protocol design, and real-time GUI development.

---

## 👤 Author

**Dezső László** — [LinkedIn](https://www.linkedin.com/in/dezsolaszlo/) · [GitHub](https://github.com/dezsolaszlo)
