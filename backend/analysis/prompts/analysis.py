"""Prompt templates for the analysis step — loaded from analysis.yml."""

from analysis.prompts.loader import load_prompt

_prompts = load_prompt("analysis")

ANALYSIS_SYSTEM_PROMPT: str = _prompts["system"]
ANALYSIS_USER_TEMPLATE: str = _prompts["user"]
