from __future__ import annotations

import json
import threading
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

from app import Handler


def _serve(server: ThreadingHTTPServer) -> None:
    server.serve_forever()


def _request(
    port: int,
    method: str,
    path: str,
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
):
    conn = HTTPConnection("127.0.0.1", port, timeout=5)
    conn.request(method, path, body=body, headers=headers or {})
    resp = conn.getresponse()
    data = resp.read()
    conn.close()
    return resp.status, data


def test_http_endpoints() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_port
    t = threading.Thread(target=_serve, args=(server,), daemon=True)
    t.start()
    try:
        status, data = _request(port, "GET", "/healthz")
        assert status == 200 and json.loads(data)["status"] == "ok"

        status, data = _request(port, "GET", "/api/levels")
        assert status == 200 and "levels" in json.loads(data)

        status, data = _request(port, "GET", "/api/use-cases")
        assert status == 200 and "use_cases" in json.loads(data)

        status, data = _request(
            port,
            "POST",
            "/api/run",
            json.dumps({"level": 1}).encode(),
            {"Content-Type": "application/json"},
        )
        payload = json.loads(data)
        assert status == 200 and any("not configured" in line.lower() for line in payload["lines"])

        status, _ = _request(
            port, "POST", "/api/run", b"{bad", {"Content-Type": "application/json"}
        )
        assert status == 400
        status, _ = _request(
            port,
            "POST",
            "/api/run",
            json.dumps({"level": 99}).encode(),
            {"Content-Type": "application/json"},
        )
        assert status == 400
        status, _ = _request(
            port,
            "POST",
            "/api/run",
            json.dumps({"level": 1}).encode(),
            {"Content-Type": "text/plain"},
        )
        assert status == 400
        status, _ = _request(
            port, "POST", "/api/run", b"x" * (17 * 1024), {"Content-Type": "application/json"}
        )
        assert status == 413
    finally:
        server.shutdown()
        server.server_close()
