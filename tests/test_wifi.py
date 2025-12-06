"""
Simple test script to verify WiFi connection
"""

import network
import time

def parse_wifi_config(filename="wifi_config.txt"):
    ssid = None
    password = None
    
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("SSID="):
                    ssid = line[5:]
                elif line.startswith("PASSWORD="):
                    password = line[9:]
    except OSError as e:
        print(f"Error reading {filename}: {e}")
        return None, None
    
    return ssid, password

print("Testing WiFi connection...")

# Parse WiFi credentials
ssid, password = parse_wifi_config()

if not ssid or not password:
    print("ERROR: Could not read WiFi credentials from wifi_config.txt")
else:
    print(f"SSID: {ssid}")
    print(f"Password: {'*' * len(password)}")
    
    # Try to connect
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    print(f"Connecting to {ssid}...")
    wlan.connect(ssid, password)
    
    # Wait for connection
    max_wait = 10
    while max_wait > 0:
        if wlan.isconnected():
            break
        max_wait -= 1
        print(".", end="")
        time.sleep(1)
    
    print()
    
    if wlan.isconnected():
        print("SUCCESS! Connected to WiFi")
        print(f"IP address: {wlan.ifconfig()[0]}")
    else:
        print("FAILED: Could not connect to WiFi")
        print(f"Status: {wlan.status()}")

print("\nTest complete!")
