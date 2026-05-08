from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .bots import AI_LAB_BOT_NAME, bot_label
from .config import Config
from .data import fetch_daily_bars
from .logging_db import read_recent_evaluated_decisions
from .risk import classify_market_regime
from .trader import OrderLogRow, Signal, execute_signals


AI_LAB_REPORT_TYPE = "ai_lab_daily"
AI_LAB_COMPONENTS = (
    "ai_trend",
    "ai_reversal",
    "ai_breakout",
    "ai_volume_confirmation",
    "ai_low_volatility",
    "ai_market_alignment",
)


@dataclass
class AILabRunResult:
    ts: str
    orders: list[OrderLogRow]
    signals: list[Signal]
    decision_context: dict
    report: dict


def _clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
    except Exception:
        return default
    return result if math.isfinite(result) else default


def _load_json(path: str) -> dict:
    policy_path = Path(path)
    if not path or not policy_path.exists():
        return {}
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _default_policy(config: Config) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": "Initial AI Lab Bot policy.",
        "min_abs_score": float(config.ai_lab_min_abs_score),
        "sleeve_weights": {
            "ai_trend": 1.0,
            "ai_reversal": 0.45,
            "ai_breakout": 0.75,
            "ai_volume_confirmation": 0.35,
            "ai_low_volatility": 0.25,
            "ai_market_alignment": 0.65,
        },
        "learning": {
            "last_update": None,
            "sample_count": 0,
            "component_edges": {},
        },
    }


def _load_policy(config: Config) -> dict[str, Any]:
    policy = _default_policy(config)
    loaded = _load_json(config.ai_lab_policy_path)
    if isinstance(loaded.get("sleeve_weights"), dict):
        for name, value in loaded["sleeve_weights"].items():
            if name in AI_LAB_COMPONENTS:
                policy["sleeve_weights"][name] = _clip(_safe_float(value, policy["sleeve_weights"][name]), 0.0, 2.5)
    if "min_abs_score" in loaded:
        policy["min_abs_score"] = _clip(_safe_float(loaded["min_abs_score"], config.ai_lab_min_abs_score), 0.0, 0.05)
    if isinstance(loaded.get("learning"), dict):
        policy["learning"] = loaded["learning"]
    return policy


def _write_policy(config: Config, policy: dict[str, Any]) -> None:
    out_path = Path(config.ai_lab_policy_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(policy, indent=2, sort_keys=True), encoding="utf-8")


def _parse_components(payload: str | None) -> dict[str, float]:
    if not payload:
        return {}
    try:
        parsed = json.loads(payload)
    except Exception:
        return {}
    if not isinstance(parsed, dict):
        return {}
    clean: dict[str, float] = {}
    for key, value in parsed.items():
        if key in AI_LAB_COMPONENTS:
            clean[key] = _safe_float(value)
    return clean


def _update_policy_from_outcomes(config: Config, policy: dict[str, Any]) -> tuple[dict[str, Any], list[str], dict[str, Any]]:
    rows = read_recent_evaluated_decisions(config.db_path, limit=300, bot_name=AI_LAB_BOT_NAME)
    if not rows:
        _write_policy(config, policy)
        return policy, ["No evaluated AI Lab decisions yet; policy unchanged."], {"evaluated_sample_count": 0.0}

    sleeve_weights = dict(policy.get("sleeve_weights", {}))
    component_stats: dict[str, list[float]] = {name: [] for name in AI_LAB_COMPONENTS}
    signed_returns = []
    for _, side, _, _, signed_return, _, beat_spy, components_json in rows:
        signed = _safe_float(signed_return)
        signed_returns.append(signed)
        direction = 1.0 if str(side).upper() == "LONG" else -1.0
        components = _parse_components(components_json)
        alpha_or_return = _safe_float(beat_spy, signed)
        for name, value in components.items():
            # Positive value means this sleeve supported the chosen side and that choice later paid.
            component_stats[name].append(direction * float(value) * alpha_or_return)

    changes: list[str] = []
    component_edges: dict[str, float] = {}
    for name, values in component_stats.items():
        if len(values) < 8:
            continue
        edge = sum(values) / len(values)
        component_edges[name] = edge
        old_weight = _safe_float(sleeve_weights.get(name), 1.0)
        step = 0.0
        if edge > 0.000015:
            step = 0.08
        elif edge < -0.000015:
            step = -0.08
        if step == 0.0:
            continue
        new_weight = round(_clip(old_weight + step, 0.0, 2.5), 3)
        if abs(new_weight - old_weight) > 1e-9:
            sleeve_weights[name] = new_weight
            changes.append(f"{name} weight {old_weight:.3f} -> {new_weight:.3f} from outcome edge {edge:+.6f}.")

    avg_signed = sum(signed_returns) / len(signed_returns)
    old_threshold = _safe_float(policy.get("min_abs_score"), config.ai_lab_min_abs_score)
    new_threshold = old_threshold
    if len(signed_returns) >= 20 and avg_signed < -0.0025:
        new_threshold = _clip(old_threshold + 0.00075, 0.0, 0.05)
    elif len(signed_returns) >= 20 and avg_signed > 0.0035:
        new_threshold = _clip(old_threshold - 0.0005, 0.0, 0.05)
    if abs(new_threshold - old_threshold) > 1e-9:
        policy["min_abs_score"] = round(new_threshold, 6)
        changes.append(f"min_abs_score {old_threshold:.4f} -> {new_threshold:.4f} from avg signed return {avg_signed:+.2%}.")

    policy["sleeve_weights"] = sleeve_weights
    policy["generated_at"] = datetime.now(timezone.utc).isoformat()
    policy["summary"] = "AI Lab Bot policy updated from mature decision outcomes."
    policy["learning"] = {
        "last_update": datetime.now(timezone.utc).isoformat(),
        "sample_count": len(signed_returns),
        "avg_signed_return": avg_signed,
        "component_edges": component_edges,
    }
    _write_policy(config, policy)
    if not changes:
        changes = ["Outcome evidence did not clear bounded update thresholds; policy unchanged."]
    return policy, changes, {
        "evaluated_sample_count": float(len(signed_returns)),
        "recent_avg_signed_return": float(avg_signed),
        "component_edges": component_edges,
    }


def _centered_rank(series: pd.Series) -> pd.Series:
    return series.rank(pct=True).fillna(0.5) - 0.5


def _latest_feature_frame(bars: pd.DataFrame, config: Config) -> tuple[pd.DataFrame, dict[str, Any]]:
    df = bars.copy().sort_values(["Symbol", "timestamp"])
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df["high"] = pd.to_numeric(df.get("high"), errors="coerce")
    df["volume"] = pd.to_numeric(df.get("volume", 0.0), errors="coerce").fillna(0.0)
    grouped = df.groupby("Symbol", group_keys=False)
    df["return_5d"] = grouped["close"].pct_change(5)
    df["return_20d"] = grouped["close"].pct_change(20)
    df["return_60d"] = grouped["close"].pct_change(60)
    df["vol_20d"] = grouped["close"].pct_change().groupby(df["Symbol"]).rolling(20).std().reset_index(level=0, drop=True)
    df["high_60d"] = grouped["high"].rolling(60).max().reset_index(level=0, drop=True)
    df["dollar_vol"] = df["close"] * df["volume"]
    df["dollar_vol_20d"] = grouped["dollar_vol"].rolling(20).mean().reset_index(level=0, drop=True)
    df["volume_ratio"] = df["dollar_vol"] / df["dollar_vol_20d"].replace(0, pd.NA)

    latest_ts = pd.to_datetime(df["timestamp"], errors="coerce", utc=True).max()
    latest = df[pd.to_datetime(df["timestamp"], errors="coerce", utc=True) == latest_ts].copy()
    latest = latest[latest["Symbol"] != "SPY"].copy()
    if config.min_price > 0:
        latest = latest[latest["close"] >= config.min_price]
    if config.min_dollar_vol > 0:
        latest = latest[latest["dollar_vol_20d"] >= config.min_dollar_vol]
    latest = latest.sort_values("dollar_vol_20d", ascending=False).head(max(config.ai_lab_symbol_limit, 10)).copy()

    vol = latest["vol_20d"].replace(0, pd.NA)
    trend_input = (0.65 * latest["return_20d"].fillna(0.0) + 0.35 * latest["return_60d"].fillna(0.0)) / vol.fillna(0.02)
    trend_rank = _centered_rank(trend_input)
    reversal_rank = -_centered_rank(latest["return_5d"].fillna(0.0) / vol.fillna(0.02))
    breakout_rank = _centered_rank((latest["close"] / latest["high_60d"].replace(0, pd.NA) - 1.0).fillna(0.0))
    volume_rank = _centered_rank(latest["volume_ratio"].fillna(1.0)) * trend_rank.apply(lambda value: 1.0 if value >= 0 else -1.0)
    low_vol_rank = -_centered_rank(latest["vol_20d"].fillna(latest["vol_20d"].median()))

    spy = df[df["Symbol"] == "SPY"].sort_values("timestamp")
    spy_ret_20 = _safe_float(spy["close"].pct_change(20).iloc[-1]) if len(spy) > 25 else 0.0
    spy_ret_60 = _safe_float(spy["close"].pct_change(60).iloc[-1]) if len(spy) > 70 else 0.0
    if spy_ret_20 > 0.015 and spy_ret_60 > 0:
        market_alignment = trend_rank
        market_mode = "risk_on_momentum"
    elif spy_ret_20 < -0.015 or spy_ret_60 < -0.03:
        market_alignment = -trend_rank
        market_mode = "risk_off_defensive"
    else:
        market_alignment = 0.6 * reversal_rank + 0.4 * low_vol_rank
        market_mode = "range_bound_adaptive"

    latest["ai_trend_raw"] = trend_rank
    latest["ai_reversal_raw"] = reversal_rank
    latest["ai_breakout_raw"] = breakout_rank
    latest["ai_volume_confirmation_raw"] = volume_rank
    latest["ai_low_volatility_raw"] = low_vol_rank
    latest["ai_market_alignment_raw"] = market_alignment
    return latest, {
        "latest_ts": latest_ts.isoformat() if not pd.isna(latest_ts) else None,
        "spy_return_20d": spy_ret_20,
        "spy_return_60d": spy_ret_60,
        "market_mode": market_mode,
    }


def _signals_from_features(latest: pd.DataFrame, policy: dict[str, Any], config: Config) -> tuple[list[Signal], dict[str, Any]]:
    weights = policy.get("sleeve_weights", {})
    scale = 0.022
    scored = latest.copy()
    component_columns = {
        "ai_trend": "ai_trend_raw",
        "ai_reversal": "ai_reversal_raw",
        "ai_breakout": "ai_breakout_raw",
        "ai_volume_confirmation": "ai_volume_confirmation_raw",
        "ai_low_volatility": "ai_low_volatility_raw",
        "ai_market_alignment": "ai_market_alignment_raw",
    }
    scored["ai_score"] = 0.0
    for component_name, raw_column in component_columns.items():
        contribution = scale * _safe_float(weights.get(component_name), 1.0) * pd.to_numeric(scored[raw_column], errors="coerce").fillna(0.0)
        scored[component_name] = contribution
        scored["ai_score"] += contribution

    threshold = _clip(_safe_float(policy.get("min_abs_score"), config.ai_lab_min_abs_score), 0.0, 0.05)
    longs = scored[scored["ai_score"] >= threshold].sort_values("ai_score", ascending=False).head(max(config.ai_lab_max_long_positions, 0))
    shorts = scored[scored["ai_score"] <= -threshold].sort_values("ai_score", ascending=True).head(max(config.ai_lab_max_short_positions, 0))
    selected_symbols = set(longs["Symbol"]).union(set(shorts["Symbol"]))
    exploration_rows: list[tuple[str, pd.Series]] = []
    total_slots = max(config.ai_lab_max_long_positions, 0) + max(config.ai_lab_max_short_positions, 0)
    exploration_slots = min(2, max(0, int(round(total_slots * _clip(config.ai_lab_exploration_rate, 0.0, 0.5)))))
    if exploration_slots and threshold > 0:
        long_slots_used = int(len(longs))
        short_slots_used = int(len(shorts))
        borderline = scored[
            (~scored["Symbol"].isin(selected_symbols))
            & (scored["ai_score"].abs() >= threshold * 0.55)
            & (scored["ai_score"].abs() < threshold)
        ].copy()
        borderline["abs_score"] = borderline["ai_score"].abs()
        for _, row in borderline.sort_values("abs_score", ascending=False).iterrows():
            if len(exploration_rows) >= exploration_slots:
                break
            score = float(row["ai_score"])
            if score > 0 and long_slots_used < max(config.ai_lab_max_long_positions, 0):
                exploration_rows.append(("LONG", row))
                long_slots_used += 1
                selected_symbols.add(row["Symbol"])
            elif score < 0 and short_slots_used < max(config.ai_lab_max_short_positions, 0):
                exploration_rows.append(("SHORT", row))
                short_slots_used += 1
                selected_symbols.add(row["Symbol"])

    signals: list[Signal] = []
    for side, rows in [("LONG", longs), ("SHORT", shorts)]:
        for _, row in rows.iterrows():
            components = {name: float(row.get(name, 0.0)) for name in component_columns}
            score = float(row["ai_score"])
            signals.append(
                Signal(
                    symbol=str(row["Symbol"]),
                    score=score,
                    side=side,
                    vol=_safe_float(row.get("vol_20d"), 0.02),
                    base_score=score,
                    selected=True,
                    components=components,
                    rationale=(
                        "AI Lab composite selected this "
                        f"{side.lower()} from adaptive sleeves: "
                        + ", ".join(f"{name.replace('ai_', '')}={value:+.4f}" for name, value in components.items() if abs(value) >= 0.0001)
                    ),
                )
            )

    for side, row in exploration_rows:
        components = {name: float(row.get(name, 0.0)) for name in component_columns}
        score = float(row["ai_score"])
        signals.append(
            Signal(
                symbol=str(row["Symbol"]),
                score=score,
                side=side,
                vol=_safe_float(row.get("vol_20d"), 0.02),
                base_score=score,
                selected=True,
                components=components,
                rationale=(
                    "AI Lab controlled-exploration slot selected this "
                    f"{side.lower()} despite a borderline score so the policy can learn from near-threshold ideas."
                ),
            )
        )

    selected_abs_scores = [abs(signal.score) for signal in signals if signal.selected]
    execution_threshold = min([threshold, *selected_abs_scores]) if selected_abs_scores else threshold
    for _, row in scored.iterrows():
        if row["Symbol"] in selected_symbols:
            continue
        components = {name: float(row.get(name, 0.0)) for name in component_columns}
        score = float(row["ai_score"])
        signals.append(
            Signal(
                symbol=str(row["Symbol"]),
                score=score,
                side="HOLD",
                vol=_safe_float(row.get("vol_20d"), 0.02),
                base_score=score,
                selected=False,
                components=components,
                rationale="AI Lab composite did not clear the adaptive entry threshold.",
            )
        )

    return signals, {
        "threshold": threshold,
        "execution_threshold": execution_threshold,
        "long_count": int(len(longs) + sum(1 for side, _ in exploration_rows if side == "LONG")),
        "short_count": int(len(shorts) + sum(1 for side, _ in exploration_rows if side == "SHORT")),
        "exploration_count": int(len(exploration_rows)),
        "top_longs": [
            {"symbol": str(row["Symbol"]), "score": float(row["ai_score"])}
            for _, row in longs.head(8).iterrows()
        ],
        "top_shorts": [
            {"symbol": str(row["Symbol"]), "score": float(row["ai_score"])}
            for _, row in shorts.head(8).iterrows()
        ],
        "exploration": [
            {"symbol": str(row["Symbol"]), "side": side, "score": float(row["ai_score"])}
            for side, row in exploration_rows
        ],
    }


def _report_for_run(
    ts: str,
    context: dict[str, Any],
    policy_changes: list[str],
    policy_metrics: dict[str, Any],
    config: Config,
) -> dict[str, Any]:
    headline = f"{bot_label(AI_LAB_BOT_NAME)} Daily Design Report"
    selected_long_count = int(context.get("selected_long_count", 0))
    selected_short_count = int(context.get("selected_short_count", 0))
    summary = (
        f"Selected {selected_long_count} long(s) and {selected_short_count} short(s) "
        "from the AI-designed adaptive sleeve ensemble."
    )
    top_longs = context.get("top_longs", []) if isinstance(context.get("top_longs"), list) else []
    top_shorts = context.get("top_shorts", []) if isinstance(context.get("top_shorts"), list) else []
    exploration = context.get("exploration", []) if isinstance(context.get("exploration"), list) else []
    policy = context.get("ai_lab_policy", {}) if isinstance(context.get("ai_lab_policy"), dict) else {}
    sleeve_weights = policy.get("sleeve_weights", {}) if isinstance(policy.get("sleeve_weights"), dict) else {}
    lines = [
        f"# {headline}",
        "",
        summary,
        "",
        "## Design",
        "- This model is intentionally AI-designed and AI-updated rather than a fixed supervised model or pure LLM trader.",
        "- It blends six sleeves: trend, short-term reversal, breakout, volume confirmation, low-volatility preference, and market-regime alignment.",
        "- Mature outcomes update sleeve weights and the adaptive entry threshold in `data/ai_lab_policy.json` within strict bounds.",
        "",
        "## Current policy",
        f"- Minimum absolute AI score: {float(policy.get('min_abs_score', config.ai_lab_min_abs_score)):.4f}.",
        f"- Execution confidence gate this run: {float(context.get('confidence_gate_override', policy.get('min_abs_score', config.ai_lab_min_abs_score))):.4f}.",
        *[f"- {name}: weight {float(value):.3f}." for name, value in sorted(sleeve_weights.items())],
        "",
        "## Top selected longs",
        *([f"- {row['symbol']}: score {float(row['score']):+.4f}." for row in top_longs] or ["- None."]),
        "",
        "## Top selected shorts",
        *([f"- {row['symbol']}: score {float(row['score']):+.4f}." for row in top_shorts] or ["- None."]),
        "",
        "## Controlled exploration",
        *(
            [
                f"- {row['symbol']} {str(row['side']).lower()}: score {float(row['score']):+.4f}."
                for row in exploration
            ]
            or ["- None this run."]
        ),
        "",
        "## Self-updates this run",
        *[f"- {item}" for item in policy_changes],
        "",
        "## Outcome-learning metrics",
        json.dumps(policy_metrics, indent=2, sort_keys=True),
    ]
    body = "\n".join(lines)
    reports_dir = Path(config.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"ai_lab_daily_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(body, encoding="utf-8")
    return {
        "ts": ts,
        "report_type": AI_LAB_REPORT_TYPE,
        "headline": headline,
        "summary": summary,
        "body": body,
        "metrics": {
            "selected_long_count": float(selected_long_count),
            "selected_short_count": float(selected_short_count),
            "threshold": float(policy.get("min_abs_score", config.ai_lab_min_abs_score)),
            "execution_threshold": float(context.get("confidence_gate_override", policy.get("min_abs_score", config.ai_lab_min_abs_score))),
            "exploration_count": float(len(exploration)),
            "policy_sample_count": float(policy_metrics.get("evaluated_sample_count", 0.0) or 0.0),
            "recent_avg_signed_return": policy_metrics.get("recent_avg_signed_return"),
        },
        "changes": {
            "policy_changes": policy_changes,
            "policy_path": config.ai_lab_policy_path,
            "sleeve_weights": sleeve_weights,
        },
        "report_path": str(report_path),
    }


def rebalance_ai_lab_bot(config: Config, symbols: list[str]) -> AILabRunResult:
    policy = _load_policy(config)
    policy, policy_changes, policy_metrics = _update_policy_from_outcomes(config, policy)
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=max(config.ai_lab_lookback_days, 120) + 20)
    universe = list(dict.fromkeys([symbol for symbol in symbols if symbol != "SPY"]))
    bars = fetch_daily_bars(config, universe + ["SPY"], start, end, bot_name=AI_LAB_BOT_NAME).bars
    latest, feature_context = _latest_feature_frame(bars, config)
    if latest.empty:
        raise RuntimeError("AI Lab Bot could not find enough liquid symbols to score.")

    signals, signal_context = _signals_from_features(latest, policy, config)
    spy_df = bars[bars["Symbol"] == "SPY"]
    regime = classify_market_regime(
        spy_df,
        gross_leverage=config.gross_leverage,
        bear_leverage=config.bear_leverage,
        vol_target=config.vol_target,
        vol_window=config.vol_window,
    )
    latest_prices = latest[["Symbol", "close"]].copy()
    context = {
        "strategy": "ai_lab_adaptive_sleeve_ensemble",
        "candidate_count": int(len(latest)),
        "selected_long_count": int(signal_context["long_count"]),
        "selected_short_count": int(signal_context["short_count"]),
        "top_longs": signal_context["top_longs"],
        "top_shorts": signal_context["top_shorts"],
        "exploration": signal_context["exploration"],
        "exploration_count": int(signal_context["exploration_count"]),
        "confidence_gate_override": float(signal_context["execution_threshold"]),
        "ai_lab_policy_threshold": float(signal_context["threshold"]),
        "ai_lab_policy": {
            "min_abs_score": float(policy.get("min_abs_score", config.ai_lab_min_abs_score)),
            "sleeve_weights": policy.get("sleeve_weights", {}),
            "learning": policy.get("learning", {}),
        },
        "ai_lab_policy_changes": policy_changes,
        "ai_lab_policy_metrics": policy_metrics,
        "feature_context": feature_context,
        "market_regime": {"label": regime.label, "notes": regime.notes},
    }
    ts, orders, executed_signals, decision_context = execute_signals(
        config,
        latest_prices,
        signals,
        regime.leverage,
        regime.spy_vol,
        context,
        bot_name=AI_LAB_BOT_NAME,
    )
    report = _report_for_run(ts, decision_context, policy_changes, policy_metrics, config)
    return AILabRunResult(ts=ts, orders=orders, signals=executed_signals, decision_context=decision_context, report=report)
