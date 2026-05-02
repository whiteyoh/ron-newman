from __future__ import annotations

from typing import Protocol


class AIChatClient(Protocol):
    model: str
    base_url: str

    def available(self) -> bool: ...

    def chat(self, system: str, user: str, temperature: float = 0.2) -> str: ...
