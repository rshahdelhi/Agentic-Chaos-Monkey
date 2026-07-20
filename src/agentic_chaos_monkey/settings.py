from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class GeminiSettings:
    api_key: str
    model: str

    @classmethod
    def from_environment(cls) -> "GeminiSettings":
        # Google's clients accept both names and prefer GOOGLE_API_KEY if both
        # exist. Mirror that precedence so validation matches runtime behavior.
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Set GEMINI_API_KEY (or GOOGLE_API_KEY) before running the ADK agent."
            )
        return cls(
            api_key=api_key,
            model=os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
        )


def gemini_model_name() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-flash-latest")
