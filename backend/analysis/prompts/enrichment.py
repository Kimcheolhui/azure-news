"""Prompts for the update enrichment pipeline — loaded from enrichment.yml."""

from __future__ import annotations

from ingest.enums import UPDATE_TYPES, CATEGORIES

from analysis.prompts.loader import load_prompt

_prompts = load_prompt("enrichment")

_UPDATE_TYPE_LIST = ", ".join(UPDATE_TYPES)
_CATEGORY_LIST = ", ".join(CATEGORIES)

ENRICHMENT_SYSTEM_PROMPT: str = _prompts["system"]
ENRICHMENT_USER_TEMPLATE: str = _prompts["user"]


def build_enrichment_prompt(
    title: str,
    body: str | None,
    source_name: str,
    published_date: str | None,
) -> str:
    body_text = body or "(no content)"
    if len(body_text) > 3000:
        body_text = body_text[:3000] + "..."

    return ENRICHMENT_USER_TEMPLATE.format(
        title=title,
        body=body_text,
        source_name=source_name,
        published_date=published_date or "unknown",
        update_types=_UPDATE_TYPE_LIST,
        categories=_CATEGORY_LIST,
    )
