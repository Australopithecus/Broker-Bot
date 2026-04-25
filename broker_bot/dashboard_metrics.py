from __future__ import annotations

from datetime import datetime, timezone
from math import sqrt
from typing import Any

import pandas as pd


WINDOW_OPTIONS = {
    "24h": pd.Timedelta(hours=24),
    "7d": pd.Timedelta(days=7),
    "14d": pd.Timedelta(days=14),
    "28d": pd.Timedelta(days=28),
    "90d": pd.Timedelta(days=90),
    "180d": pd.Timedelta(days=180),
    "360d": pd.Timedelta(days=360),
}


def to_float(value: Any, default: float | None = None) -> float | None:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except Exception:
        return default


def parse_ts(value: Any) -> pd.Timestamp | None:
    ts = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(ts):
        return None
    return ts


def pct_change(current: float | None, prior: float | None) -> float | None:
    if current is None or prior in {None, 0}:
        return None
    return (current / prior) - 1.0


def stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    avg = sum(values) / len(values)
    return sqrt(sum((value - avg) ** 2 for value in values) / (len(values) - 1))


def max_drawdown(values: list[float]) -> float:
    if not values:
        return 0.0
    peak = values[0]
    max_dd = 0.0
    for value in values[1:]:
        peak = max(peak, value)
        if peak > 0:
            max_dd = max(max_dd, (peak - value) / peak)
    return max_dd


def equity_frame(equity_rows: list[dict[str, Any]]) -> pd.DataFrame:
    if not equity_rows:
        return pd.DataFrame()
    df = pd.DataFrame(equity_rows)
    if "spy" not in df.columns and "spy_value" in df.columns:
        df["spy"] = df["spy_value"]
    for column in ["equity", "spy", "cash", "portfolio_value"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    df["ts"] = pd.to_datetime(df.get("ts"), errors="coerce", utc=True)
    df = df.dropna(subset=["ts", "equity"]).sort_values("ts")
    if df.empty:
        return df
    df = df.set_index("ts")
    return df[~df.index.duplicated(keep="last")]


def filter_frame_to_window(df: pd.DataFrame, window: pd.Timedelta, anchor_ts: pd.Timestamp | None = None) -> pd.DataFrame:
    if df.empty:
        return df
    latest = anchor_ts if anchor_ts is not None else df.index.max()
    cutoff = latest - window
    before_cutoff = df[df.index < cutoff].tail(1)
    in_window = df[df.index >= cutoff]
    if in_window.empty:
        return df.tail(2).sort_index()
    filtered = pd.concat([before_cutoff, in_window])
    filtered = filtered[~filtered.index.duplicated(keep="last")]
    return filtered.sort_index()


def selected_window_return(df: pd.DataFrame, window: pd.Timedelta, anchor_ts: pd.Timestamp | None = None) -> tuple[float | None, float | None]:
    filtered = filter_frame_to_window(df, window, anchor_ts)
    if len(filtered) < 2:
        return None, None
    bot_ret = pct_change(to_float(filtered["equity"].iloc[-1]), to_float(filtered["equity"].iloc[0]))
    spy_ret = None
    if "spy" in filtered.columns and filtered["spy"].notna().sum() >= 2:
        spy = filtered["spy"].dropna()
        spy_ret = pct_change(to_float(spy.iloc[-1]), to_float(spy.iloc[0]))
    return bot_ret, spy_ret


def bot_performance_metrics(
    bot_payload: dict[str, Any],
    window: pd.Timedelta,
    anchor_ts: pd.Timestamp | None = None,
) -> dict[str, Any]:
    df = equity_frame(bot_payload.get("equity", []))
    positions = bot_payload.get("positions", []) or []
    trades = bot_payload.get("trades", []) or []
    decisions = bot_payload.get("decisions", []) or []
    latest_equity = to_float(df["equity"].iloc[-1]) if not df.empty else None
    bot_ret, spy_ret = selected_window_return(df, window, anchor_ts) if not df.empty else (None, None)
    window_df = filter_frame_to_window(df, window, anchor_ts) if not df.empty else pd.DataFrame()
    equity_values = [float(value) for value in window_df.get("equity", pd.Series(dtype=float)).dropna().tolist()]

    position_values = [abs(to_float(row.get("market_value"), 0.0) or 0.0) for row in positions]
    protected = [
        row
        for row in positions
        if str(row.get("protection_mode") or "").strip().lower() not in {"", "none", "unknown"}
    ]
    evaluated = [row for row in decisions if row.get("signed_return") is not None]
    signed_returns = [to_float(row.get("signed_return"), 0.0) or 0.0 for row in evaluated]
    beat_spy_values = [to_float(row.get("beat_spy")) for row in evaluated if to_float(row.get("beat_spy")) is not None]

    long_exposure = sum(to_float(row.get("market_value"), 0.0) or 0.0 for row in positions if (to_float(row.get("market_value"), 0.0) or 0.0) > 0)
    short_exposure = sum(abs(to_float(row.get("market_value"), 0.0) or 0.0) for row in positions if (to_float(row.get("market_value"), 0.0) or 0.0) < 0)
    gross_exposure = sum(position_values)

    return {
        "latest_equity": latest_equity,
        "window_return": bot_ret,
        "spy_window_return": spy_ret,
        "window_alpha": (bot_ret - spy_ret) if bot_ret is not None and spy_ret is not None else None,
        "max_drawdown": max_drawdown(equity_values),
        "trade_count": len(trades),
        "position_count": len(positions),
        "gross_exposure": gross_exposure,
        "gross_exposure_pct": (gross_exposure / latest_equity) if latest_equity else None,
        "long_exposure": long_exposure,
        "short_exposure": short_exposure,
        "largest_position": max(position_values) if position_values else 0.0,
        "largest_position_pct": (max(position_values) / latest_equity) if latest_equity and position_values else None,
        "protected_position_count": len(protected),
        "unprotected_position_count": max(0, len(positions) - len(protected)),
        "protection_rate": (len(protected) / len(positions)) if positions else None,
        "evaluated_decision_count": len(evaluated),
        "win_rate": (sum(1 for value in signed_returns if value > 0) / len(signed_returns)) if signed_returns else None,
        "avg_trade_alpha": (sum(beat_spy_values) / len(beat_spy_values)) if beat_spy_values else None,
        "latest_snapshot_ts": df.index.max().isoformat() if not df.empty else None,
    }


def comparison_table(bots_payload: dict[str, dict[str, Any]], window_key: str = "90d") -> list[dict[str, Any]]:
    window = WINDOW_OPTIONS.get(window_key, WINDOW_OPTIONS["90d"])
    frames = {name: equity_frame(payload.get("equity", [])) for name, payload in bots_payload.items()}
    anchor = max((df.index.max() for df in frames.values() if not df.empty), default=None)
    rows: list[dict[str, Any]] = []
    for name, payload in bots_payload.items():
        metrics = bot_performance_metrics(payload, window, anchor)
        rows.append(
            {
                "bot": name,
                "label": payload.get("label", name.upper()),
                **metrics,
            }
        )
    rows.sort(key=lambda row: row.get("window_return") if row.get("window_return") is not None else -999, reverse=True)
    return rows


def agreement_summary(bots_payload: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if "ml" not in bots_payload or "llm" not in bots_payload:
        return {"overlap": 0, "agreements": [], "disagreements": []}

    latest: dict[str, dict[str, tuple[str, float | None]]] = {}
    for bot_name in ["ml", "llm"]:
        latest[bot_name] = {}
        for row in bots_payload.get(bot_name, {}).get("decisions", []) or []:
            symbol = str(row.get("symbol") or "").upper()
            side = str(row.get("side") or "").upper()
            if not symbol or not side or symbol in latest[bot_name]:
                continue
            latest[bot_name][symbol] = (side, to_float(row.get("signed_return")))

    overlap = sorted(set(latest["ml"]) & set(latest["llm"]))
    agreements = [symbol for symbol in overlap if latest["ml"][symbol][0] == latest["llm"][symbol][0]]
    disagreements = [symbol for symbol in overlap if latest["ml"][symbol][0] != latest["llm"][symbol][0]]
    return {
        "overlap": len(overlap),
        "agreement_rate": (len(agreements) / len(overlap)) if overlap else None,
        "agreements": agreements,
        "disagreements": disagreements,
    }


def freshness_status(generated_at: str | None, stale_after_minutes: int = 180) -> dict[str, Any]:
    ts = parse_ts(generated_at)
    if ts is None:
        return {"status": "unknown", "age_minutes": None, "message": "No snapshot timestamp available."}
    now = pd.Timestamp(datetime.now(timezone.utc))
    age_minutes = max(0.0, (now - ts).total_seconds() / 60.0)
    status = "fresh" if age_minutes <= stale_after_minutes else "stale"
    return {
        "status": status,
        "age_minutes": age_minutes,
        "message": f"Snapshot is {age_minutes:.0f} minutes old.",
    }


def extract_key_takeaways(body: str | None, limit: int = 5) -> list[str]:
    if not body:
        return []
    takeaways: list[str] = []
    for raw_line in str(body).splitlines():
        line = raw_line.strip()
        if not line.startswith("- "):
            continue
        text = line[2:].strip()
        if text and len(text) > 8:
            takeaways.append(text)
        if len(takeaways) >= limit:
            break
    return takeaways
