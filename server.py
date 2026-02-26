"""
Nano Banana Pro - Image Generation Server

Usage:
  1. Set your API key:
       export GEMINI_API_KEY="your-api-key-here"
  2. Run the server:
       python server.py
  3. Open http://localhost:8080 in your browser
"""

import http.server
import json
import os
import sys
import urllib.request
import urllib.error

API_KEY = os.environ.get("GEMINI_API_KEY", "")
PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

HTML_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nanobananapro.html")


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(HTML_FILE, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/api/generate":
            self.send_error(404)
            return

        if not API_KEY:
            self._json_response(500, {"error": "Server API key is not configured."})
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-3-pro-image-preview:generateContent?key={API_KEY}"
        )

        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
                self._json_response(200, json.loads(data))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            try:
                error_json = json.loads(error_body)
                msg = error_json.get("error", {}).get("message", error_body)
            except json.JSONDecodeError:
                msg = error_body
            self._json_response(e.code, {"error": msg})
        except Exception as e:
            self._json_response(500, {"error": str(e)})

    def _json_response(self, code, obj):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode("utf-8"))

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    if not API_KEY:
        print("WARNING: GEMINI_API_KEY is not set!")
        print("  export GEMINI_API_KEY=\"your-api-key-here\"")
        print()

    server = http.server.HTTPServer((HOST, PORT), Handler)
    print(f"Nano Banana Pro server running at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
