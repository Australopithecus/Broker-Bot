from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


COMPONENT_COLUMNS = [
    "technical_adjustment",
    "snapshot_adjustment",
    "screener_adjustment",
    "news_adjustment",
    "memory_adjustment",
    "llm_adjustment",
]

DEFAULT_COMPONENT_SCALES = {name: 1.0 for name in COMPONENT_COLUMNS}


def _clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def load_component_scales(policy_path: str) -> dict[str, float]:
    scales = dict(DEFAULT_COMPONENT_SCALES)
    if not policy_path or not Path(policy_path).exists():
        return scales

    try:
        payload = json.loads(Path(policy_path).read_text(encoding="utf-8"))
    except Exception:
        return scales

    raw_scales = payload.get("component_scales") if isinstance(payload, dict) else None
    if not isinstance(raw_scales, dict):
        return scales

    for name in COMPONENT_COLUMNS:
        try:
            scales[name] = round(_clip(float(raw_scales.get(name, 1.0)), 0.4, 1.6), 3)
        except Exception:
            scales[name] = 1.0
    return scales


def derive_component_scales(component_metrics: dict[str, dict[str, float]]) -> dict[str, float]:
    scales: dict[str, float] = {}
    for name in COMPONENT_COLUMNS:
        stats = component_metrics.get(name) or {}
        samples = float(stats.get("samples", 0.0))
        if samples < 8:
            scales[name] = 1.0
            continue

        edge = float(stats.get("edge", 0.0))
        hit_rate = float(stats.get("hit_rate", 0.5))
        confidence = min(1.0, samples / 40.0)
        edge_term = _clip(edge / 0.006, -1.0, 1.0) * 0.30
        hit_term = _clip((hit_rate - 0.5) / 0.25, -1.0, 1.0) * 0.20
        scales[name] = round(_clip(1.0 + confidence * (edge_term + hit_term), 0.4, 1.6), 3)
    return scales


def apply_component_scales(frame: pd.DataFrame, scales: dict[str, float] | None) -> pd.DataFrame:
    if "base_pred_return" not in frame.columns:
        return frame

    active_scales = scales or DEFAULT_COMPONENT_SCALES
    adjusted = frame.copy()
    for name in COMPONENT_COLUMNS:
        if name not in adjusted.columns:
            continue
        adjusted[name] = adjusted[name].astype(float) * float(active_scales.get(name, 1.0))

    available = [name for name in COMPONENT_COLUMNS if name in adjusted.columns]
    adjusted["pred_return"] = adjusted["base_pred_return"].astype(float)
    if available:
        adjusted["pred_return"] = adjusted["pred_return"] + adjusted[available].sum(axis=1)
    return adjusted
