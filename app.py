from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from dataclasses import dataclass
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from src.ai_client import AIClient, AIClientError
from src.constants import LEVELS, USE_CASE_OPTIONS
from src.levels import run_level

ROOT = Path(__file__).parent
WEB = ROOT / "web"
MAX_BODY_BYTES = 16 * 1024
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 20
_rate_limit_store: dict[str, list[float]] = {}
_rate_limit_lock = threading.Lock()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("glytch-demo")


@dataclass
class RunRequest:
    level: int
    use_case: str
    use_case_context: str


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(WEB), **kwargs)

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _request_id(self) -> str:
        return uuid.uuid4().hex[:12]

    def _validation_error(self, request_id: str, error: str, code: str, field: str | None = None) -> None:
        payload: dict[str, Any] = {"request_id": request_id, "error": error, "code": code}
        if field:
            payload["field"] = field
        self._send_json(400, payload)

    def _check_rate_limit(self, request_id: str) -> bool:
        ip = self.client_address[0] if self.client_address else "unknown"
        now = time.time()
        with _rate_limit_lock:
            window = [t for t in _rate_limit_store.get(ip, []) if now - t < RATE_LIMIT_WINDOW_SECONDS]
            if len(window) >= RATE_LIMIT_MAX_REQUESTS:
                self._send_json(429, {"request_id": request_id, "error": "rate limit exceeded", "code": "rate_limited"})
                return False
            window.append(now)
            _rate_limit_store[ip] = window
        return True

    def do_GET(self) -> None:
        request_id = self._request_id()
        path = urlparse(self.path).path
        start = time.perf_counter()
        if path == "/healthz":
            self._send_json(200, {"status": "ok"})
            return
        if path == "/api/levels":
            self._send_json(200, {"request_id": request_id, "levels": LEVELS})
            return
        if path == "/api/use-cases":
            self._send_json(200, {"request_id": request_id, "use_cases": USE_CASE_OPTIONS})
            return
        if path.startswith("/api/run/"):
            return self._execute_level(path.split("/")[-1], request_id, path, start)
        if path.startswith("/assets/"):
            self.path = path
            return SimpleHTTPRequestHandler.do_GET(self)
        return super().do_GET()

    def _parse_run_request(self, request_id: str) -> RunRequest | None:
        content_type = self.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            self._validation_error(request_id, "content type must be application/json", "invalid_content_type", "Content-Type")
            return None
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._validation_error(request_id, "invalid content length", "invalid_content_length", "Content-Length")
            return None
        if length <= 0:
            self._validation_error(request_id, "request body is required", "missing_body")
            return None
        if length > MAX_BODY_BYTES:
            self._send_json(413, {"request_id": request_id, "error": "request body too large", "code": "body_too_large"})
            return None
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._validation_error(request_id, "invalid JSON payload", "invalid_json")
            return None
        if not isinstance(data, dict):
            self._validation_error(request_id, "JSON object expected", "invalid_schema")
            return None
        level = data.get("level")
        if not isinstance(level, int):
            self._validation_error(request_id, "level must be an integer", "invalid_field", "level")
            return None
        use_case = data.get("use_case", "uk_year10_teacher")
        use_case_context = data.get("use_case_context", "")
        return RunRequest(level=level, use_case=str(use_case), use_case_context=str(use_case_context))

    def do_POST(self) -> None:
        request_id = self._request_id()
        path = urlparse(self.path).path
        start = time.perf_counter()
        if path != "/api/run":
            self._send_json(404, {"request_id": request_id, "error": "not found", "code": "not_found"})
            return
        if not self._check_rate_limit(request_id):
            return
        parsed = self._parse_run_request(request_id)
        if parsed is None:
            return
        self._execute_level(str(parsed.level), request_id, path, start, parsed.use_case, parsed.use_case_context)

    def _execute_level(self, level_text: str, request_id: str, path: str, start: float, use_case_key: str = "uk_year10_teacher", use_case_context: str = "") -> None:
        status = 200
        try:
            level = int(level_text)
            if level not in LEVELS:
                raise ValueError("out of range")
            client = AIClient()
            payload = run_level(level, client, use_case_key=use_case_key, use_case_context=use_case_context)
            payload["backend"] = {"provider": "OpenAI", "configured": client.available(), "model": client.model, "base_url": client.base_url}
            payload["request_id"] = request_id
            self._send_json(status, payload)
        except ValueError:
            status = 400
            self._send_json(status, {"request_id": request_id, "error": "invalid level", "code": "invalid_level", "field": "level"})
        except AIClientError as err:
            status = err.status
            self._send_json(status, {"request_id": request_id, "error": err.message, "code": err.code})
        except Exception:
            status = 500
            self._send_json(status, {"request_id": request_id, "error": "internal error", "code": "internal_error"})
        logger.info("request_id=%s path=%s level=%s status=%s duration_ms=%.2f", request_id, path, level_text, status, (time.perf_counter() - start) * 1000)


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    print(f"Serving demo at http://{host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
