"""
MicroPython Web Server for Raspberry Pi Pico W
BSR Driver IO Remote Control Dashboard

This script serves a dashboard for remote control of a Raspberry Pi 4.
"""

import network
import socket
import time
from machine import Pin
import sys

# Optional in-memory logo (base64 PNG) loaded from `logo_base64.txt` on the Pico
LOGO_BASE64 = None


def load_logo_base64(filename='logo_base64.txt'):
    """
    Load base64 PNG data from a file on the Pico (no data: prefix expected).
    If the file contains a full data URI (data:image/png;base64,...) the prefix
    will be stripped.
    """
    global LOGO_BASE64
    try:
        with open(filename, 'r') as f:
            data = f.read().strip()
            if not data:
                LOGO_BASE64 = None
                print('Logo file empty')
                return
            # Strip data URI prefix if present
            if data.startswith('data:'):
                comma = data.find(',')
                if comma != -1:
                    data = data[comma+1:]
            LOGO_BASE64 = data
            print('Loaded logo_base64, length=', len(data))
    except Exception as e:
        LOGO_BASE64 = None
        print('logo_base64.txt not found or could not be read:', e)

# ============================================================================
# GPIO PIN CONFIGURATION
# ============================================================================
# GPIO pin 8 connects to Pi 4 BOOT/EEPROM pins (bootloader recovery mode)
BOOT_PIN = 8
# GPIO pin 9 connects to Pi 4 RUN/Reset pins (hardware reset/reboot)
RUN_PIN = 9


def read_driverio_config(filename='driverio_config.txt'):
    """
    Read Driver IO board configuration from file.
    Expected format:
    DRIVERIO_IP=192.168.1.x
    DRIVERIO_USER=username
    DRIVERIO_PASS=password
    
    Returns:
        dict: Configuration with keys 'ip', 'user', 'pass'
    """
    config = {}
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        if key == 'DRIVERIO_IP':
                            config['ip'] = value
                        elif key == 'DRIVERIO_USER':
                            config['user'] = value
                        elif key == 'DRIVERIO_PASS':
                            config['pass'] = value
                        elif key == 'PASSCODE':
                            config['passcode'] = value
    except Exception as e:
        print(f"Error reading Driver IO config: {e}")
    return config


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
    # Build logo HTML if available
    logo_html = ''
    if LOGO_BASE64:
        logo_html = '<img src="data:image/png;base64,' + LOGO_BASE64 + '" alt="BSR Logo" style="width:80px;height:80px;margin-bottom:20px;">'

    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BSR Driver IO Remote Control</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: Arial, sans-serif;
            background-color: #ffffff;
            color: #CC0000;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }
        h1 {
            margin-bottom: 40px;
            text-align: center;
            color: #CC0000;
            font-size: 28px;
        }
        .button-container {
            display: flex;
            flex-direction: column;
            gap: 40px;
            width: 100%;
            max-width: 300px;
        }
        .btn {
            padding: 20px 40px;
            font-size: 18px;
            font-weight: bold;
            border: 3px solid;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            text-align: center;
        }
        .btn-boot {
            background-color: #28a745;
            color: white;
            border-color: #28a745;
        }
        .btn-boot:hover {
            background-color: #218838;
            transform: scale(1.05);
        }
        .btn-status {
            background-color: white;
            color: #CC0000;
            border-color: #CC0000;
        }
        .btn-status:hover {
            background-color: #f0f0f0;
            transform: scale(1.05);
        }
        .btn-reboot {
            background-color: #CC0000;
            color: white;
            border-color: #CC0000;
        }
        .btn-reboot:hover {
            background-color: #A00000;
            transform: scale(1.05);
        }
        .status {
            margin-top: 30px;
            padding: 15px;
            background-color: #f5f5f5;
            border: 2px solid #CC0000;
            border-radius: 8px;
            text-align: center;
            color: #333;
        }
    </style>
    <script>
        function handleAction(action) {
            const passcode = prompt('Enter 6-digit passcode:');
            if (passcode && passcode.length === 6 && /^[0-9]{6}$/.test(passcode)) {
                window.location.href = action + '?passcode=' + passcode;
            } else if (passcode !== null) {
                alert('Invalid passcode. Must be 6 digits.');
            }
            return false;
        }
    </script>
</head>
<body>
    """ + logo_html + """
    <h1>BSR Driver IO Remote Control</h1>
    <div class="button-container">
        <a href="#" onclick="return handleAction('/boot')" class="btn btn-boot">Bootloader Recovery</a>
        <a href="#" onclick="return handleAction('/status')" class="btn btn-status">Check Driver IO Status</a>
        <a href="#" onclick="return handleAction('/reboot')" class="btn btn-reboot">Hardware Reset</a>
    </div>
</body>
</html>"""
    return html


def get_response_page(action):
    """
    Generate a response page after an action is triggered.
    
    Args:
        action: The action that was triggered ('boot', 'reboot', or 'shutdown')
        
    Returns:
        str: HTML content
    """
    # Determine if this is an unauthorized access
    is_unauthorized = (action == "unauthorized")
    
    if action == "boot":
        action_text = "Force Bootloader Recovery Mode"
    elif action == "reboot":
        action_text = "Hardware Reset (RUN)"
    elif action == "status":
        action_text = "Status Check - Driver IO is ONLINE"
    elif action == "status_offline":
        action_text = "Status Check - Driver IO is OFFLINE"
    elif action == "unauthorized":
        action_text = "Invalid Passcode"
    else:
        action_text = "Unknown Action"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="3;url=/">
    <title>BSR Driver IO Remote Control</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #ffffff;
            color: #CC0000;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        h1 {{
            color: #CC0000;
            margin-bottom: 20px;
        }}
        .message {{
            background-color: #f5f5f5;
            border: 2px solid #CC0000;
            padding: 20px 40px;
            border-radius: 10px;
            text-align: center;
        }}
        .success {{
            color: #CC0000;
            font-weight: bold;
        }}
        .error {{
            color: #CC0000;
            font-weight: bold;
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <h1>BSR Driver IO Remote Control</h1>
    <div class="message">"""
    
    if is_unauthorized:
        html += f"""
        <p class="error">ACCESS DENIED</p>
        <p class="success">{action_text}</p>
        <p>No command was executed. Redirecting back to dashboard...</p>"""
    else:
        html += f"""
        <p class="success">Command sent: {action_text}</p>
        <p>Redirecting back to dashboard...</p>"""
    
    html += """
    </div>
</body>
</html>"""
    return html


def verify_passcode(provided_passcode):
    """
    Verify the provided passcode against the configured passcode.
    
    Args:
        provided_passcode: The passcode provided by the user
        
    Returns:
        bool: True if passcode matches, False otherwise
    """
    config = read_driverio_config()
    correct_passcode = config.get('passcode', '')
    
    if not correct_passcode:
        print("WARNING: No passcode configured, allowing access")
        return True
    
    if provided_passcode == correct_passcode:
        print("Passcode verified")
        return True
    else:
        print("Invalid passcode provided")
        return False


def handle_boot():
    """
    Handle the BOOT/EEPROM recovery action.
    
    This function shorts the Pi 4 BOOT/EEPROM pins for ~1 second while powered on
    to force bootloader recovery mode / USB boot mode.
    """
    print("BOOT/EEPROM recovery command received")
    boot_pin = Pin(BOOT_PIN, Pin.OUT)
    boot_pin.value(1)
    time.sleep(1.0)  # Short for ~1 second as per Pi 4 spec
    boot_pin.value(0)
    print("BOOT signal sent (1.0s)")


def handle_reboot():
    """
    Handle the RUN/Reset action.
    
    This function shorts the Pi 4 RUN/Reset pins for ~0.3 seconds
    to trigger an immediate hardware reset (same as power-cycle).
    """
    print("RUN/Reset command received")
    reboot_pin = Pin(RUN_PIN, Pin.OUT)
    reboot_pin.value(1)
    time.sleep(0.3)  # Short for 0.1-0.5s as per Pi 4 spec (using 0.3s middle value)
    reboot_pin.value(0)
    print("RUN/Reset signal sent (0.3s)")


def handle_status():
    """
    Handle the Status Check action.
    
    This function checks if the Driver IO (Pi 4) board is online and reachable.
    Does NOT trigger any GPIO pins or perform any actions.
    """
    print("Status check command received")
    
    # Read Driver IO config
    config = read_driverio_config()
    
    if not config.get('ip'):
        print("Error: Driver IO IP not configured in driverio_config.txt")
        return False
    
    driverio_ip = config['ip']
    driverio_user = config.get('user', 'pi')
    driverio_pass = config.get('pass', '')
    
    print(f"Attempting to shutdown Driver IO at {driverio_ip}")
    
    # Try to test connectivity to the Driver IO board
    try:
        # Create a socket to test connectivity on SSH port
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_sock.settimeout(5)
        result = test_sock.connect_ex((driverio_ip, 22))  # Test SSH port
        test_sock.close()
        
        if result == 0:
            print(f"Driver IO at {driverio_ip} is ONLINE and reachable")
            print("Boot sequence successful - Pi 4 is responding")
            return True
        else:
            print(f"Driver IO at {driverio_ip} is OFFLINE or not reachable")
            return False
            
    except Exception as e:
        print(f"Error connecting to Driver IO: {e}")
        sys.print_exception(e)
        return False


def start_server(ip_address, port=80):
    """
    Start the web server.
    
    Args:
        ip_address: IP address to bind to
        port: Port number (default 80)
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', port))
    server_socket.listen(5)
    
    print(f"Web server running on http://{ip_address}:{port}")
    print("Press Ctrl+C to stop the server")
    
    while True:
        try:
            client, client_addr = server_socket.accept()
            print(f"Connection from {client_addr}")
            
            request = client.recv(1024).decode("utf-8")
            
            # Parse the request to get the path
            try:
                request_line = request.split("\r\n")[0]
                print(f"Request: {request_line}")
                
                # Extract passcode from query string
                passcode = None
                if '?passcode=' in request_line:
                    try:
                        passcode = request_line.split('?passcode=')[1].split(' ')[0]
                    except:
                        pass
                
                if request_line.startswith('GET /boot'):
                    print("Boot endpoint hit")
                    if verify_passcode(passcode):
                        handle_boot()
                        response = get_response_page('boot')
                    else:
                        response = get_response_page('unauthorized')
                elif request_line.startswith('GET /reboot'):
                    print("Reboot endpoint hit")
                    if verify_passcode(passcode):
                        handle_reboot()
                        response = get_response_page('reboot')
                    else:
                        response = get_response_page('unauthorized')
                elif request_line.startswith('GET /status'):
                    print("Status check endpoint hit")
                    if verify_passcode(passcode):
                        success = handle_status()
                        response = get_response_page('status' if success else 'status_offline')
                    else:
                        response = get_response_page('unauthorized')
                else:
                    response = get_html_page()
            except (IndexError, ValueError):
                response = get_html_page()
            
            # Send HTTP response
            http_response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n" + response
            client.sendall(http_response.encode("utf-8"))
            client.close()
            
        except Exception as e:
            print(f"Error handling request: {e}")
            sys.print_exception(e)
            try:
                client.close()
            except:
                pass


def main():
    """
    Main entry point for the application.
    """
    try:
        print("=" * 50)
        print("BSR Driver IO Remote Control Dashboard")
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
        
        # Load optional logo (base64) if present on the Pico
        load_logo_base64('logo_base64.txt')

        # Start the web server
        start_server(ip_address)
        
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        sys.print_exception(e)


# Run the main function when the script is executed
if __name__ == "__main__":
    main()
