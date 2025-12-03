# pico-driverIO-webserver
Allows for remote control (startup/shutdown) of Pi 4

## Overview

This MicroPython project runs on a Raspberry Pi Pico W and provides a web-based dashboard for remotely controlling a Raspberry Pi 4 (boot up and soft reboot functionality).

## Files

- `main.py` - Main MicroPython script that runs the web server
- `wifi_config.txt` - Configuration file for WiFi credentials

## Setup

### 1. Configure WiFi Credentials

Edit `wifi_config.txt` with your WiFi network details:

```
SSID=your_wifi_ssid
PASSWORD=your_wifi_password
```

### 2. Upload Files to Pico W

Upload both `main.py` and `wifi_config.txt` to your Raspberry Pi Pico W using Thonny or another MicroPython IDE.

### 3. Configure GPIO Pins (Optional)

In `main.py`, uncomment and configure the GPIO pin definitions and control code:

```python
# GPIO PIN CONFIGURATION section at the top of main.py
BOOT_PIN = Pin(16, Pin.OUT)  # GPIO pin to trigger Pi boot
REBOOT_PIN = Pin(17, Pin.OUT)  # GPIO pin to trigger Pi reboot
```

Then update the `handle_boot()` and `handle_reboot()` functions with your GPIO control logic.

### 4. Run the Script

The script will automatically run when the Pico W boots. It will:
1. Parse WiFi credentials from `wifi_config.txt`
2. Connect to the specified WiFi network
3. Start a web server on port 80
4. Display the IP address in the console

### 5. Access the Dashboard

Open a web browser and navigate to the IP address displayed in the console (e.g., `http://192.168.1.100`).

## Web Dashboard Features

- **Boot up Pi** - Triggers the boot sequence for the Raspberry Pi 4
- **Soft Reboot** - Triggers a soft reboot of the Raspberry Pi 4

## Requirements

- Raspberry Pi Pico W
- MicroPython firmware installed on the Pico W
- WiFi network
