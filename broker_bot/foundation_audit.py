from __future__ import annotations

import csv
import json
import os
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import dotenv_values

from .bots import AI_LAB_BOT_NAME, LLM_BOT_NAME, ML_BOT_NAME


PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"


@dataclass(frozen=True)
class AuditCheck:
    name: str
    status: str
    summary: str
    details: list[str]


@dataclass(frozen=True)
class FoundationAudit:
    generated_at: str
    project_root: str
    overall_status: str
    fail_count: int
    warn_count: int
    checks: list[AuditCheck]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["checks"] = [asdict(check) for check in self.checks]
        return payload


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _status_rank(status: str) -> int:
    return {PASS: 0, WARN: 1, FAIL: 2}.get(status, 2)


def _worst_status(checks: list[AuditCheck]) -> str:
    return max((check.status for check in checks), key=_status_rank, default=PASS)


def _env_bool(env: dict[str, str], name: str, default: bool = False) -> bool:
    value = str(env.get(name, "")).strip().lower()
    if not value:
        return default
    return value in {"1", "true", "yes", "y", "on"}


def _env_int(env: dict[str, str], name: str, default: int) -> int:
    try:
        return int(str(env.get(name, "")).strip() or default)
    except Exception:
        return default


def _env_float(env: dict[str, str], name: str, default: float) -> float:
    try:
        return float(str(env.get(name, "")).strip() or default)
    except Exception:
        return default


def _load_env(project_root: Path) -> dict[str, str]:
    env_path = project_root / ".env"
    file_values = {
        key: str(value)
        for key, value in dotenv_values(env_path).items()
        if value is not None
    }
    merged = dict(file_values)
    merged.update({key: value for key, value in os.environ.items() if value is not None})
    return merged


def _rooted_path(project_root: Path, value: str | None, default: str) -> Path:
    raw = (value or default).strip() or default
    path = Path(raw)
    if not path.is_absolute():
        path = project_root / path
    return path


def _parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _age_hours(ts: datetime | None, now: datetime) -> float | None:
    if ts is None:
        return None
    return max(0.0, (now - ts).total_seconds() / 3600.0)


def _fmt_age(hours: float | None) -> str:
    if hours is None:
        return "unknown age"
    if hours < 48:
        return f"{hours:.1f} hours old"
    return f"{hours / 24.0:.1f} days old"


def _read_universe(path: Path) -> list[str]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        symbols: list[str] = []
        for row in reader:
            symbol = (row.get("symbol") or row.get("Symbol") or "").strip().upper()
            if symbol:
                symbols.append(symbol.replace(".", "-"))
        return sorted(set(symbols))


def _read_sector_map(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        sectors: dict[str, str] = {}
        for row in reader:
            symbol = (row.get("symbol") or row.get("Symbol") or "").strip().upper()
            sector = (row.get("sector") or row.get("Sector") or "").strip()
            if symbol and sector:
                sectors[symbol.replace(".", "-")] = sector
        return sectors


def _audit_credentials(env: dict[str, str]) -> AuditCheck:
    missing = [
        name
        for name in ["ALPACA_API_KEY", "ALPACA_SECRET_KEY"]
        if not str(env.get(name, "")).strip()
    ]
    details: list[str] = []
    if missing:
        return AuditCheck(
            "credentials",
            FAIL,
            "Required Alpaca paper-trading credentials are missing.",
            [f"Missing {', '.join(missing)}."],
        )

    partial_pairs = []
    for label, key_name, secret_name in [
        ("LLM Bot", "ALPACA_LLM_API_KEY", "ALPACA_LLM_SECRET_KEY"),
        ("AI Lab Bot", "ALPACA_AI_LAB_API_KEY", "ALPACA_AI_LAB_SECRET_KEY"),
    ]:
        has_key = bool(str(env.get(key_name, "")).strip())
        has_secret = bool(str(env.get(secret_name, "")).strip())
        if has_key != has_secret:
            partial_pairs.append(f"{label} has only one of {key_name}/{secret_name} set.")

    if partial_pairs:
        return AuditCheck("credentials", FAIL, "One or more optional bot credential pairs are incomplete.", partial_pairs)

    if _env_bool(env, "LLM_ENABLED", False) and not str(env.get("OPENAI_API_KEY", "")).strip():
        return AuditCheck(
            "credentials",
            FAIL,
            "LLM features are enabled but OPENAI_API_KEY is missing.",
            ["Set OPENAI_API_KEY or set LLM_ENABLED=0."],
        )

    feed = str(env.get("ALPACA_DATA_FEED", "iex") or "iex").strip().lower()
    if feed not in {"iex", "sip", "delayed_sip"}:
        details.append(f"ALPACA_DATA_FEED={feed!r} is unusual; expected iex, sip, or delayed_sip.")

    details.append("Base Alpaca credentials are present; secret values were not inspected or printed.")
    return AuditCheck("credentials", WARN if len(details) > 1 else PASS, "Credential shape looks usable.", details)


def _audit_universe(project_root: Path, env: dict[str, str]) -> AuditCheck:
    universe_path = _rooted_path(project_root, env.get("UNIVERSE_PATH"), "data/sp500.csv")
    sector_path = _rooted_path(project_root, env.get("SECTOR_MAP_PATH"), "data/sector_map.csv")
    min_symbols = _env_int(env, "BROKER_BOT_MIN_UNIVERSE_SYMBOLS", 100)
    max_sector_share = _env_float(env, "BROKER_BOT_MAX_SINGLE_SECTOR_SHARE", 0.45)

    if not universe_path.exists():
        return AuditCheck(
            "universe",
            FAIL,
            "Trading universe file is missing.",
            [f"Expected universe at {universe_path}."],
        )

    symbols = _read_universe(universe_path)
    details = [f"{universe_path} contains {len(symbols)} unique symbol(s)."]
    status = PASS
    if len(symbols) < min_symbols:
        status = FAIL
        details.append(
            f"Minimum recommended symbol count is {min_symbols}; a tiny universe can overfit and overconcentrate."
        )

    sector_map = _read_sector_map(sector_path)
    if sector_map:
        covered = [symbol for symbol in symbols if symbol in sector_map]
        coverage = len(covered) / len(symbols) if symbols else 0.0
        details.append(f"Sector map covers {coverage:.1%} of the universe.")
        if coverage < 0.75:
            status = max(status, WARN, key=_status_rank)
            details.append("Sector coverage is low; sector exposure caps may be less effective.")
        sector_counts: dict[str, int] = {}
        for symbol in covered:
            sector_counts[sector_map[symbol]] = sector_counts.get(sector_map[symbol], 0) + 1
        if sector_counts:
            sector, count = max(sector_counts.items(), key=lambda item: item[1])
            share = count / len(covered)
            details.append(f"Largest mapped sector is {sector} at {share:.1%} of mapped symbols.")
            if share > max_sector_share:
                status = max(status, WARN, key=_status_rank)
                details.append("Universe is sector-heavy; this can make model comparison mostly a sector bet.")
    else:
        status = max(status, WARN, key=_status_rank)
        details.append(f"No sector map found at {sector_path}; sector caps will be limited.")

    return AuditCheck(
        "universe",
        status,
        "Universe breadth is adequate." if status == PASS else "Universe needs attention.",
        details,
    )


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _scalar(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()) -> Any:
    row = conn.execute(sql, params).fetchone()
    return row[0] if row else None


def _available_bots(conn: sqlite3.Connection) -> list[str]:
    bots = {ML_BOT_NAME}
    for table_name in ["equity", "trades", "decision_logs", "strategy_reports"]:
        if not _table_exists(conn, table_name):
            continue
        try:
            rows = conn.execute(
                f"SELECT DISTINCT COALESCE(NULLIF(bot_name, ''), 'ml') FROM {table_name}"
            ).fetchall()
        except sqlite3.Error:
            continue
        bots.update(str(row[0]) for row in rows if row and row[0])
    return sorted(bots)


def _active_audit_bots(env: dict[str, str], db_bots: list[str]) -> list[str]:
    bots = {ML_BOT_NAME}
    if str(env.get("ALPACA_LLM_API_KEY", "")).strip() and str(env.get("ALPACA_LLM_SECRET_KEY", "")).strip():
        bots.add(LLM_BOT_NAME)
    if str(env.get("ALPACA_AI_LAB_API_KEY", "")).strip() and str(env.get("ALPACA_AI_LAB_SECRET_KEY", "")).strip():
        bots.add(AI_LAB_BOT_NAME)
    bots.update(bot for bot in db_bots if bot in {ML_BOT_NAME, LLM_BOT_NAME, AI_LAB_BOT_NAME})
    return sorted(bots)


def _audit_database(project_root: Path, env: dict[str, str], now: datetime) -> AuditCheck:
    db_path = _rooted_path(project_root, env.get("BROKER_BOT_DB"), "data/broker_bot.sqlite")
    if not db_path.exists():
        return AuditCheck("database", FAIL, "Broker bot database is missing.", [f"Expected DB at {db_path}."])

    required_tables = [
        "equity",
        "trades",
        "positions",
        "signals",
        "decision_runs",
        "decision_logs",
        "decision_outcomes",
        "strategy_reports",
    ]
    max_equity_age_hours = _env_float(env, "BROKER_BOT_MAX_EQUITY_AGE_HOURS", 72.0)
    min_evaluated = _env_int(env, "BROKER_BOT_MIN_EVALUATED_DECISIONS", 30)

    details: list[str] = []
    status = PASS
    try:
        with sqlite3.connect(db_path) as conn:
            missing_tables = [table for table in required_tables if not _table_exists(conn, table)]
            if missing_tables:
                return AuditCheck(
                    "database",
                    FAIL,
                    "Broker bot database schema is incomplete.",
                    [f"Missing table(s): {', '.join(missing_tables)}."],
                )

            db_bots = _available_bots(conn)
            bots = _active_audit_bots(env, db_bots)
            inactive_bots = sorted(set(db_bots) - set(bots))
            total_equity = int(_scalar(conn, "SELECT COUNT(*) FROM equity") or 0)
            total_decisions = int(_scalar(conn, "SELECT COUNT(*) FROM decision_logs") or 0)
            total_outcomes = int(_scalar(conn, "SELECT COUNT(*) FROM decision_outcomes") or 0)
            details.append(
                f"DB rows: equity={total_equity}, decisions={total_decisions}, evaluated_decisions={total_outcomes}."
            )
            if inactive_bots:
                details.append(f"Ignoring archived/inactive bot history for freshness: {', '.join(inactive_bots)}.")
            if total_equity == 0:
                status = FAIL
                details.append("No equity snapshots exist; performance comparisons cannot be trusted.")
            if total_decisions == 0:
                status = max(status, WARN, key=_status_rank)
                details.append("No decision logs exist; the learning loop has no decision-level evidence.")
            if total_outcomes < min_evaluated:
                status = max(status, WARN, key=_status_rank)
                details.append(f"Only {total_outcomes} evaluated decision(s); target is at least {min_evaluated}.")

            for bot in bots:
                latest_equity = _parse_ts(
                    _scalar(
                        conn,
                        """
                        SELECT MAX(ts) FROM equity
                        WHERE COALESCE(NULLIF(bot_name, ''), 'ml') = ?
                        """,
                        (bot,),
                    )
                )
                equity_age = _age_hours(latest_equity, now)
                if latest_equity is None:
                    status = max(status, WARN, key=_status_rank)
                    details.append(f"{bot}: no equity snapshot.")
                elif equity_age is not None and equity_age > max_equity_age_hours:
                    status = FAIL
                    details.append(f"{bot}: latest equity snapshot is {_fmt_age(equity_age)}.")
                else:
                    details.append(f"{bot}: latest equity snapshot is {_fmt_age(equity_age)}.")
    except sqlite3.Error as exc:
        return AuditCheck("database", FAIL, "Could not inspect broker bot database.", [str(exc)])

    return AuditCheck(
        "database",
        status,
        "Evidence database looks usable." if status == PASS else "Evidence database needs attention.",
        details,
    )


def _latest_matching_file(path: Path, pattern: str) -> Path | None:
    if not path.exists():
        return None
    matches = sorted(path.glob(pattern))
    return matches[-1] if matches else None


def _report_generated_at(path: Path) -> datetime | None:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return None
    for line in lines[:12]:
        if not line.strip().lower().startswith("generated at "):
            continue
        return _parse_ts(line.split("Generated at ", 1)[-1].strip())
    return None


def _audit_reports(project_root: Path, env: dict[str, str], now: datetime) -> AuditCheck:
    reports_dir = _rooted_path(project_root, env.get("REPORTS_DIR"), "data/reports")
    if not reports_dir.exists():
        return AuditCheck("reports", FAIL, "Reports directory is missing.", [f"Expected reports at {reports_dir}."])

    stale_summary_hours = _env_float(env, "BROKER_BOT_MAX_SUMMARY_AGE_HOURS", 96.0)
    stale_model_eval_hours = _env_float(env, "BROKER_BOT_MAX_MODEL_EVAL_AGE_HOURS", 45.0 * 24.0)
    patterns = [
        ("summary", "summary_*.md", stale_summary_hours, FAIL),
        ("supervisor", "supervisor_*.md", stale_summary_hours, WARN),
        ("model_eval", "model_eval_*.md", stale_model_eval_hours, WARN),
    ]
    details: list[str] = []
    status = PASS

    for label, pattern, max_age, stale_status in patterns:
        path = _latest_matching_file(reports_dir, pattern)
        if path is None:
            status = max(status, WARN, key=_status_rank)
            details.append(f"No {label} report found with pattern {pattern}.")
            continue
        report_ts = _report_generated_at(path) or datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        age = _age_hours(report_ts, now)
        details.append(f"Latest {label} report is {path.name}, {_fmt_age(age)} by embedded timestamp.")
        if age is not None and age > max_age:
            status = max(status, stale_status, key=_status_rank)
            details.append(f"{label} report is stale; threshold is {max_age / 24.0:.1f} day(s).")

    return AuditCheck(
        "reports",
        status,
        "Reports are fresh enough." if status == PASS else "Report freshness needs attention.",
        details,
    )


def _audit_snapshot(project_root: Path, env: dict[str, str], now: datetime) -> AuditCheck:
    snapshot_path = _rooted_path(project_root, env.get("DASHBOARD_SNAPSHOT_PATH"), "data/dashboard_snapshot.json")
    max_snapshot_age_hours = _env_float(env, "BROKER_BOT_MAX_SNAPSHOT_AGE_HOURS", 24.0)
    if not snapshot_path.exists():
        return AuditCheck(
            "dashboard_snapshot",
            WARN,
            "Dashboard snapshot is missing.",
            [f"Expected snapshot at {snapshot_path}."],
        )

    try:
        payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return AuditCheck("dashboard_snapshot", FAIL, "Dashboard snapshot is not valid JSON.", [str(exc)])

    generated_at = _parse_ts(payload.get("generated_at"))
    age = _age_hours(generated_at, now)
    details = [f"Snapshot generated_at={payload.get('generated_at') or 'missing'} ({_fmt_age(age)})."]
    status = PASS
    if generated_at is None:
        status = FAIL
        details.append("Snapshot has no parseable generated_at timestamp.")
    elif age is not None and age > max_snapshot_age_hours:
        status = FAIL
        details.append(f"Snapshot is stale; threshold is {max_snapshot_age_hours:.1f} hour(s).")

    bots = payload.get("bots")
    if not isinstance(bots, dict) or not bots:
        status = max(status, WARN, key=_status_rank)
        details.append("Snapshot does not contain bot payloads.")
    else:
        details.append(f"Snapshot contains {len(bots)} bot payload(s): {', '.join(sorted(bots))}.")

    return AuditCheck(
        "dashboard_snapshot",
        status,
        "Dashboard snapshot is fresh." if status == PASS else "Dashboard snapshot needs attention.",
        details,
    )


def _audit_policy_files(project_root: Path, env: dict[str, str]) -> AuditCheck:
    expected = [
        ("learned policy", _rooted_path(project_root, env.get("LEARNED_POLICY_PATH"), "data/learned_policy.json")),
        ("champion policy", _rooted_path(project_root, env.get("CHAMPION_POLICY_PATH"), "data/champion_challenger_policy.json")),
        ("AI Lab policy", _rooted_path(project_root, env.get("AI_LAB_POLICY_PATH"), "data/ai_lab_policy.json")),
    ]
    details: list[str] = []
    status = PASS
    for label, path in expected:
        if not path.exists():
            status = max(status, WARN, key=_status_rank)
            details.append(f"Missing {label} at {path}.")
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            status = FAIL
            details.append(f"{label} is invalid JSON: {exc}.")
            continue
        details.append(f"{label} exists and is valid JSON.")

    return AuditCheck(
        "policy_files",
        status,
        "Policy files are present and parseable." if status == PASS else "Policy files need attention.",
        details,
    )


def _audit_workflows(project_root: Path) -> AuditCheck:
    workflow_dir = project_root / ".github" / "workflows"
    expected = ["advisor_snapshot.yml", "market_caretaker.yml"]
    details: list[str] = []
    missing: list[str] = []
    for filename in expected:
        path = workflow_dir / filename
        if path.exists():
            details.append(f"Found {path}.")
        else:
            missing.append(filename)
    if missing:
        return AuditCheck(
            "automation",
            WARN,
            "One or more scheduled workflow files are missing.",
            [*details, f"Missing workflow(s): {', '.join(missing)}."],
        )
    return AuditCheck("automation", PASS, "Scheduled workflow files are present.", details)


def run_foundation_audit(project_root: str | Path = ".") -> FoundationAudit:
    root = Path(project_root).resolve()
    env = _load_env(root)
    now = _now()
    checks = [
        _audit_credentials(env),
        _audit_universe(root, env),
        _audit_database(root, env, now),
        _audit_reports(root, env, now),
        _audit_snapshot(root, env, now),
        _audit_policy_files(root, env),
        _audit_workflows(root),
    ]
    fail_count = sum(1 for check in checks if check.status == FAIL)
    warn_count = sum(1 for check in checks if check.status == WARN)
    return FoundationAudit(
        generated_at=now.isoformat(),
        project_root=str(root),
        overall_status=_worst_status(checks),
        fail_count=fail_count,
        warn_count=warn_count,
        checks=checks,
    )


def format_audit_report(audit: FoundationAudit) -> str:
    lines = [
        "Broker Bot Foundation Audit",
        f"Generated: {audit.generated_at}",
        f"Project: {audit.project_root}",
        f"Overall: {audit.overall_status} ({audit.fail_count} fail, {audit.warn_count} warn)",
        "",
    ]
    for check in audit.checks:
        lines.append(f"[{check.status}] {check.name}: {check.summary}")
        for detail in check.details:
            lines.append(f"  - {detail}")
        lines.append("")
    return "\n".join(lines).rstrip()
