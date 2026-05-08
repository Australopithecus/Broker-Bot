from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .bots import AI_LAB_BOT_NAME, LLM_BOT_NAME, ML_BOT_NAME, STAT_ARB_BOT_NAME, bot_label, normalize_bot_name
from .config import Config, configured_bot_names
from .logging_db import log_strategy_report, read_latest_strategy_reports


SUPERVISOR_REPORT_TYPE = "supervisor"
SUMMARY_REPORT_TYPE = "summary"
SUPERVISOR_LOOKBACK_REPORTS = 5
SUPERVISOR_MIN_REPEAT_COUNT = 2
SUPERVISOR_COOLDOWN_DAYS = 3
SUPERVISOR_MAX_APPLIED_CHANGES = 2


PARAMETER_SPECS: dict[str, dict[str, float | str]] = {
    ML_BOT_NAME: {
        "field": "min_signal_abs_score",
        "step": 0.00025,
        "low": 0.0,
        "high": 0.05,
    },
    LLM_BOT_NAME: {
        "field": "llm_min_conviction",
        "step": 0.05,
        "low": 0.1,
        "high": 0.95,
    },
    STAT_ARB_BOT_NAME: {
        "field": "stat_arb_entry_z",
        "step": 0.15,
        "low": 0.5,
        "high": 3.5,
    },
    AI_LAB_BOT_NAME: {
        "field": "ai_lab_min_abs_score",
        "step": 0.00075,
        "low": 0.0,
        "high": 0.05,
    },
}


@dataclass
class SupervisorReport:
    ts: str
    headline: str
    summary: str
    report_path: str


def _clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _read_json(payload: str | None) -> dict:
    if not payload:
        return {}
    try:
        parsed = json.loads(payload)
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _load_policy(path: str) -> dict:
    policy_path = Path(path)
    if not path or not policy_path.exists():
        return {"bots": {}, "supervisor_history": []}
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except Exception:
        return {"bots": {}, "supervisor_history": []}
    if not isinstance(payload, dict):
        return {"bots": {}, "supervisor_history": []}
    if not isinstance(payload.get("bots"), dict):
        payload["bots"] = {}
    if not isinstance(payload.get("supervisor_history"), list):
        payload["supervisor_history"] = []
    return payload


def _write_policy(path: str, payload: dict) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _current_value(config: Config, policy: dict, bot_name: str, field: str) -> float:
    normalized = normalize_bot_name(bot_name)
    bot_policy = policy.get("bots", {}).get(normalized, {})
    if isinstance(bot_policy, dict) and field in bot_policy:
        try:
            return float(bot_policy[field])
        except Exception:
            pass
    if field == "min_signal_abs_score":
        return float(config.min_signal_abs_score)
    if field == "llm_min_conviction":
        return float(config.llm_min_conviction)
    if field == "llm_skeptic_veto_enabled":
        return 1.0 if config.llm_skeptic_veto_enabled else 0.0
    if field == "stat_arb_entry_z":
        return float(config.stat_arb_entry_z)
    if field == "ai_lab_min_abs_score":
        return float(config.ai_lab_min_abs_score)
    raise ValueError(f"Unsupported supervisor policy field: {field}")


def _adjust_numeric_value(bot_name: str, field: str, current: float, direction: str) -> float:
    spec = PARAMETER_SPECS[normalize_bot_name(bot_name)]
    step = float(spec["step"])
    low = float(spec["low"])
    high = float(spec["high"])
    if direction == "tighten":
        if field in {"min_signal_abs_score", "ai_lab_min_abs_score"}:
            proposed = max(current * 1.15, current + step)
        else:
            proposed = current + step
    elif direction == "relax":
        if field in {"min_signal_abs_score", "ai_lab_min_abs_score"}:
            proposed = min(current * 0.85, max(current - step, low))
        else:
            proposed = current - step
    else:
        proposed = current
    return round(_clip(float(proposed), low, high), 6)


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _recent_policy_update(policy: dict, bot_name: str, field: str, now: datetime) -> str | None:
    cutoff = now - timedelta(days=SUPERVISOR_COOLDOWN_DAYS)
    normalized = normalize_bot_name(bot_name)
    history = policy.get("supervisor_history") if isinstance(policy.get("supervisor_history"), list) else []
    for item in reversed(history):
        if not isinstance(item, dict):
            continue
        if item.get("bot_name") != normalized or item.get("field") != field or not item.get("applied"):
            continue
        parsed = _parse_ts(str(item.get("ts") or ""))
        if parsed and parsed >= cutoff:
            return f"Supervisor already changed {field} for {bot_label(normalized)} on {parsed.date()}."

    bot_policy = policy.get("bots", {}).get(normalized, {})
    if isinstance(bot_policy, dict) and bot_policy.get("updated_at") and bot_policy.get("updated_by") in {"champion_challenger", "supervisor"}:
        parsed = _parse_ts(str(bot_policy.get("updated_at") or ""))
        if parsed and parsed >= cutoff and field in bot_policy:
            return f"{bot_label(normalized)} policy was already updated by {bot_policy.get('updated_by')} on {parsed.date()}."
    return None


def _summary_reports(config: Config) -> list[dict[str, Any]]:
    rows = read_latest_strategy_reports(
        config.db_path,
        limit=SUPERVISOR_LOOKBACK_REPORTS,
        bot_name=ML_BOT_NAME,
        report_type=SUMMARY_REPORT_TYPE,
    )
    return [
        {
            "ts": row[0],
            "headline": row[2],
            "summary": row[3],
            "body": row[4],
            "metrics": _read_json(row[5]),
            "changes": _read_json(row[6]),
        }
        for row in rows
    ]


def _supporting_report_text(config: Config, bot_name: str) -> str:
    parts: list[str] = []
    for report_type in ["coach", "learning", "attribution", "champion_challenger"]:
        rows = read_latest_strategy_reports(config.db_path, limit=1, bot_name=bot_name, report_type=report_type)
        if not rows:
            continue
        row = rows[0]
        parts.append(" ".join(str(value or "") for value in [row[2], row[3], row[4]]))
    return "\n".join(parts).lower()


def _diagnostic_text(diagnostic: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ["issues", "recommendations", "positives"]:
        values = diagnostic.get(key)
        if isinstance(values, list):
            parts.extend(str(value) for value in values)
    return " ".join(parts).lower()


def _diagnostic_tags(diagnostic: dict[str, Any], supporting_text: str = "") -> set[str]:
    text = f"{_diagnostic_text(diagnostic)} {supporting_text}"
    tags: set[str] = set()
    if "no selected trades" in text or "no selected trade" in text or "nearly uninvested" in text or "all-hold" in text:
        tags.add("undertrading")
    if "over-constrained" in text or "skeptic-vetoed" in text or "skeptic veto" in text or "too cautious" in text:
        tags.add("llm_overconstrained")
    if "lagged the benchmark" in text or "poorly calibrated" in text or "weak trades" in text:
        tags.add("weak_trade_quality")
    if "entry gate may be too strict" in text or "selected none" in text or "z-score entry gate" in text:
        tags.add("stat_arb_too_strict")
    if "found no eligible pair candidates" in text:
        tags.add("data_or_universe_gap")
    return tags


def _collect_evidence(config: Config, bot_names: list[str]) -> dict[str, dict[str, Any]]:
    reports = _summary_reports(config)
    evidence: dict[str, dict[str, Any]] = {
        normalize_bot_name(bot_name): {
            "bot_name": normalize_bot_name(bot_name),
            "summary_count": len(reports),
            "tag_counts": {},
            "latest_diagnostic": {},
            "latest_tags": set(),
            "supporting_report_notes": [],
        }
        for bot_name in bot_names
    }

    supporting_text_by_bot = {bot_name: _supporting_report_text(config, bot_name) for bot_name in bot_names}
    for report_index, report in enumerate(reports):
        changes = report.get("changes") if isinstance(report.get("changes"), dict) else {}
        diagnostics = changes.get("model_diagnostics") if isinstance(changes.get("model_diagnostics"), dict) else {}
        for bot_name in bot_names:
            diagnostic = diagnostics.get(bot_name)
            if not isinstance(diagnostic, dict):
                continue
            tags = _diagnostic_tags(diagnostic, supporting_text_by_bot.get(bot_name, "") if report_index == 0 else "")
            entry = evidence[bot_name]
            if report_index == 0:
                entry["latest_diagnostic"] = diagnostic
                entry["latest_tags"] = tags
            for tag in tags:
                entry["tag_counts"][tag] = int(entry["tag_counts"].get(tag, 0)) + 1

    for bot_name, text in supporting_text_by_bot.items():
        notes = []
        if "too cautious" in text or "overly cautious" in text:
            notes.append("Recent supporting report text mentions caution or under-trading.")
        if "threshold" in text or "gate" in text:
            notes.append("Recent supporting report text discusses gates or thresholds.")
        if "skeptic" in text and "veto" in text:
            notes.append("Recent supporting report text discusses Skeptic veto behavior.")
        evidence[bot_name]["supporting_report_notes"] = notes
    return evidence


def _candidate_actions(config: Config, evidence: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for bot_name, entry in evidence.items():
        tag_counts = entry.get("tag_counts", {})
        latest_tags = entry.get("latest_tags") if isinstance(entry.get("latest_tags"), set) else set()
        repeated = lambda tag: int(tag_counts.get(tag, 0)) >= SUPERVISOR_MIN_REPEAT_COUNT and tag in latest_tags

        if bot_name == ML_BOT_NAME:
            if repeated("weak_trade_quality"):
                candidates.append(
                    {
                        "bot_name": bot_name,
                        "field": "min_signal_abs_score",
                        "direction": "tighten",
                        "reason": "Repeated Summary Reports indicate weak ML trade quality or benchmark lag.",
                    }
                )
            elif repeated("undertrading"):
                candidates.append(
                    {
                        "bot_name": bot_name,
                        "field": "min_signal_abs_score",
                        "direction": "relax",
                        "reason": "Repeated Summary Reports indicate ML under-trading during a moving market.",
                    }
                )

        if bot_name == LLM_BOT_NAME:
            if repeated("llm_overconstrained"):
                if config.llm_skeptic_veto_enabled:
                    candidates.append(
                        {
                            "bot_name": bot_name,
                            "field": "llm_skeptic_veto_enabled",
                            "direction": "disable",
                            "reason": "Repeated Summary/Coach evidence indicates the LLM Skeptic veto may be over-constraining trades.",
                        }
                    )
                else:
                    candidates.append(
                        {
                            "bot_name": bot_name,
                            "field": "llm_min_conviction",
                            "direction": "relax",
                            "reason": "Repeated Summary/Coach evidence indicates the LLM bot remains too cautious even after veto authority is reduced.",
                        }
                    )
            elif repeated("undertrading"):
                candidates.append(
                    {
                        "bot_name": bot_name,
                        "field": "llm_min_conviction",
                        "direction": "relax",
                        "reason": "Repeated Summary Reports indicate LLM under-trading during a moving market.",
                    }
                )
            elif repeated("weak_trade_quality"):
                if not config.llm_skeptic_veto_enabled:
                    candidates.append(
                        {
                            "bot_name": bot_name,
                            "field": "llm_skeptic_veto_enabled",
                            "direction": "enable",
                            "reason": "Repeated Summary Reports indicate weak LLM trade quality, so Skeptic veto authority should be restored.",
                        }
                    )
                else:
                    candidates.append(
                        {
                            "bot_name": bot_name,
                            "field": "llm_min_conviction",
                            "direction": "tighten",
                            "reason": "Repeated Summary Reports indicate weak LLM trade quality or benchmark lag.",
                        }
                    )

        if bot_name == STAT_ARB_BOT_NAME:
            if repeated("stat_arb_too_strict") or repeated("undertrading"):
                candidates.append(
                    {
                        "bot_name": bot_name,
                        "field": "stat_arb_entry_z",
                        "direction": "relax",
                        "reason": "Repeated Summary Reports indicate Stat Arb is finding setups but the entry gate may be too strict.",
                    }
                )
            elif repeated("weak_trade_quality"):
                candidates.append(
                    {
                        "bot_name": bot_name,
                        "field": "stat_arb_entry_z",
                        "direction": "tighten",
                        "reason": "Repeated Summary Reports indicate weak Stat Arb trade quality or benchmark lag.",
                    }
                )
        if bot_name == AI_LAB_BOT_NAME:
            if repeated("weak_trade_quality"):
                candidates.append(
                    {
                        "bot_name": bot_name,
                        "field": "ai_lab_min_abs_score",
                        "direction": "tighten",
                        "reason": "Repeated Summary Reports indicate weak AI Lab trade quality or benchmark lag.",
                    }
                )
            elif repeated("undertrading"):
                candidates.append(
                    {
                        "bot_name": bot_name,
                        "field": "ai_lab_min_abs_score",
                        "direction": "relax",
                        "reason": "Repeated Summary Reports indicate AI Lab under-trading during a moving market.",
                    }
                )
    return candidates


def _apply_action(config: Config, policy: dict, action: dict[str, Any], now: datetime) -> dict[str, Any]:
    bot_name = normalize_bot_name(str(action["bot_name"]))
    field = str(action["field"])
    current = _current_value(config, policy, bot_name, field)
    cooldown = _recent_policy_update(policy, bot_name, field, now)
    result = {
        **action,
        "bot_name": bot_name,
        "old_value": current,
        "new_value": current,
        "applied": False,
        "status": "skipped",
        "skip_reason": cooldown or "",
    }
    if cooldown:
        result["status"] = "cooldown"
        return result

    if field == "llm_skeptic_veto_enabled":
        new_value = 0.0 if action.get("direction") == "disable" else 1.0
    else:
        new_value = _adjust_numeric_value(bot_name, field, current, str(action.get("direction") or "hold"))
    result["new_value"] = new_value
    if abs(float(new_value) - float(current)) < 1e-9:
        result["status"] = "unchanged"
        result["skip_reason"] = "The bounded adjustment would not change the current policy value."
        return result

    bots = policy.setdefault("bots", {})
    bot_policy = bots.setdefault(bot_name, {})
    bot_policy[field] = new_value
    bot_policy["updated_at"] = now.isoformat()
    bot_policy["updated_by"] = "supervisor"
    bot_policy["last_reason"] = str(action.get("reason") or "")
    result["applied"] = True
    result["status"] = "applied"
    result["ts"] = now.isoformat()
    return result


def _monitoring_rows(evidence: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for bot_name, entry in evidence.items():
        tag_counts = entry.get("tag_counts", {})
        if not tag_counts:
            rows.append(
                {
                    "bot_name": bot_name,
                    "label": bot_label(bot_name),
                    "status": "No repeated Summary Report issue tags yet.",
                    "tag_counts": {},
                    "supporting_report_notes": entry.get("supporting_report_notes", []),
                }
            )
            continue
        rows.append(
            {
                "bot_name": bot_name,
                "label": bot_label(bot_name),
                "status": "Monitoring until repeated evidence clears the minimum-change threshold.",
                "tag_counts": tag_counts,
                "supporting_report_notes": entry.get("supporting_report_notes", []),
            }
        )
    return rows


def _build_body(
    ts: str,
    summary_reports: list[dict[str, Any]],
    applied: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    monitoring: list[dict[str, Any]],
) -> str:
    lines = [
        "# Supervisor Policy Report",
        "",
        f"Generated at {ts}",
        "",
        "## Purpose",
        (
            "The Supervisor consolidates the all-model Summary Report, Coach/Learning/Attribution reports, "
            "and Champion/Challenger evidence into bounded runtime policy changes. It does not edit source code."
        ),
        "",
        "## Guardrails",
        f"- Requires at least {SUPERVISOR_MIN_REPEAT_COUNT} recent Summary Report confirmations before applying a change.",
        f"- Enforces a {SUPERVISOR_COOLDOWN_DAYS}-day cooldown per model/field.",
        f"- Applies at most {SUPERVISOR_MAX_APPLIED_CHANGES} change(s) per run.",
        "- Writes only bounded policy values to the existing champion/challenger policy file.",
        "",
        "## Changes Applied",
    ]
    if applied:
        for item in applied:
            lines.append(
                f"- {bot_label(item['bot_name'])}: `{item['field']}` "
                f"{float(item['old_value']):.6f} -> {float(item['new_value']):.6f}. {item.get('reason', '')}"
            )
    else:
        lines.append("- No policy changes were applied this run.")

    lines.extend(["", "## Skipped Or Deferred Actions"])
    if skipped:
        for item in skipped:
            lines.append(
                f"- {bot_label(item['bot_name'])}: `{item['field']}` {item.get('direction', 'hold')} skipped "
                f"({item.get('status', 'skipped')}). {item.get('skip_reason') or item.get('reason', '')}"
            )
    else:
        lines.append("- No candidate actions were skipped.")

    lines.extend(["", "## Monitored Evidence"])
    for row in monitoring:
        tag_counts = row.get("tag_counts") or {}
        tag_text = ", ".join(f"{key}={value}" for key, value in sorted(tag_counts.items())) or "none"
        lines.append(f"- {row['label']}: {row['status']} Tags: {tag_text}.")
        for note in row.get("supporting_report_notes", [])[:3]:
            lines.append(f"- {row['label']} supporting note: {note}")

    lines.extend(["", "## Summary Reports Reviewed"])
    if summary_reports:
        for report in summary_reports:
            lines.append(f"- {report.get('ts', 'unknown')}: {report.get('summary', '')}")
    else:
        lines.append("- No Summary Reports were available yet, so the Supervisor only monitored.")
    return "\n".join(lines)


def generate_supervisor_report(config: Config) -> SupervisorReport:
    now = datetime.now(timezone.utc)
    bot_names = configured_bot_names(config)
    summary_reports = _summary_reports(config)
    evidence = _collect_evidence(config, bot_names)
    candidates = _candidate_actions(config, evidence)
    policy = _load_policy(config.champion_policy_path)

    applied: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for candidate in candidates:
        if len(applied) >= SUPERVISOR_MAX_APPLIED_CHANGES:
            skipped.append({**candidate, "status": "run_limit", "skip_reason": "Supervisor max changes per run reached."})
            continue
        result = _apply_action(config, policy, candidate, now)
        if result.get("applied"):
            applied.append(result)
        else:
            skipped.append(result)

    if applied:
        history = policy.setdefault("supervisor_history", [])
        for item in applied:
            history.append(
                {
                    "ts": now.isoformat(),
                    "bot_name": item["bot_name"],
                    "field": item["field"],
                    "old_value": item["old_value"],
                    "new_value": item["new_value"],
                    "direction": item.get("direction"),
                    "reason": item.get("reason"),
                    "applied": True,
                }
            )
        policy["supervisor_history"] = history[-80:]
        policy["generated_at"] = now.isoformat()
        policy["summary"] = "Conservative threshold and authority overrides promoted by champion/challenger and Supervisor reports."
        policy["supervisor"] = {
            "generated_at": now.isoformat(),
            "applied_change_count": len(applied),
            "skipped_change_count": len(skipped),
        }
        _write_policy(config.champion_policy_path, policy)

    monitoring = _monitoring_rows(evidence)
    ts = now.isoformat()
    body = _build_body(ts, summary_reports, applied, skipped, monitoring)
    summary = (
        f"Reviewed {len(summary_reports)} Summary Report(s). "
        f"Applied {len(applied)} bounded policy change(s); deferred {len(skipped)} candidate change(s)."
    )
    metrics = {
        "summary_report_count": float(len(summary_reports)),
        "candidate_change_count": float(len(candidates)),
        "applied_change_count": float(len(applied)),
        "skipped_change_count": float(len(skipped)),
    }
    changes = {
        "applied_changes": applied,
        "skipped_changes": skipped,
        "monitoring": monitoring,
        "policy_path": config.champion_policy_path,
        "guardrails": {
            "min_repeat_count": SUPERVISOR_MIN_REPEAT_COUNT,
            "cooldown_days": SUPERVISOR_COOLDOWN_DAYS,
            "max_applied_changes": SUPERVISOR_MAX_APPLIED_CHANGES,
        },
    }

    reports_dir = Path(config.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"supervisor_{now.strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(body, encoding="utf-8")
    log_strategy_report(
        config.db_path,
        ts,
        SUPERVISOR_REPORT_TYPE,
        "Supervisor Policy Report",
        summary,
        body,
        json.dumps(metrics, sort_keys=True),
        json.dumps(changes, sort_keys=True),
        bot_name=ML_BOT_NAME,
    )
    return SupervisorReport(ts=ts, headline="Supervisor Policy Report", summary=summary, report_path=str(report_path))
