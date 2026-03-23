from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class AnalysisSettings:
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-5.4"
    max_tokens_per_report: int = 8000
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> AnalysisSettings:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is required")
        return cls(
            openai_api_key=api_key,
            openai_base_url=os.environ.get(
                "OPENAI_BASE_URL", "https://api.openai.com/v1"
            ),
            model=os.environ.get("ANALYSIS_MODEL", "gpt-5.4"),
            max_tokens_per_report=int(
                os.environ.get("MAX_TOKENS_PER_REPORT", "8000")
            ),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
        )
