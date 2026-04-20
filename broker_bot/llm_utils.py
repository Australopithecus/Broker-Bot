from __future__ import annotations

import json
import os
from typing import Any

from .config import Config


def llm_is_available(config: Config) -> bool:
    return config.llm_enabled and bool(os.getenv("OPENAI_API_KEY", "").strip())


def call_json_llm(
    config: Config,
    system_prompt: str,
    payload: dict[str, Any],
    max_output_tokens: int = 700,
) -> dict[str, Any] | None:
    if not llm_is_available(config):
        return None

    try:
        from openai import OpenAI
    except Exception:
        return None

    client = OpenAI()
    try:
        response = client.responses.create(
            model=config.llm_model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(payload, sort_keys=True)},
            ],
            max_output_tokens=max_output_tokens,
        )
    except Exception:
        return None

    text = getattr(response, "output_text", "") or ""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    try:
        parsed = json.loads(text[start : end + 1])
    except Exception:
        return None
    return parsed if isinstance(parsed, dict) else None
