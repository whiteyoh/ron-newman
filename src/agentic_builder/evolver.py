from __future__ import annotations

import re

from .models import EvolutionState


class EvolutionEngine:
    THEME_RULES = {
        "security": {"security", "auth", "permissions", "policy", "vuln"},
        "performance": {"performance", "latency", "speed", "optimize", "fast"},
        "testing": {"test", "coverage", "qa", "regression"},
        "ux": {"ux", "ui", "chat", "streamlit", "experience"},
    }

    PRIORITY_RULES = {
        "P0": {"urgent", "critical", "blocker", "immediately"},
        "P1": {"important", "soon", "high", "must"},
    }

    def record_feedback(self, state: EvolutionState, feedback: str) -> str:
        normalized_feedback = feedback.strip()
        state.append_feedback(feedback)
        theme = self._classify_theme(normalized_feedback)
        priority = self._classify_priority(normalized_feedback)
        display_feedback = normalized_feedback or "No feedback text provided."
        backlog_key = self._feedback_key(display_feedback)
        backlog_item = f"[{priority}/{theme}] {display_feedback}"
        change_kind = state.upsert_backlog_item(backlog_key, backlog_item)

        if change_kind == "existing":
            suggestion = (
                "Feedback already tracked; escalating visibility in roadmap: "
                f"{backlog_item}"
            )
        else:
            suggestion = f"Promote latest feedback into roadmap: {backlog_item}"

        suggestion = (
            f"{suggestion}. "
            f"Backlog now contains {len(state.backlog)} unique item(s)."
        )
        state.append_improvement(suggestion)
        return suggestion

    def _classify_theme(self, feedback: str) -> str:
        text = feedback.lower()
        for theme, words in self.THEME_RULES.items():
            if any(word in text for word in words):
                return theme
        return "general"

    def _classify_priority(self, feedback: str) -> str:
        text = feedback.lower()
        for priority, words in self.PRIORITY_RULES.items():
            if any(word in text for word in words):
                return priority
        return "P2"

    def _feedback_key(self, feedback: str) -> str:
        return re.sub(r"\s+", " ", feedback).strip().lower()
