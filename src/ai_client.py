import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class AIClientError(Exception):
    message: str
    code: str
    status: int = 500


class AIClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        # Keep a broadly available default model for CI/service accounts.
        # gpt-4.1-mini is generally enabled on newer projects/accounts.
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    def available(self) -> bool:
        return bool(self.api_key)

    def chat(self, system: str, user: str, temperature: float = 0.2) -> str:
        if not self.available():
            raise AIClientError("OPENAI_API_KEY is not set", code="missing_api_key", status=503)

        payload = {
            "model": self.model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        request = Request(
            url=f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                body: dict[str, Any] = json.loads(response.read().decode("utf-8"))
        except HTTPError as err:
            detail = ""
            try:
                detail = err.read().decode("utf-8", errors="ignore").strip()
            except Exception:
                detail = ""
            message = f"upstream HTTP error: {err.code}"
            if detail:
                message = f"{message} ({detail[:300]})"
            raise AIClientError(message, code="upstream_http", status=502) from err
        except URLError as err:
            raise AIClientError(f"connection error: {err.reason}", code="upstream_connection", status=502) from err
        except TimeoutError as err:
            raise AIClientError("upstream timeout", code="upstream_timeout", status=504) from err

        try:
            return body["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError, AttributeError) as err:
            raise AIClientError("unexpected upstream response shape", code="upstream_schema", status=502) from err
