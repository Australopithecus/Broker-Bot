from __future__ import annotations

ML_BOT_NAME = "ml"
LLM_BOT_NAME = "llm"
STAT_ARB_BOT_NAME = "stat_arb"
AI_LAB_BOT_NAME = "ai_lab"

BOT_LABELS = {
    ML_BOT_NAME: "ML Bot",
    LLM_BOT_NAME: "LLM Bot",
    STAT_ARB_BOT_NAME: "Stat Arb Bot",
    AI_LAB_BOT_NAME: "AI Lab Bot",
}

ACTIVE_BOT_LABELS = {
    ML_BOT_NAME: BOT_LABELS[ML_BOT_NAME],
    LLM_BOT_NAME: BOT_LABELS[LLM_BOT_NAME],
    AI_LAB_BOT_NAME: BOT_LABELS[AI_LAB_BOT_NAME],
}


def normalize_bot_name(bot_name: str | None) -> str:
    value = (bot_name or ML_BOT_NAME).strip().lower()
    if value not in BOT_LABELS:
        return ML_BOT_NAME
    return value


def is_active_bot_name(bot_name: str | None) -> bool:
    return normalize_bot_name(bot_name) in ACTIVE_BOT_LABELS


def bot_label(bot_name: str | None) -> str:
    return BOT_LABELS.get(normalize_bot_name(bot_name), "ML Bot")
