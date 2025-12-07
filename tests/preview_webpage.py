#!/usr/bin/env python3
"""
Preview the Pico web interface locally before flashing.
This creates a simple HTTP server that serves the HTML from main.py
"""

import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Add parent directory to path to import main.py functions
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Read the logo base64 data
LOGO_BASE64 = None
try:
    with open('logo_base64.txt', 'r') as f:
        data = f.read().strip()
        if data.startswith('data:'):
            comma = data.find(',')
            if comma != -1:
                data = data[comma+1:]
        LOGO_BASE64 = data
        print(f"✓ Loaded logo ({len(data)} bytes)")
except:
    print("⚠ No logo_base64.txt found (optional)")

def get_html_page():
    """Generate the main dashboard HTML"""
    logo_html = ''
    if LOGO_BASE64:
        logo_html = f'<img src="data:image/png;base64,{LOGO_BASE64}" alt="BSR Logo" style="width:80px;height:80px;margin-bottom:20px;">'

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
            background-color: #000000;
            color: #FFFFFF;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }
        h1 {
            margin-bottom: 40px;
            text-align: center;
            color: #FFFFFF;
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
            background-color: #FF0000;
            color: white;
            border-color: #FF0000;
        }
        .btn-status:hover {
            background-color: #CC0000;
            transform: scale(1.05);
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
        <a href="#" onclick="return handleAction('/boot')" class="btn btn-boot">⏻ Boot up Pi</a>
        <a href="#" onclick="return handleAction('/status')" class="btn btn-status">ــہہـ٨ــ Check Driver IO Status</a>
    </div>
</body>
</html>"""
    return html


def get_response_page(action, passcode_correct=True):
    """Generate response page for preview"""
    is_unauthorized = not passcode_correct
    
    if action == "boot":
        action_text = "Boot up Pi - RUN Pin Triggered"
    elif action == "status":
        action_text = "Status Check - Driver IO is ONLINE"
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
            background-color: #000000;
            color: #FFFFFF;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        h1 {{
            color: #FFFFFF;
            margin-bottom: 20px;
        }}
        .message {{
            background-color: #1a1a1a;
            border: 2px solid #FFFFFF;
            padding: 20px 40px;
            border-radius: 10px;
            text-align: center;
        }}
        .success {{
            color: #28a745;
            font-weight: bold;
        }}
        .error {{
            color: #FF0000;
            font-weight: bold;
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <h1>BSR Driver IO Remote Control</h1>
    <div class="message">"""
    
    if is_unauthorized:
        html += """
        <p class="error">INCORRECT PASSCODE</p>
        <p>Access denied. Redirecting back to dashboard...</p>"""
    else:
        html += f"""
        <p class="success">Command sent: {action_text}</p>
        <p>Redirecting back to dashboard...</p>"""
    
    html += """
    </div>
</body>
</html>"""
    return html


class PreviewHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[{self.address_string()}] {format % args}")

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)
        
        # Extract passcode if provided
        passcode = query.get('passcode', [None])[0]
        
        if path == '/boot':
            # Simulate boot response (check if passcode is 123456 for demo)
            passcode_correct = (passcode == '123456')
            html = get_response_page('boot', passcode_correct)
        elif path == '/status':
            # Simulate status response
            passcode_correct = (passcode == '123456')
            html = get_response_page('status', passcode_correct)
        else:
            # Main dashboard
            html = get_html_page()
        
        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))


def main():
    """Start preview server"""
    port = 8080
    server = HTTPServer(('localhost', port), PreviewHandler)
    
    print("=" * 60)
    print("🌐 Pico Web Interface Preview Server")
    print("=" * 60)
    print(f"\n✓ Server running at: http://localhost:{port}")
    print(f"✓ Test passcode: 123456")
    print(f"\n📝 Press Ctrl+C to stop the server\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped")
        server.shutdown()


if __name__ == '__main__':
    main()
