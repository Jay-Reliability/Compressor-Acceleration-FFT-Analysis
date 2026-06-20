import http.server
import socketserver
import webbrowser
import threading
import os
import sys

# http://localhost:8000/Compressor_Acceleration_Analysis.html
PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    # Use log_message override to silence stdout noise in python server logs
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            print(f"\n[SERVER] Serving HTTP on port {PORT}...")
            print(f"[SERVER] Dashboard URL: http://localhost:{PORT}/Compressor_Acceleration_Analysis.html")
            httpd.serve_forever()
    except Exception as e:
        print(f"\n[SERVER ERROR] Failed to start HTTP server: {e}")

if __name__ == "__main__":
    # Start server in background thread so launcher doesn't block shell
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait half a second for server to initialize, then launch browser
    import time
    time.sleep(0.5)
    
    dashboard_url = f"http://localhost:{PORT}/Compressor_Acceleration_Analysis.html"
    print(f"\n[LAUNCHER] Opening web browser: {dashboard_url}")
    webbrowser.open(dashboard_url)
    
    print("\n-------------------------------------------------------------")
    print("Press Ctrl+C in this terminal window to stop the local server.")
    print("-------------------------------------------------------------")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[LAUNCHER] Shutting down local web server...")
        sys.exit(0)
