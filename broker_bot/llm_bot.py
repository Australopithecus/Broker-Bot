from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pandas as pd

from .bots import LLM_BOT_NAME, bot_label
from .config import Config
from .learning import _evaluate_pending_decisions, _load_components
from .llm_utils import call_json_llm, llm_is_available
from .logging_db import (
    log_decision_outcomes,
    log_strategy_report,
    read_latest_strategy_reports,
    read_pending_decision_logs,
    read_recent_evaluated_decisions,
    read_recent_selected_decisions,
)
from .trader import OrderLogRow, Signal, execute_signals, generate_signals


MAX_WATCHLIST = 8


@dataclass
class LlmBotRunResult:
    ts: str
    orders: list[OrderLogRow]
    signals: list[Signal]
    decision_context: dict


def _round_pct(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


def _bounded_float(value: object, default: float, low: float, high: float) -> float:
    try:
        parsed = float(value)
    except Exception:
        parsed = default
    return max(low, min(parsed, high))


def _parse_pct_value(value: object, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except Exception:
        parsed = default
    if parsed > 1.0:
        parsed /= 100.0
    return max(0.0, parsed)


def _safe_text_list(values: object, limit: int = 4) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, (list, tuple, set)):
        values = [values]
    cleaned: list[str] = []
    for value in values:
        text = str(value).strip()
        if not text:
            continue
        cleaned.append(text)
        if len(cleaned) >= limit:
            break
    return cleaned


def _serialize_candidate(row: dict, research: dict) -> dict:
    symbol = row["symbol"]
    return {
        "symbol": symbol,
        "side": row["side"],
        "base_score": _round_pct(row["base_score"]),
        "final_score": _round_pct(row["final_score"]),
        "vol_20d": _round_pct(row["vol"]),
        "components": row["components"],
        "rationale": row["rationale"],
        "headlines": ((research.get("news_headlines") or {}).get(symbol) or [])[:3],
        "snapshot_score": (research.get("snapshot_scores") or {}).get(symbol),
    }


def _fallback_watchlist(candidates: list[dict]) -> tuple[list[str], str]:
    ranked = sorted(candidates, key=lambda row: abs(float(row["final_score"])), reverse=True)
    selected = [row["symbol"] for row in ranked[:MAX_WATCHLIST]]
    return selected, "Fallback selector used the strongest existing candidate scores."


def _select_watchlist(config: Config, candidates: list[dict], research: dict) -> tuple[list[str], str]:
    if not candidates:
        return [], "No candidates available."
    if not llm_is_available(config):
        return _fallback_watchlist(candidates)

    payload = {
        "objective": "Select a concentrated watchlist for an aggressive but explainable paper-trading bot.",
        "max_watchlist_size": MAX_WATCHLIST,
        "candidates": [_serialize_candidate(row, research) for row in candidates[:14]],
        "output_format": {
            "watchlist_symbols": ["AAPL", "MSFT"],
            "summary": "brief explanation"
        },
    }
    response = call_json_llm(
        config,
        system_prompt=(
            "You are the Stock Selector for a paper-trading bot. "
            "Return JSON only. Select a watchlist that is focused, tradable, and diverse enough to avoid one-theme overconcentration. "
            "Use only the supplied evidence."
        ),
        payload=payload,
        max_output_tokens=1200,
    )
    if not response:
        return _fallback_watchlist(candidates)

    symbols = []
    for value in response.get("watchlist_symbols", []):
        symbol = str(value).strip().upper()
        if symbol and symbol not in symbols and any(row["symbol"] == symbol for row in candidates):
            symbols.append(symbol)
        if len(symbols) >= MAX_WATCHLIST:
            break
    if not symbols:
        return _fallback_watchlist(candidates)
    summary = str(response.get("summary", "")).strip() or "LLM selector chose the watchlist from current candidates."
    return symbols, summary


def _build_fallback_analyst_report(row: dict, research: dict, prediction_horizon_days: int) -> dict:
    symbol = row["symbol"]
    headlines = ((research.get("news_headlines") or {}).get(symbol) or [])[:3]
    thesis = [
        f"Model-implied direction is {row['side']} with final score {row['final_score']:.2%}.",
        f"Recent component mix: {', '.join(f'{k}={float(v):+.4f}' for k, v in row['components'].items() if abs(float(v)) >= 0.0001) or 'no material overlay adjustments'}.",
    ]
    risks = [
        "The signal could be overfit to recent momentum or event noise.",
        "New information could quickly invalidate the current setup.",
    ]
    current_events = headlines or ["No recent Alpaca headlines were available in the configured lookback window."]
    return {
        "symbol": symbol,
        "market_analysis": f"{symbol} is being monitored as a {row['side']} candidate based on the current signal stack.",
        "historical_trends": thesis[0],
        "current_events": current_events,
        "catalysts": ["Recent signal strength and market-data overlays put this name on the watchlist."],
        "contrary_evidence": ["The setup may be mostly model-driven if current news is thin."],
        "time_horizon": f"{max(prediction_horizon_days, 1)} trading day(s)",
        "confidence": 0.55,
        "outlook": row["rationale"] or "No extra rationale recorded.",
        "risks": risks,
    }


def _analyst_reports(config: Config, watchlist: list[dict], research: dict) -> list[dict]:
    if not watchlist:
        return []
    if not llm_is_available(config):
        return [_build_fallback_analyst_report(row, research, config.prediction_horizon_days) for row in watchlist]

    payload = {
        "objective": "Write a daily analyst memo for each watchlist stock.",
        "watchlist": [_serialize_candidate(row, research) for row in watchlist],
        "output_format": {
            "reports": [
                {
                    "symbol": "ticker",
                    "market_analysis": "paragraph",
                    "historical_trends": "paragraph",
                    "current_events": ["bullet", "bullet"],
                    "catalysts": ["bullet", "bullet"],
                    "contrary_evidence": ["bullet", "bullet"],
                    "time_horizon": "short phrase",
                    "confidence": 0.65,
                    "outlook": "paragraph",
                    "risks": ["bullet", "bullet"],
                }
            ]
        },
    }
    response = call_json_llm(
        config,
        system_prompt=(
            "You are the Analyst for a paper-trading bot. "
            "Return JSON only. For each stock, write an informative daily memo using only the supplied evidence. "
            "Be concrete about current events, historical pattern, thesis, catalysts, contrary evidence, and risks."
        ),
        payload=payload,
        max_output_tokens=2600,
    )
    if not response or not isinstance(response.get("reports"), list):
        return [_build_fallback_analyst_report(row, research, config.prediction_horizon_days) for row in watchlist]

    reports_by_symbol = {
        row["symbol"]: _build_fallback_analyst_report(row, research, config.prediction_horizon_days)
        for row in watchlist
    }
    for item in response.get("reports", []):
        if not isinstance(item, dict):
            continue
        symbol = str(item.get("symbol", "")).strip().upper()
        if symbol not in reports_by_symbol:
            continue
        reports_by_symbol[symbol] = {
            "symbol": symbol,
            "market_analysis": str(item.get("market_analysis", "")).strip() or reports_by_symbol[symbol]["market_analysis"],
            "historical_trends": str(item.get("historical_trends", "")).strip() or reports_by_symbol[symbol]["historical_trends"],
            "current_events": _safe_text_list(item.get("current_events", [])) or reports_by_symbol[symbol]["current_events"],
            "catalysts": _safe_text_list(item.get("catalysts", [])) or reports_by_symbol[symbol]["catalysts"],
            "contrary_evidence": _safe_text_list(item.get("contrary_evidence", [])) or reports_by_symbol[symbol]["contrary_evidence"],
            "time_horizon": str(item.get("time_horizon", "")).strip() or reports_by_symbol[symbol]["time_horizon"],
            "confidence": _bounded_float(item.get("confidence", reports_by_symbol[symbol]["confidence"]), reports_by_symbol[symbol]["confidence"], 0.0, 1.0),
            "outlook": str(item.get("outlook", "")).strip() or reports_by_symbol[symbol]["outlook"],
            "risks": _safe_text_list(item.get("risks", [])) or reports_by_symbol[symbol]["risks"],
        }
    return [reports_by_symbol[row["symbol"]] for row in watchlist]


def _coach_report_body(coach_report: dict) -> str:
    lines = [
        f"# {bot_label(LLM_BOT_NAME)} Coach Report",
        "",
        coach_report["summary"],
        "",
        "## Strengths",
        *[f"- {item}" for item in coach_report.get("strengths", [])],
        "",
        "## Mistakes",
        *[f"- {item}" for item in coach_report.get("mistakes", [])],
        "",
        "## Adjustments for Trader",
        *[f"- {item}" for item in coach_report.get("adjustments", [])],
        "",
        "## Trader Prompt Guidance",
        coach_report.get("trader_guidance", ""),
    ]
    return "\n".join(lines).strip() + "\n"


def generate_llm_coach_report(config: Config) -> dict:
    cutoff_ts = (datetime.now(timezone.utc) - timedelta(days=max(config.prediction_horizon_days, 1) + 1)).isoformat()
    pending_rows = read_pending_decision_logs(config.db_path, cutoff_ts=cutoff_ts, limit=1200, bot_name=LLM_BOT_NAME)
    evaluated_rows = _evaluate_pending_decisions(config, pending_rows, bot_name=LLM_BOT_NAME) if pending_rows else []
    if evaluated_rows:
        log_decision_outcomes(config.db_path, evaluated_rows)

    recent_outcomes = read_recent_evaluated_decisions(config.db_path, limit=25, bot_name=LLM_BOT_NAME)
    fallback = {
        "headline": "LLM Coach Report",
        "summary": (
            f"Reviewed {len(recent_outcomes)} mature LLM decisions and evaluated {len(evaluated_rows)} new outcomes this run."
            if recent_outcomes or evaluated_rows
            else "The LLM bot does not have enough mature outcomes yet, so the coach is staying cautious."
        ),
        "strengths": ["Use concise theses tied to actual evidence rather than broad market storytelling."],
        "mistakes": ["Avoid overreacting to a small number of recent wins or losses."],
        "adjustments": ["Prefer clearer setups where the thesis, catalyst, and risk are all explicit."],
        "trader_guidance": "Trade only when the analyst memo is specific, balanced, and supported by recent evidence.",
    }
    if not recent_outcomes:
        body = _coach_report_body(fallback)
        log_strategy_report(
            config.db_path,
            datetime.now(timezone.utc).isoformat(),
            "coach",
            fallback["headline"],
            fallback["summary"],
            body,
            json.dumps({"evaluated_now": len(evaluated_rows), "recent_outcome_count": 0}, sort_keys=True),
            json.dumps({}, sort_keys=True),
            bot_name=LLM_BOT_NAME,
        )
        return fallback

    if not llm_is_available(config):
        body = _coach_report_body(fallback)
        log_strategy_report(
            config.db_path,
            datetime.now(timezone.utc).isoformat(),
            "coach",
            fallback["headline"],
            fallback["summary"],
            body,
            json.dumps({"evaluated_now": len(evaluated_rows), "recent_outcome_count": len(recent_outcomes)}, sort_keys=True),
            json.dumps({}, sort_keys=True),
            bot_name=LLM_BOT_NAME,
        )
        return fallback

    payload = {
        "objective": "Coach the LLM trader based on recent paper-trading outcomes.",
        "recent_outcomes": [
            {
                "symbol": row[0],
                "side": row[1],
                "evaluated_ts": row[2],
                "realized_return": _round_pct(row[3]),
                "signed_return": _round_pct(row[4]),
                "spy_return": _round_pct(row[5]),
                "beat_spy": _round_pct(row[6]),
                "components": _load_components(row[7]),
            }
            for row in recent_outcomes[:18]
        ],
        "output_format": {
            "headline": "short title",
            "summary": "short paragraph",
            "strengths": ["bullet"],
            "mistakes": ["bullet"],
            "adjustments": ["bullet"],
            "trader_guidance": "concise guidance for tomorrow's trader prompt",
        },
    }
    response = call_json_llm(
        config,
        system_prompt=(
            "You are the Coach for a paper-trading bot. "
            "Return JSON only. Identify what the trader is doing well, what is going poorly, and what should change next. "
            "Be specific, evidence-bound, and constructive. Recommend behavior changes only when multiple outcomes support the pattern."
        ),
        payload=payload,
        max_output_tokens=1800,
    ) or fallback

    coach_report = {
        "headline": str(response.get("headline", fallback["headline"])).strip() or fallback["headline"],
        "summary": str(response.get("summary", fallback["summary"])).strip() or fallback["summary"],
        "strengths": _safe_text_list(response.get("strengths", [])) or fallback["strengths"],
        "mistakes": _safe_text_list(response.get("mistakes", [])) or fallback["mistakes"],
        "adjustments": _safe_text_list(response.get("adjustments", [])) or fallback["adjustments"],
        "trader_guidance": str(response.get("trader_guidance", fallback["trader_guidance"])).strip() or fallback["trader_guidance"],
    }
    body = _coach_report_body(coach_report)
    log_strategy_report(
        config.db_path,
        datetime.now(timezone.utc).isoformat(),
        "coach",
        coach_report["headline"],
        coach_report["summary"],
        body,
        json.dumps({"evaluated_now": len(evaluated_rows), "recent_outcome_count": len(recent_outcomes)}, sort_keys=True),
        json.dumps({}, sort_keys=True),
        bot_name=LLM_BOT_NAME,
    )
    return coach_report


def _fallback_trader_decisions(watchlist: list[dict], coach_report: dict) -> tuple[list[dict], str]:
    ranked = sorted(watchlist, key=lambda row: abs(float(row["final_score"])), reverse=True)
    selected: list[dict] = []
    for row in ranked[: max(4, min(len(ranked), 6))]:
        if row["side"] not in {"LONG", "SHORT"}:
            continue
        selected.append(
            {
                "symbol": row["symbol"],
                "side": row["side"],
                "conviction": 0.6,
                "expected_upside_pct": abs(float(row["final_score"])) * 2.0,
                "expected_downside_pct": max(float(row.get("vol", 0.02)), 0.01),
                "time_horizon": "short swing",
                "why_now": row["rationale"] or "Current model score ranks highly among available candidates.",
                "disconfirming_evidence": "Fallback trader did not receive a full LLM contradiction review.",
                "thesis": row["rationale"] or coach_report.get("trader_guidance", ""),
                "risk_note": "Fallback trader used existing model direction with moderate conviction.",
            }
        )
    return selected, "Fallback trader used the strongest watchlist directions with moderate conviction."


def _trader_decisions(config: Config, watchlist: list[dict], analyst_reports: list[dict], coach_report: dict) -> tuple[list[dict], str]:
    if not watchlist:
        return [], "No watchlist candidates were available for the trader."
    if not llm_is_available(config):
        return _fallback_trader_decisions(watchlist, coach_report)

    payload = {
        "objective": "Turn analyst reports into today's trading decisions.",
        "constraints": {
            "max_positions": min(len(watchlist), max(4, config.rebalance_top_k)),
            "allowed_sides": ["LONG", "SHORT", "HOLD"],
            "paper_trading": True,
            "same_execution_framework_as_ml_bot": True,
        },
        "coach_guidance": coach_report.get("trader_guidance", ""),
        "watchlist_reports": analyst_reports,
        "output_format": {
            "summary": "brief explanation",
            "decisions": [
                {
                    "symbol": "ticker",
                    "side": "LONG",
                    "conviction": 0.7,
                    "expected_upside_pct": 0.03,
                    "expected_downside_pct": 0.015,
                    "time_horizon": "1-5 trading days",
                    "why_now": "one sentence",
                    "disconfirming_evidence": "one sentence",
                    "thesis": "one sentence",
                    "risk_note": "one sentence",
                }
            ],
        },
    }
    response = call_json_llm(
        config,
        system_prompt=(
            "You are the Trader for a paper-trading bot. "
            "Return JSON only. Read the analyst reports and coach guidance, then choose which stocks to trade today. "
            "Be selective, explicit about thesis, why-now timing, expected upside/downside, disconfirming evidence, and risk. "
            "Avoid inventing facts not present in the reports."
        ),
        payload=payload,
        max_output_tokens=2200,
    )
    if not response:
        return _fallback_trader_decisions(watchlist, coach_report)

    allowed = {row["symbol"] for row in watchlist}
    decisions: list[dict] = []
    for item in response.get("decisions", []):
        if not isinstance(item, dict):
            continue
        symbol = str(item.get("symbol", "")).strip().upper()
        side = str(item.get("side", "")).strip().upper()
        if symbol not in allowed or side not in {"LONG", "SHORT"}:
            continue
        try:
            conviction = float(item.get("conviction", 0.5))
        except Exception:
            conviction = 0.5
        expected_upside = _parse_pct_value(item.get("expected_upside_pct", 0.0))
        expected_downside = _parse_pct_value(item.get("expected_downside_pct", 0.0))
        decisions.append(
            {
                "symbol": symbol,
                "side": side,
                "conviction": max(0.05, min(conviction, 1.0)),
                "expected_upside_pct": min(expected_upside, 0.50),
                "expected_downside_pct": min(expected_downside, 0.50),
                "time_horizon": str(item.get("time_horizon", "")).strip(),
                "why_now": str(item.get("why_now", "")).strip(),
                "disconfirming_evidence": str(item.get("disconfirming_evidence", "")).strip(),
                "thesis": str(item.get("thesis", "")).strip(),
                "risk_note": str(item.get("risk_note", "")).strip(),
            }
        )
    if not decisions:
        return _fallback_trader_decisions(watchlist, coach_report)
    return decisions, str(response.get("summary", "")).strip() or "LLM trader selected today's trades from the analyst reports."


def _apply_llm_conviction_gate(config: Config, decisions: list[dict]) -> tuple[list[dict], list[dict]]:
    min_conviction = max(float(config.llm_min_conviction), 0.0)
    if min_conviction <= 0:
        return decisions, []

    passed: list[dict] = []
    gated: list[dict] = []
    for decision in decisions:
        conviction = float(decision.get("conviction", 0.0) or 0.0)
        if conviction < min_conviction:
            removed = dict(decision)
            removed["gate_reason"] = f"Conviction {conviction:.2f} was below minimum {min_conviction:.2f}."
            gated.append(removed)
            continue
        passed.append(decision)
    return passed, gated


def _fallback_skeptic_review(config: Config, decisions: list[dict], analyst_reports: list[dict]) -> dict:
    analyst_by_symbol = {str(report.get("symbol", "")).upper(): report for report in analyst_reports}
    reviews: list[dict] = []
    for decision in decisions:
        symbol = decision["symbol"]
        conviction = float(decision.get("conviction", 0.0) or 0.0)
        expected_edge = float(decision.get("expected_upside_pct", 0.0) or 0.0) - float(
            decision.get("expected_downside_pct", 0.0) or 0.0
        )
        analyst_confidence = float((analyst_by_symbol.get(symbol) or {}).get("confidence", 0.5) or 0.5)
        concerns: list[str] = []
        approval = "approve"
        risk_level = "low"
        if expected_edge <= 0:
            concerns.append("Expected upside did not clearly exceed expected downside.")
            approval = "veto"
            risk_level = "high"
        elif expected_edge < 0.01:
            concerns.append("Expected edge is positive but thin.")
            approval = "caution"
            risk_level = "medium"
        if conviction < max(config.llm_min_conviction + 0.05, 0.60):
            concerns.append("Trader conviction is only modest after the minimum gate.")
            approval = "caution" if approval != "veto" else approval
            risk_level = "medium" if risk_level != "high" else risk_level
        if analyst_confidence < 0.50:
            concerns.append("Analyst confidence is below neutral.")
            approval = "caution" if approval != "veto" else approval
            risk_level = "medium" if risk_level != "high" else risk_level
        if not str(decision.get("disconfirming_evidence", "")).strip():
            concerns.append("Trader did not provide clear disconfirming evidence.")
            approval = "caution" if approval != "veto" else approval
            risk_level = "medium" if risk_level != "high" else risk_level
        reviews.append(
            {
                "symbol": symbol,
                "approval": approval,
                "risk_level": risk_level,
                "concerns": concerns or ["No major contradiction found in the supplied evidence."],
                "adjustment": "Proceed normally." if approval == "approve" else "Reduce conviction or skip if sizing is crowded.",
            }
        )
    return {
        "summary": "Fallback Skeptic checked edge, conviction, analyst confidence, and contradiction coverage.",
        "reviews": reviews,
    }


def _skeptic_review(config: Config, decisions: list[dict], analyst_reports: list[dict], coach_report: dict) -> dict:
    if not decisions:
        return {"summary": "No trader decisions were available for Skeptic review.", "reviews": []}
    if not config.llm_skeptic_enabled:
        return {
            "summary": "LLM Skeptic is disabled by configuration.",
            "reviews": [
                {
                    "symbol": decision["symbol"],
                    "approval": "approve",
                    "risk_level": "not_reviewed",
                    "concerns": ["Skeptic review disabled."],
                    "adjustment": "No adjustment.",
                }
                for decision in decisions
            ],
        }

    fallback = _fallback_skeptic_review(config, decisions, analyst_reports)
    if not llm_is_available(config):
        return fallback

    payload = {
        "objective": "Challenge the Trader's decisions before execution.",
        "role": "LLM Skeptic",
        "instructions": [
            "Try to falsify each trade thesis using only supplied evidence.",
            "Flag unsupported, crowded, asymmetric, or weakly timed trades.",
            "Approve strong trades, caution weaker trades, and veto trades whose upside/downside or evidence quality is poor.",
        ],
        "vetoes_enabled": config.llm_skeptic_veto_enabled,
        "coach_guidance": coach_report.get("trader_guidance", ""),
        "analyst_reports": analyst_reports,
        "trader_decisions": decisions,
        "output_format": {
            "summary": "brief explanation",
            "reviews": [
                {
                    "symbol": "ticker",
                    "approval": "approve|caution|veto",
                    "risk_level": "low|medium|high",
                    "concerns": ["bullet", "bullet"],
                    "adjustment": "one sentence",
                }
            ],
        },
    }
    response = call_json_llm(
        config,
        system_prompt=(
            "You are the Skeptic for a paper-trading LLM bot. "
            "Return JSON only. Your job is to challenge the Trader, not to be agreeable. "
            "Use only the supplied analyst reports, trader decisions, and coach guidance. "
            "Be concrete about what evidence is weak, stale, contradictory, or insufficient."
        ),
        payload=payload,
        max_output_tokens=1800,
    )
    if not response:
        return fallback

    allowed = {decision["symbol"] for decision in decisions}
    fallback_by_symbol = {review["symbol"]: review for review in fallback.get("reviews", [])}
    reviews: list[dict] = []
    for item in response.get("reviews", []):
        if not isinstance(item, dict):
            continue
        symbol = str(item.get("symbol", "")).strip().upper()
        if symbol not in allowed:
            continue
        approval = str(item.get("approval", "caution")).strip().lower()
        if approval not in {"approve", "caution", "veto"}:
            approval = "caution"
        risk_level = str(item.get("risk_level", "medium")).strip().lower()
        if risk_level not in {"low", "medium", "high"}:
            risk_level = "medium"
        concerns = _safe_text_list(item.get("concerns", []), limit=5)
        reviews.append(
            {
                "symbol": symbol,
                "approval": approval,
                "risk_level": risk_level,
                "concerns": concerns or fallback_by_symbol.get(symbol, {}).get("concerns", []),
                "adjustment": str(item.get("adjustment", "")).strip()
                or fallback_by_symbol.get(symbol, {}).get("adjustment", ""),
            }
        )

    reviewed_symbols = {review["symbol"] for review in reviews}
    for symbol, review in fallback_by_symbol.items():
        if symbol not in reviewed_symbols:
            reviews.append(review)

    return {
        "summary": str(response.get("summary", "")).strip() or fallback["summary"],
        "reviews": reviews,
    }


def _apply_skeptic_review(config: Config, decisions: list[dict], review: dict) -> tuple[list[dict], dict]:
    reviews_by_symbol = {str(item.get("symbol", "")).upper(): item for item in review.get("reviews", []) if isinstance(item, dict)}
    final_decisions: list[dict] = []
    vetoed: list[dict] = []
    cautioned = 0

    for decision in decisions:
        symbol = decision["symbol"]
        item = reviews_by_symbol.get(symbol, {})
        approval = str(item.get("approval", "approve")).lower()
        risk_level = str(item.get("risk_level", "low")).lower()
        concerns = _safe_text_list(item.get("concerns", []), limit=5)
        if approval == "veto" and config.llm_skeptic_veto_enabled:
            vetoed.append(
                {
                    "symbol": symbol,
                    "side": decision.get("side", ""),
                    "reason": "; ".join(concerns) or "Skeptic vetoed the trade.",
                }
            )
            continue

        penalty = 0.0
        if approval == "caution":
            penalty = max(penalty, 0.15)
        if risk_level == "medium":
            penalty = max(penalty, 0.10)
        elif risk_level == "high":
            penalty = max(penalty, 0.25)

        adjusted = dict(decision)
        adjusted["skeptic_approval"] = approval
        adjusted["skeptic_risk_level"] = risk_level
        adjusted["skeptic_concerns"] = concerns
        adjusted["skeptic_adjustment"] = str(item.get("adjustment", "")).strip()
        adjusted["skeptic_penalty"] = penalty
        if penalty > 0:
            adjusted["conviction"] = max(0.05, float(adjusted.get("conviction", 0.0) or 0.0) * (1.0 - penalty))
            cautioned += 1
        final_decisions.append(adjusted)

    action_summary = {
        "reviewed_count": len(decisions),
        "approved_count": sum(1 for decision in final_decisions if decision.get("skeptic_approval") == "approve"),
        "cautioned_count": cautioned,
        "vetoed_count": len(vetoed),
        "vetoes_enabled": bool(config.llm_skeptic_veto_enabled),
        "vetoed": vetoed,
    }
    return final_decisions, action_summary


def _signals_from_trader(latest: pd.DataFrame, watchlist: list[dict], decisions: list[dict]) -> list[Signal]:
    vol_by_symbol = {str(row["Symbol"]): float(row.get("vol_20d", 0.0) or 0.0) for _, row in latest.iterrows()}
    watchlist_map = {row["symbol"]: row for row in watchlist}
    selected_symbols = {decision["symbol"] for decision in decisions}
    signals: list[Signal] = []
    for decision in decisions:
        symbol = decision["symbol"]
        source = watchlist_map.get(symbol, {})
        conviction = float(decision["conviction"])
        signed_score = conviction if decision["side"] == "LONG" else -conviction
        rationale = decision["thesis"]
        if decision.get("why_now"):
            rationale = f"{rationale} Why now: {decision['why_now']}".strip()
        if decision.get("disconfirming_evidence"):
            rationale = f"{rationale} Contrary evidence: {decision['disconfirming_evidence']}".strip()
        if decision.get("risk_note"):
            rationale = f"{rationale} Risk: {decision['risk_note']}".strip()
        if decision.get("skeptic_concerns"):
            rationale = f"{rationale} Skeptic: {'; '.join(decision['skeptic_concerns'])}".strip()
        components = dict(source.get("components") or {})
        components["llm_conviction_adjustment"] = conviction * 0.001
        components["llm_expected_edge"] = (
            float(decision.get("expected_upside_pct", 0.0)) - float(decision.get("expected_downside_pct", 0.0))
        ) * 0.001
        skeptic_penalty = float(decision.get("skeptic_penalty", 0.0) or 0.0)
        if skeptic_penalty > 0:
            components["llm_skeptic_penalty"] = -skeptic_penalty * 0.001
        signals.append(
            Signal(
                symbol=symbol,
                score=signed_score,
                side=decision["side"],
                vol=vol_by_symbol.get(symbol) or 0.02,
                base_score=float(source.get("base_score", signed_score)),
                selected=True,
                components=components,
                rationale=rationale,
            )
        )
    for row in watchlist:
        if row["symbol"] in selected_symbols:
            continue
        signals.append(
            Signal(
                symbol=row["symbol"],
                score=float(row["final_score"]),
                side="HOLD",
                vol=float(row.get("vol", 0.02) or 0.02),
                base_score=float(row["base_score"]),
                selected=False,
                components=row.get("components"),
                rationale="Trader passed on this watchlist name today.",
            )
        )
    return signals


def _analyst_body(analyst_reports: list[dict], selector_summary: str) -> str:
    lines = [
        f"# {bot_label(LLM_BOT_NAME)} Analyst Report",
        "",
        selector_summary,
        "",
    ]
    for report in analyst_reports:
        lines.extend(
            [
                f"## {report['symbol']}",
                f"Market analysis: {report['market_analysis']}",
                "",
                f"Historical trends: {report['historical_trends']}",
                "",
                "Current events:",
                *[f"- {item}" for item in report.get("current_events", [])],
                "",
                "Catalysts:",
                *[f"- {item}" for item in report.get("catalysts", [])],
                "",
                "Contrary evidence:",
                *[f"- {item}" for item in report.get("contrary_evidence", [])],
                "",
                f"Time horizon: {report.get('time_horizon', 'Not specified')}",
                f"Confidence: {float(report.get('confidence', 0.0) or 0.0):.0%}",
                "",
                f"Outlook: {report['outlook']}",
                "",
                "Risks:",
                *[f"- {item}" for item in report.get("risks", [])],
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def _skeptic_body(review: dict, action_summary: dict, gated_decisions: list[dict]) -> str:
    lines = [
        f"# {bot_label(LLM_BOT_NAME)} Skeptic Report",
        "",
        str(review.get("summary", "")).strip() or "No Skeptic summary was provided.",
        "",
        "## Execution impact",
        f"- Reviewed decisions: {int(action_summary.get('reviewed_count', 0))}",
        f"- Cautioned/reduced conviction: {int(action_summary.get('cautioned_count', 0))}",
        f"- Vetoed: {int(action_summary.get('vetoed_count', 0))}",
        f"- Conviction-gated before Skeptic: {len(gated_decisions)}",
        "",
        "## Reviews",
    ]
    for item in review.get("reviews", []):
        if not isinstance(item, dict):
            continue
        lines.extend(
            [
                f"- {item.get('symbol', 'UNKNOWN')}: {item.get('approval', 'unknown')} / risk={item.get('risk_level', 'unknown')}",
                f"  Concerns: {'; '.join(_safe_text_list(item.get('concerns', []), limit=5)) or 'None recorded.'}",
                f"  Adjustment: {item.get('adjustment') or 'No adjustment.'}",
            ]
        )
    if gated_decisions:
        lines.extend(["", "## Removed by conviction gate"])
        for decision in gated_decisions:
            lines.append(f"- {decision.get('symbol', 'UNKNOWN')} {decision.get('side', '')}: {decision.get('gate_reason', '')}")
    vetoed = action_summary.get("vetoed", [])
    if vetoed:
        lines.extend(["", "## Vetoed before execution"])
        for item in vetoed:
            lines.append(f"- {item.get('symbol', 'UNKNOWN')} {item.get('side', '')}: {item.get('reason', '')}")
    return "\n".join(lines).strip() + "\n"


def _trader_body(
    trader_summary: str,
    decisions: list[dict],
    coach_report: dict,
    gated_decisions: list[dict] | None = None,
    skeptic_action_summary: dict | None = None,
) -> str:
    lines = [
        f"# {bot_label(LLM_BOT_NAME)} Trader Report",
        "",
        trader_summary,
        "",
        "Coach guidance used:",
        coach_report.get("trader_guidance", ""),
        "",
        "Skeptic / gate impact:",
        (
            f"{int((skeptic_action_summary or {}).get('cautioned_count', 0))} cautioned, "
            f"{int((skeptic_action_summary or {}).get('vetoed_count', 0))} vetoed, "
            f"{len(gated_decisions or [])} below conviction threshold."
        ),
        "",
        "## Decisions",
    ]
    for decision in decisions:
        lines.extend(
            [
                f"- {decision['symbol']} {decision['side']} conviction={float(decision['conviction']):.2f}",
                f"  Expected upside/downside: {float(decision.get('expected_upside_pct', 0.0)):.2%} / {float(decision.get('expected_downside_pct', 0.0)):.2%}",
                f"  Time horizon: {decision.get('time_horizon') or 'Not specified'}",
                f"  Why now: {decision.get('why_now') or 'Not specified'}",
                f"  Contrary evidence: {decision.get('disconfirming_evidence') or 'Not specified'}",
                f"  Thesis: {decision['thesis']}",
                f"  Risk: {decision['risk_note']}",
                f"  Skeptic: {decision.get('skeptic_approval', 'not_reviewed')} / risk={decision.get('skeptic_risk_level', 'unknown')}",
            ]
        )
    if gated_decisions:
        lines.extend(["", "## Removed before execution"])
        for decision in gated_decisions:
            lines.append(f"- {decision.get('symbol', 'UNKNOWN')} {decision.get('side', '')}: {decision.get('gate_reason', '')}")
    return "\n".join(lines).strip() + "\n"


def rebalance_llm_bot(config: Config, symbols: list[str]) -> LlmBotRunResult:
    coach_report = generate_llm_coach_report(config)
    latest, base_signals, regime_lev, spy_vol, base_context = generate_signals(config, symbols, bot_name=LLM_BOT_NAME)

    candidate_rows: list[dict] = []
    for signal in base_signals:
        if signal.side == "HOLD":
            continue
        candidate_rows.append(
            {
                "symbol": signal.symbol,
                "side": signal.side,
                "base_score": float(signal.base_score if signal.base_score is not None else signal.score),
                "final_score": float(signal.score),
                "vol": float(signal.vol or 0.02),
                "components": signal.components or {},
                "rationale": signal.rationale or "",
            }
        )
    candidate_rows = sorted(candidate_rows, key=lambda row: abs(float(row["final_score"])), reverse=True)
    research = base_context.get("research", {}) if isinstance(base_context.get("research"), dict) else {}
    watchlist_symbols, selector_summary = _select_watchlist(config, candidate_rows, research)
    watchlist = [row for row in candidate_rows if row["symbol"] in set(watchlist_symbols)]
    watchlist.sort(key=lambda row: watchlist_symbols.index(row["symbol"]) if row["symbol"] in watchlist_symbols else 999)

    analyst_reports = _analyst_reports(config, watchlist, research)
    analyst_body = _analyst_body(analyst_reports, selector_summary)
    log_strategy_report(
        config.db_path,
        datetime.now(timezone.utc).isoformat(),
        "analyst_daily",
        f"{bot_label(LLM_BOT_NAME)} Analyst Daily Report",
        f"Prepared analyst memos for {len(analyst_reports)} watchlist names.",
        analyst_body,
        json.dumps({"watchlist_count": len(analyst_reports)}, sort_keys=True),
        json.dumps({}, sort_keys=True),
        bot_name=LLM_BOT_NAME,
    )

    raw_decisions, trader_summary = _trader_decisions(config, watchlist, analyst_reports, coach_report)
    decisions, conviction_gated = _apply_llm_conviction_gate(config, raw_decisions)
    skeptic_review = _skeptic_review(config, decisions, analyst_reports, coach_report)
    decisions, skeptic_action_summary = _apply_skeptic_review(config, decisions, skeptic_review)
    decisions = sorted(decisions, key=lambda item: float(item.get("conviction", 0.0)), reverse=True)
    skeptic_body = _skeptic_body(skeptic_review, skeptic_action_summary, conviction_gated)
    log_strategy_report(
        config.db_path,
        datetime.now(timezone.utc).isoformat(),
        "skeptic",
        f"{bot_label(LLM_BOT_NAME)} Skeptic Report",
        (
            f"Reviewed {skeptic_action_summary.get('reviewed_count', 0)} trader decisions; "
            f"cautioned {skeptic_action_summary.get('cautioned_count', 0)}, "
            f"vetoed {skeptic_action_summary.get('vetoed_count', 0)}, "
            f"conviction-gated {len(conviction_gated)}."
        ),
        skeptic_body,
        json.dumps(
            {
                "reviewed_count": skeptic_action_summary.get("reviewed_count", 0),
                "cautioned_count": skeptic_action_summary.get("cautioned_count", 0),
                "vetoed_count": skeptic_action_summary.get("vetoed_count", 0),
                "conviction_gated_count": len(conviction_gated),
                "llm_min_conviction": config.llm_min_conviction,
            },
            sort_keys=True,
        ),
        json.dumps({"vetoed": skeptic_action_summary.get("vetoed", [])}, sort_keys=True),
        bot_name=LLM_BOT_NAME,
    )
    trader_body = _trader_body(trader_summary, decisions, coach_report, conviction_gated, skeptic_action_summary)
    log_strategy_report(
        config.db_path,
        datetime.now(timezone.utc).isoformat(),
        "trader_daily",
        f"{bot_label(LLM_BOT_NAME)} Trader Daily Report",
        trader_summary,
        trader_body,
        json.dumps({"decision_count": len(decisions)}, sort_keys=True),
        json.dumps({}, sort_keys=True),
        bot_name=LLM_BOT_NAME,
    )

    llm_signals = _signals_from_trader(latest, watchlist, decisions)
    decision_context = dict(base_context)
    decision_context.update(
        {
            "selector_summary": selector_summary,
            "watchlist_symbols": watchlist_symbols,
            "analyst_reports": analyst_reports,
            "coach_report": coach_report,
            "trader_summary": trader_summary,
            "raw_trader_decision_count": len(raw_decisions),
            "conviction_gated": conviction_gated,
            "skeptic_review": skeptic_review,
            "skeptic_action_summary": skeptic_action_summary,
            "bot_name": LLM_BOT_NAME,
        }
    )
    ts, orders, signals, final_context = execute_signals(
        config,
        latest,
        llm_signals,
        regime_lev,
        spy_vol,
        decision_context,
        bot_name=LLM_BOT_NAME,
    )

    overview_lines = [
        f"# {bot_label(LLM_BOT_NAME)} Daily Overview",
        "",
        f"Generated at {datetime.now(timezone.utc).isoformat()}",
        "",
        f"Selector summary: {selector_summary}",
        "",
        f"Trader summary: {trader_summary}",
        "",
        f"Skeptic summary: {skeptic_review.get('summary', '')}",
        "",
        f"Coach summary: {coach_report.get('summary', '')}",
        "",
        "## Watchlist",
        *[f"- {symbol}" for symbol in watchlist_symbols],
        "",
        "## Submitted decisions",
        *[
            f"- {decision['symbol']} {decision['side']} conviction={float(decision['conviction']):.2f}: {decision['thesis']}"
            for decision in decisions
        ],
    ]
    overview_body = "\n".join(overview_lines).strip() + "\n"
    reports_dir = Path(config.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"llm_daily_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(overview_body, encoding="utf-8")
    log_strategy_report(
        config.db_path,
        datetime.now(timezone.utc).isoformat(),
        "llm_daily",
        f"{bot_label(LLM_BOT_NAME)} Daily Overview",
        f"Watchlist size {len(watchlist_symbols)}, trader decisions {len(decisions)}, submitted orders {len(orders)}.",
        overview_body,
        json.dumps({"watchlist_count": len(watchlist_symbols), "decision_count": len(decisions), "order_count": len(orders)}, sort_keys=True),
        json.dumps({}, sort_keys=True),
        bot_name=LLM_BOT_NAME,
    )

    return LlmBotRunResult(ts=ts, orders=orders, signals=signals, decision_context=final_context)


def generate_llm_bot_status_report(config: Config) -> str:
    reports = read_latest_strategy_reports(config.db_path, limit=12, bot_name=LLM_BOT_NAME)
    recent_decisions = read_recent_selected_decisions(config.db_path, limit=20, bot_name=LLM_BOT_NAME)
    lines = [
        f"# {bot_label(LLM_BOT_NAME)} Status Report",
        "",
        "## Recent reports",
    ]
    for row in reports[:8]:
        lines.append(f"- {row[0]} [{row[1]}] {row[2]}: {row[3]}")
    lines.extend(["", "## Recent selected decisions"])
    for row in recent_decisions[:10]:
        lines.append(
            f"- {row[0]} {row[1]} {row[2]} base={float(row[3]):.2%} final={float(row[4]):.2%} outcome={row[12] or 'pending'}"
        )
    return "\n".join(lines).strip() + "\n"
