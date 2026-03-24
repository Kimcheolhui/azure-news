"""Prompt templates for the report writing step — loaded from writing.yml."""

from analysis.prompts.loader import load_prompt

_prompts = load_prompt("writing")

WRITING_SYSTEM_PROMPT: str = _prompts["system"]
WRITING_USER_TEMPLATE: str = _prompts["user"]
