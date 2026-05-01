from __future__ import annotations

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
from pathlib import Path
import time
from urllib.parse import urlparse
import os
import uuid

from src.ai_client import AIClient, AIClientError
from src.constants import LEVELS
from src.levels import run_level

ROOT = Path(__file__).parent
WEB = ROOT / "web"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("glitch-demo")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _request_id(self) -> str:
        return uuid.uuid4().hex[:12]

    def do_GET(self):
        request_id = self._request_id()
        path = urlparse(self.path).path
        start = time.perf_counter()

        if path == "/api/levels":
            self._send_json(200, {"request_id": request_id, "levels": LEVELS})
            logger.info("request_id=%s path=%s status=200 duration_ms=%.2f", request_id, path, (time.perf_counter() - start) * 1000)
            return

        if path.startswith("/api/run/"):
            level_text = path.split("/")[-1]
            return self._execute_level(level_text, request_id, path, start)

        return super().do_GET()

    def do_POST(self):
        request_id = self._request_id()
        path = urlparse(self.path).path
        start = time.perf_counter()
        if path != "/api/run":
            self._send_json(404, {"request_id": request_id, "error": "not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            level = data.get("level")
        except Exception:
            self._send_json(400, {"request_id": request_id, "error": "invalid JSON payload"})
            return

        self._execute_level(str(level), request_id, path, start)

    def _execute_level(self, level_text: str, request_id: str, path: str, start: float):
        try:
            level = int(level_text)
            if level not in LEVELS:
                raise ValueError("out of range")
            client = AIClient()
            payload = run_level(level, client)
            payload["backend"] = {
                "provider": "OpenAI",
                "configured": client.available(),
                "model": client.model,
                "base_url": client.base_url,
            }
            payload["request_id"] = request_id
            status = 200
            self._send_json(status, payload)
        except ValueError:
            status = 400
            self._send_json(status, {"request_id": request_id, "error": "invalid level"})
        except AIClientError as err:
            status = err.status
            self._send_json(status, {"request_id": request_id, "error": err.message, "code": err.code})
        except Exception:
            status = 500
            self._send_json(status, {"request_id": request_id, "error": "internal error"})

        logger.info(
            "request_id=%s path=%s level=%s status=%s duration_ms=%.2f",
            request_id,
            path,
            level_text,
            status,
            (time.perf_counter() - start) * 1000,
        )


if __name__ == "__main__":
    # Default to 0.0.0.0 so cloud platforms (e.g., Render) can route traffic.
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    print(f"Serving demo at http://{host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
