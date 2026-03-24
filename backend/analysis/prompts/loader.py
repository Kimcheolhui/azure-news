"""Load prompt templates from YAML files."""

from __future__ import annotations

from pathlib import Path

import yaml

_PROMPT_DIR = Path(__file__).parent


def load_prompt(name: str) -> dict[str, str]:
    """Load a prompt YAML file and return its contents as a dict.

    Each YAML file should have ``system`` and ``user`` keys.
    """
    path = _PROMPT_DIR / f"{name}.yml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)
