"""Copilot SDK client wrapper for analysis pipeline."""

from __future__ import annotations

import os

from copilot import CopilotClient, PermissionHandler


async def create_analysis_session(
    model: str = "gpt-5.4",
    tools: list | None = None,
    system_message: str | None = None,
):
    """Create a Copilot SDK session configured for analysis work."""
    client = CopilotClient()
    await client.start()

    provider_config = {
        "type": "openai",
        "base_url": os.environ.get(
            "OPENAI_BASE_URL", "https://api.openai.com/v1"
        ),
        "api_key": os.environ["OPENAI_API_KEY"],
    }

    session_config = {
        "model": model,
        "provider": provider_config,
        "on_permission_request": PermissionHandler.approve_all,
    }

    if tools:
        session_config["tools"] = tools
    if system_message:
        session_config["system_message"] = {"content": system_message}

    session = await client.create_session(session_config)
    return client, session
