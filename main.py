"""
MicroPython Web Server for Raspberry Pi Pico W
Driver IO Remote Control Dashboard

This script starts a web server that serves a dashboard for remote control
of a Raspberry Pi 4 (startup/shutdown functionality).
"""

import network
import socket
import time
from machine import Pin

# ============================================================================
# GPIO PIN CONFIGURATION
# ============================================================================
# TODO: Define your GPIO pins here for controlling the Raspberry Pi 4
# Example:
# BOOT_PIN = Pin(16, Pin.OUT)  # GPIO pin to trigger Pi boot
# REBOOT_PIN = Pin(17, Pin.OUT)  # GPIO pin to trigger Pi reboot


def parse_wifi_config(filename="wifi_config.txt"):
    """
    Parse WiFi credentials from a text file.
    
    Expected file format:
    SSID=your_wifi_ssid
    PASSWORD=your_wifi_password
    
    Args:
        filename: Path to the WiFi configuration file
        
    Returns:
        tuple: (ssid, password)
    """
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
    except OSError:
        print(f"Error: Could not read {filename}")
        return None, None
    
    return ssid, password


def connect_wifi(ssid, password, timeout=10):
    """
    Connect to a WiFi network.
    
    Args:
        ssid: WiFi network name
        password: WiFi password
        timeout: Connection timeout in seconds
        
    Returns:
        str: IP address if connected, None otherwise
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        print("Already connected to WiFi")
        return wlan.ifconfig()[0]
    
    print(f"Connecting to WiFi: {ssid}")
    wlan.connect(ssid, password)
    
    start_time = time.time()
    while not wlan.isconnected():
        if time.time() - start_time > timeout:
            print("WiFi connection timeout")
            return None
        time.sleep(0.5)
        print(".", end="")
    
    ip_address = wlan.ifconfig()[0]
    print(f"\nConnected! IP address: {ip_address}")
    return ip_address


def get_html_page():
    """
    Generate the HTML page for the dashboard.
    
    Returns:
        str: HTML content
    """
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Driver IO remote control dashboard</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: Arial, sans-serif;
            background-color: #1a1a2e;
            color: #eee;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }
        h1 {
            margin-bottom: 40px;
            text-align: center;
            color: #00d4ff;
        }
        .button-container {
            display: flex;
            flex-direction: column;
            gap: 20px;
            width: 100%;
            max-width: 300px;
        }
        .btn {
            padding: 20px 40px;
            font-size: 18px;
            font-weight: bold;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            text-align: center;
        }
        .btn-boot {
            background-color: #28a745;
            color: white;
        }
        .btn-boot:hover {
            background-color: #218838;
            transform: scale(1.05);
        }
        .btn-reboot {
            background-color: #ffc107;
            color: #212529;
        }
        .btn-reboot:hover {
            background-color: #e0a800;
            transform: scale(1.05);
        }
        .status {
            margin-top: 30px;
            padding: 15px;
            background-color: #16213e;
            border-radius: 8px;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>Driver IO remote control dashboard</h1>
    <div class="button-container">
        <a href="/boot" class="btn btn-boot">Boot up Pi</a>
        <a href="/reboot" class="btn btn-reboot">Soft Reboot</a>
    </div>
    <div class="status" id="status">
        Ready for commands
    </div>
</body>
</html>"""
    return html


def get_response_page(action):
    """
    Generate a response page after an action is triggered.
    
    Args:
        action: The action that was triggered ('boot' or 'reboot')
        
    Returns:
        str: HTML content
    """
    action_text = "Boot up Pi" if action == "boot" else "Soft Reboot"
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="3;url=/">
    <title>Driver IO remote control dashboard</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #1a1a2e;
            color: #eee;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        h1 {{
            color: #00d4ff;
            margin-bottom: 20px;
        }}
        .message {{
            background-color: #16213e;
            padding: 20px 40px;
            border-radius: 10px;
            text-align: center;
        }}
        .success {{
            color: #28a745;
        }}
    </style>
</head>
<body>
    <h1>Driver IO remote control dashboard</h1>
    <div class="message">
        <p class="success">Command sent: {action_text}</p>
        <p>Redirecting back to dashboard...</p>
    </div>
</body>
</html>"""
    return html


def handle_boot():
    """
    Handle the Boot up Pi action.
    
    This function triggers the GPIO pin to boot up the Raspberry Pi 4.
    """
    print("Boot up Pi command received")
    
    # ========================================================================
    # TODO: Add GPIO control code here to boot up the Raspberry Pi 4
    # ========================================================================
    # Example:
    # BOOT_PIN.value(1)  # Set pin HIGH to trigger boot
    # time.sleep(0.5)    # Hold for 500ms
    # BOOT_PIN.value(0)  # Set pin LOW
    # ========================================================================
    
    pass


def handle_reboot():
    """
    Handle the Soft Reboot action.
    
    This function triggers the GPIO pin to soft reboot the Raspberry Pi 4.
    """
    print("Soft Reboot command received")
    
    # ========================================================================
    # TODO: Add GPIO control code here to soft reboot the Raspberry Pi 4
    # ========================================================================
    # Example:
    # REBOOT_PIN.value(1)  # Set pin HIGH to trigger reboot
    # time.sleep(0.5)      # Hold for 500ms
    # REBOOT_PIN.value(0)  # Set pin LOW
    # ========================================================================
    
    pass


def start_server(ip_address, port=80):
    """
    Start the web server.
    
    Args:
        ip_address: IP address to bind to
        port: Port number (default 80)
    """
    addr = socket.getaddrinfo(ip_address, port)[0][-1]
    
    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(addr)
    server_socket.listen(5)
    
    print(f"Web server running on http://{ip_address}:{port}")
    print("Press Ctrl+C to stop the server")
    
    while True:
        try:
            client, client_addr = server_socket.accept()
            print(f"Connection from {client_addr}")
            
            request = client.recv(1024).decode("utf-8")
            
            # Parse the request to get the path
            path = "/"
            try:
                request_line = request.split("\r\n")[0]
                parts = request_line.split(" ")
                if len(parts) >= 2:
                    path = parts[1]
            except (IndexError, ValueError):
                # Handle malformed requests gracefully
                path = "/"
            
            # Handle different routes
            if path == "/boot":
                handle_boot()
                response = get_response_page("boot")
            elif path == "/reboot":
                handle_reboot()
                response = get_response_page("reboot")
            else:
                response = get_html_page()
            
            # Send HTTP response (combine headers to avoid partial sends)
            http_response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n" + response
            client.sendall(http_response.encode("utf-8"))
            
            client.close()
            
        except Exception as e:
            print(f"Error handling request: {e}")
            try:
                client.close()
            except:
                pass


def main():
    """
    Main entry point for the application.
    """
    print("=" * 50)
    print("Driver IO Remote Control Dashboard")
    print("=" * 50)
    
    # Parse WiFi credentials from config file
    ssid, password = parse_wifi_config()
    
    if not ssid or not password:
        print("Error: Could not read WiFi credentials from wifi_config.txt")
        print("Please ensure the file exists with format:")
        print("SSID=your_wifi_ssid")
        print("PASSWORD=your_wifi_password")
        return
    
    # Connect to WiFi
    ip_address = connect_wifi(ssid, password)
    
    if not ip_address:
        print("Error: Could not connect to WiFi")
        return
    
    # Start the web server
    start_server(ip_address)


# Run the main function when the script is executed
if __name__ == "__main__":
    main()
