# pico-driverIO-webserver
BSR Driver IO Remote Control - Allows for remote boot control of Pi 4

## Overview

This MicroPython project runs on a Raspberry Pi Pico W and provides a web-based dashboard for remotely controlling a Raspberry Pi 4. It features passcode authentication and safety checks to prevent accidental resets.

![Image of Remote Control Application](Images/menu_image.png "Remote Control Application")

## Project Structure

### Root Files (to be flashed to Pico W)
- `main.py` - Main MicroPython web server script
- `wifi_config.txt` - WiFi credentials configuration
- `driverio_config.txt` - Driver IO (Pi 4) IP, credentials, and passcode
- `logo_base64.txt` - Base64-encoded logo for web dashboard (optional)
- `boot.py` - Boot configuration (optional)

### Development Files
- `tools/` - Utility scripts (e.g., `convert_logo.py`)
- `tests/` - Test scripts for WiFi and server functionality
- `archive/` - Old/backup files
- `Images/` - Source logo image files

## Setup

### 1. Configure WiFi Credentials

Make a file named `wifi_config.txt` and edit it with your WiFi network details:

```
SSID=your_wifi_ssid
PASSWORD=your_wifi_password
```

### 2. Configure Driver IO Settings

Make a file called `driverio_config.txt` and edit it with your Pi 4 details. You can set any six digit pin you'd like:

```
DRIVERIO_IP=10.42.0.18
DRIVERIO_USER=your_username
DRIVERIO_PASS=your_password
PASSCODE=123456
```

**Note:** The 6-digit PASSCODE is required to authenticate all web dashboard actions.

### 3. Hardware Setup

Connect GPIO pin 9 from the Pico W to a MOSFET switch that shorts the Pi 4's **RUN/Reset pins**. This allows the Pico to trigger a hardware reset/boot of the Pi 4.

**Pi 4 RUN Pin Specifications:**
- Short duration: 0.1-0.5 seconds (Pico uses 0.3s)
- Effect: Triggers immediate hardware reset (same as power-cycle)
- Use case: Boot up Pi when powered but offline

### 4. Upload Files to Pico W

Using the MicroPico VS Code extension or Thonny, upload these files to your Pico W:
- `main.py`
- `wifi_config.txt`
- `driverio_config.txt`
- `logo_base64.txt` (optional)

### 5. Run the Script

The script will automatically run when the Pico W boots. It will:
1. Parse WiFi credentials from `wifi_config.txt`
2. Connect to the specified WiFi network
3. Load the logo from `logo_base64.txt` (if present)
4. Start a web server on port 80
5. Display the Pico's IP address in the console

### 6. Access the Dashboard

Open a web browser and navigate to the Pico's IP address (e.g., `http://192.168.1.110`).

## Web Dashboard Features

- **Boot up Pi** (Green button) - Pings the Pi 4 first to check if it's already online. If offline, triggers the RUN/Reset pin to boot it up safely.
- **Check Driver IO Status** (White button) - Verifies if the Pi 4 is online and reachable via SSH port check.

### Security

All actions require a **6-digit passcode** entered via browser prompt. Invalid passcodes display "ACCESS DENIED" and do not execute commands.

## Requirements

- Raspberry Pi Pico W with MicroPython firmware
- WiFi network
- Raspberry Pi 4 (Driver IO) with power and ethernet
- MOSFET switch to interface Pico GPIO with Pi 4 RUN pins
- VS Code with MicroPico extension (recommended) or Thonny IDE
