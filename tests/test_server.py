"""
Minimal web server test
"""

import socket
import network

print("Starting minimal web server test...")

# Check WiFi
wlan = network.WLAN(network.STA_IF)
if wlan.isconnected():
    ip = wlan.ifconfig()[0]
    print(f"WiFi connected: {ip}")
else:
    print("ERROR: Not connected to WiFi")

# Try to create socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 80))
    s.listen(5)
    print(f"Server listening on {ip}:80")
    print("Waiting for connection...")
    
    # Accept one connection
    conn, addr = s.accept()
    print(f"Got connection from {addr}")
    conn.send(b'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n<h1>IT WORKS!</h1>')
    conn.close()
    s.close()
    print("Test complete!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import sys
    sys.print_exception(e)
