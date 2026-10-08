"""
Mock Student API Server
-----------------------
A lightweight local REST API created using Python's standard library (http.server).
Exposes the endpoint `GET /students` and returns student test scores in JSON format.
Requires no external frameworks.

Author: Vimlesh Tiwari
"""

import http.server
import json
import socketserver
import sys

HOST = "127.0.0.1"
PORT = 8000

STUDENTS_DATA = [
    {"name": "Rahul", "score": 85},
    {"name": "Aman", "score": 72},
    {"name": "Priya", "score": 91},
    {"name": "Neha", "score": 78}
]


class StudentRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    HTTP Request Handler serving student test-score data.
    """

    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path == "/students" or self.path == "/students/":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            response_body = json.dumps(STUDENTS_DATA, indent=2)
            self.wfile.write(response_body.encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            error_body = json.dumps({"error": "Endpoint not found. Use GET /students"})
            self.wfile.write(error_body.encode("utf-8"))

    def log_message(self, format_str: str, *args: object) -> None:
        """Custom logging for clean terminal output."""
        print(f"[API SERVER] {self.address_string()} - {format_str % args}")


def run_server(host: str = HOST, port: int = PORT) -> None:
    """
    Start the standard-library HTTP server.
    """
    # Allow quick restart on the same port
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer((host, port), StudentRequestHandler) as httpd:
        print(f"==================================================")
        print(f"[*] Mock Student API running at: http://{host}:{port}/students")
        print(f"[*] Press Ctrl+C to stop the server.")
        print(f"==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[!] Shutting down Mock API server...")
        finally:
            httpd.server_close()
            print("[+] Server stopped safely.")


if __name__ == "__main__":
    run_server()
