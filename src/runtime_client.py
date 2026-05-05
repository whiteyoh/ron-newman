from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.ai_client import AIClientError

SAFE_PLACEHOLDER = (
    "[AI call failed safely. No external action was taken. "
    "Check model access, quota, billing, or OPENAI_MODEL.]"
)


@dataclass
class RuntimeAIError:
    message: str
    code: str
    status: int


class AIClientLike(Protocol):
    def available(self) -> bool: ...

    def chat(self, system: str, user: str, temperature: float = 0.2) -> str: ...


class CapturedAIClient:
    def __init__(self, inner: AIClientLike) -> None:
        self.inner = inner
        self.model = getattr(inner, "model", "")
        self.base_url = getattr(inner, "base_url", "")
        self.errors: list[RuntimeAIError] = []

    def available(self) -> bool:
        return self.inner.available()

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    def chat(self, system: str, user: str, temperature: float = 0.2) -> str:
        try:
            return self.inner.chat(system, user, temperature=temperature)
        except AIClientError as err:
            self.errors.append(
                RuntimeAIError(message=str(err.message), code=str(err.code), status=int(err.status))
            )
            return SAFE_PLACEHOLDER
        except Exception:
            self.errors.append(
                RuntimeAIError(
                    message="Unexpected AI runtime error during model call.",
                    code="ai_runtime_error",
                    status=500,
                )
            )
            return SAFE_PLACEHOLDER
