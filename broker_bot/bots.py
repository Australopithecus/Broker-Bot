from __future__ import annotations

ML_BOT_NAME = "ml"
LLM_BOT_NAME = "llm"

BOT_LABELS = {
    ML_BOT_NAME: "ML Bot",
    LLM_BOT_NAME: "LLM Bot",
}


def normalize_bot_name(bot_name: str | None) -> str:
    value = (bot_name or ML_BOT_NAME).strip().lower()
    if value not in BOT_LABELS:
        return ML_BOT_NAME
    return value


def bot_label(bot_name: str | None) -> str:
    return BOT_LABELS.get(normalize_bot_name(bot_name), "ML Bot")
