from __future__ import annotations

from .models import EvolutionState


class EvolutionEngine:
    def record_feedback(self, state: EvolutionState, feedback: str) -> str:
        state.append_feedback(feedback)
        suggestion = (
            "Promote latest feedback into roadmap: "
            f"{feedback.strip() or 'No feedback text provided.'}"
        )
        state.append_improvement(suggestion)
        return suggestion
