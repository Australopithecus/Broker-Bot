from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class MarketRegime:
    label: str
    leverage: float
    spy_vol: float
    notes: list[str]


def load_sector_map(path: str) -> dict[str, str]:
    sector_map: dict[str, str] = {}
    if not path or not Path(path).exists():
        return sector_map
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            symbol = (row.get("symbol") or row.get("Symbol") or "").strip().upper()
            sector = (row.get("sector") or row.get("Sector") or "").strip()
            if symbol and sector:
                sector_map[symbol] = sector
    return sector_map


def classify_market_regime(
    spy_df: pd.DataFrame,
    gross_leverage: float,
    bear_leverage: float,
    vol_target: float,
    vol_window: int,
) -> MarketRegime:
    if spy_df.empty:
        return MarketRegime("unknown", gross_leverage, 0.0, ["SPY data unavailable; using default leverage."])

    ordered = spy_df.sort_values("timestamp").copy()
    closes = pd.to_numeric(ordered["close"], errors="coerce").dropna()
    returns = closes.pct_change().dropna()
    spy_vol = float(returns.rolling(max(vol_window, 2)).std().iloc[-1]) if len(returns) >= max(vol_window, 2) else 0.0
    notes: list[str] = []
    leverage = gross_leverage
    label = "neutral"

    if len(closes) >= 200:
        ma50 = float(closes.rolling(50).mean().iloc[-1])
        ma200 = float(closes.rolling(200).mean().iloc[-1])
        mom20 = float(closes.pct_change(20).iloc[-1]) if len(closes) >= 21 else 0.0
        mom60 = float(closes.pct_change(60).iloc[-1]) if len(closes) >= 61 else 0.0

        if ma50 > ma200 and mom20 > 0 and mom60 > 0:
            label = "bull_trend"
            notes.append("SPY trend is constructive: 50D average is above 200D and recent momentum is positive.")
        elif ma50 < ma200 and (mom20 < 0 or mom60 < 0):
            label = "bear_trend"
            leverage = bear_leverage
            notes.append("SPY trend is defensive: 50D average is below 200D with negative momentum.")
        elif mom20 < 0:
            label = "pullback"
            leverage = min(gross_leverage, max(bear_leverage, gross_leverage * 0.75))
            notes.append("SPY is in a short-term pullback; leverage is reduced.")
        else:
            notes.append("SPY trend is mixed; using neutral leverage.")
    else:
        notes.append("Less than 200 SPY bars available; using neutral regime logic.")

    if vol_target > 0 and spy_vol > 0:
        vol_scale = min(1.0, vol_target / spy_vol)
        if vol_scale < 0.85:
            label = "high_vol_risk_off" if label in {"bear_trend", "pullback"} else "high_vol_neutral"
            notes.append(f"SPY volatility is elevated vs target; leverage scale {vol_scale:.2f}.")
        leverage *= vol_scale

    leverage = max(0.0, min(leverage, gross_leverage))
    return MarketRegime(label, leverage, spy_vol, notes)


def estimate_correlation_clusters(
    bars: pd.DataFrame,
    symbols: list[str],
    threshold: float,
    window: int,
) -> list[dict[str, object]]:
    unique_symbols = [symbol for symbol in dict.fromkeys(symbols) if symbol != "SPY"]
    if len(unique_symbols) < 2 or bars.empty or threshold <= 0:
        return []

    pivot = (
        bars[bars["Symbol"].isin(unique_symbols)]
        .pivot_table(index="timestamp", columns="Symbol", values="close")
        .sort_index()
    )
    returns = pivot.pct_change().dropna(how="all").tail(max(window, 10))
    if returns.shape[0] < 10 or returns.shape[1] < 2:
        return []

    corr = returns.corr().abs()
    remaining = set(corr.columns)
    clusters: list[dict[str, object]] = []
    while remaining:
        seed = sorted(remaining)[0]
        related = {seed}
        for candidate in list(remaining):
            if candidate == seed:
                continue
            value = corr.loc[seed, candidate] if seed in corr.index and candidate in corr.columns else 0.0
            if pd.notna(value) and float(value) >= threshold:
                related.add(candidate)
        remaining -= related
        if len(related) > 1:
            pairs = [
                float(corr.loc[a, b])
                for a in related
                for b in related
                if a < b and a in corr.index and b in corr.columns and pd.notna(corr.loc[a, b])
            ]
            clusters.append(
                {
                    "symbols": sorted(related),
                    "avg_abs_corr": float(sum(pairs) / len(pairs)) if pairs else 0.0,
                }
            )
    return clusters


def apply_portfolio_risk_limits(
    weights: dict[str, float],
    sector_map: dict[str, str],
    correlation_clusters: list[dict[str, object]],
    max_sector_exposure_pct: float,
    max_correlated_exposure_pct: float,
) -> tuple[dict[str, float], dict[str, object]]:
    adjusted = dict(weights)
    summary: dict[str, object] = {
        "sector_caps_applied": [],
        "correlation_caps_applied": [],
    }

    if max_sector_exposure_pct > 0 and sector_map:
        sector_symbols: dict[str, list[str]] = {}
        for symbol, weight in adjusted.items():
            if abs(weight) <= 0:
                continue
            sector = sector_map.get(symbol)
            if sector:
                sector_symbols.setdefault(sector, []).append(symbol)
        for sector, symbols in sector_symbols.items():
            exposure = sum(abs(adjusted.get(symbol, 0.0)) for symbol in symbols)
            if exposure <= max_sector_exposure_pct or exposure <= 0:
                continue
            scale = max_sector_exposure_pct / exposure
            for symbol in symbols:
                adjusted[symbol] *= scale
            summary["sector_caps_applied"].append(
                {
                    "sector": sector,
                    "symbols": symbols,
                    "prior_exposure": exposure,
                    "capped_exposure": max_sector_exposure_pct,
                }
            )

    if max_correlated_exposure_pct > 0 and correlation_clusters:
        for cluster in correlation_clusters:
            symbols = [str(symbol) for symbol in cluster.get("symbols", []) if str(symbol) in adjusted]
            if len(symbols) < 2:
                continue
            exposure = sum(abs(adjusted.get(symbol, 0.0)) for symbol in symbols)
            if exposure <= max_correlated_exposure_pct or exposure <= 0:
                continue
            scale = max_correlated_exposure_pct / exposure
            for symbol in symbols:
                adjusted[symbol] *= scale
            summary["correlation_caps_applied"].append(
                {
                    "symbols": symbols,
                    "avg_abs_corr": float(cluster.get("avg_abs_corr", 0.0) or 0.0),
                    "prior_exposure": exposure,
                    "capped_exposure": max_correlated_exposure_pct,
                }
            )

    summary["gross_exposure_before"] = float(sum(abs(value) for value in weights.values()))
    summary["gross_exposure_after"] = float(sum(abs(value) for value in adjusted.values()))
    return adjusted, summary
