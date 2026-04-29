from __future__ import annotations

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlparse

from src.ai_client import AIClient
from src.constants import LEVELS
from src.levels import run_level

ROOT = Path(__file__).parent
WEB = ROOT / "web"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/levels":
            body = json.dumps(LEVELS).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path.startswith("/api/run/"):
            try:
                level = int(path.split("/")[-1])
                if level not in LEVELS:
                    raise ValueError("out of range")
                payload = run_level(level, AIClient())
            except Exception as err:
                self.send_error(400, f"Invalid level or execution error: {err}")
                return
            body = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        return super().do_GET()


if __name__ == "__main__":
    host, port = "127.0.0.1", 8000
    print(f"Serving demo at http://{host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
