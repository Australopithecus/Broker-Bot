from __future__ import annotations

import random
import pandas as pd

from .features import build_features, build_labels
from .model import train_model, predict_return
from .overlay_learning import apply_component_scales
from .risk import (
    apply_portfolio_risk_limits,
    classify_market_regime,
    estimate_correlation_clusters,
    load_sector_map,
)


def _inverse_vol_weights(
    slice_df: pd.DataFrame,
    top_k: int,
    min_long_return: float,
    max_short_return: float,
    gross_leverage: float,
    max_position_pct: float,
    allow_shorts: bool,
) -> dict[str, float]:
    weights: dict[str, float] = {}
    if slice_df.empty:
        return weights

    longs = slice_df[slice_df["pred_return"] >= min_long_return].sort_values("pred_return", ascending=False).head(top_k)
    shorts = (
        slice_df[slice_df["pred_return"] <= max_short_return].sort_values("pred_return", ascending=True).head(top_k)
        if allow_shorts
        else slice_df.iloc[0:0]
    )

    if allow_shorts:
        long_gross = gross_leverage / 2.0
        short_gross = gross_leverage / 2.0
    else:
        long_gross = gross_leverage
        short_gross = 0.0

    if not longs.empty:
        inv_vol = 1.0 / longs["vol_20d"].clip(lower=1e-6)
        scaled = inv_vol / inv_vol.sum()
        for symbol, weight in zip(longs["Symbol"], scaled):
            weights[symbol] = min(max_position_pct, float(weight) * long_gross)

    if not shorts.empty:
        inv_vol = 1.0 / shorts["vol_20d"].clip(lower=1e-6)
        scaled = inv_vol / inv_vol.sum()
        for symbol, weight in zip(shorts["Symbol"], scaled):
            weights[symbol] = -min(max_position_pct, float(weight) * short_gross)

    return weights


def _clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _rank_signal(series: pd.Series, ascending: bool = True) -> pd.Series:
    if series.empty:
        return pd.Series(dtype=float, index=series.index)
    filled = pd.to_numeric(series, errors="coerce")
    median = float(filled.dropna().median()) if not filled.dropna().empty else 0.0
    filled = filled.fillna(median)
    ranked = filled.rank(pct=True, ascending=ascending)
    return (ranked * 2.0) - 1.0


def _memory_score(history: list[float]) -> float:
    if not history:
        return 0.0
    avg_signed = sum(history) / len(history)
    hit_rate = sum(1 for value in history if value > 0) / len(history)
    confidence = min(1.0, len(history) / 6.0)
    score = ((avg_signed / 0.02) * 0.6) + (((hit_rate - 0.5) * 2.0) * 0.4)
    return _clip(score, -1.0, 1.0) * confidence


def _apply_ensemble_overlay(
    slice_df: pd.DataFrame,
    technical_weight: float,
    snapshot_weight: float,
    screener_weight: float,
    news_weight: float,
    memory_weight: float,
    llm_weight: float,
    symbol_memory: dict[str, float],
    component_scales: dict[str, float] | None = None,
) -> pd.DataFrame:
    overlay = slice_df.copy()
    overlay["base_pred_return"] = overlay["pred_return"].astype(float)

    mom_signal = _rank_signal(overlay["mom_20d"], ascending=True)
    short_signal = _rank_signal(overlay["return_5d"], ascending=True)
    rank_signal = (overlay["rank_mom_20d"].astype(float) * 2.0) - 1.0
    vol_signal = -_rank_signal(overlay["vol_20d"], ascending=True)
    overlay["technical_adjustment"] = (
        ((0.40 * mom_signal) + (0.20 * short_signal) + (0.25 * rank_signal) + (0.15 * vol_signal))
        * 0.0025
        * technical_weight
    )

    daily_move = _rank_signal(overlay["return_1d"], ascending=True)
    range_signal = _rank_signal(-overlay["range_5d"], ascending=True)
    volume_signal = _rank_signal(overlay["dollar_vol_20d"], ascending=True)
    overlay["snapshot_adjustment"] = (
        ((0.55 * daily_move) + (0.25 * range_signal) + (0.20 * volume_signal))
        * 0.0016
        * snapshot_weight
    )

    mover_signal = _rank_signal(overlay["return_1d"], ascending=True)
    active_signal = _rank_signal(overlay["dollar_vol_20d"], ascending=True)
    overlay["screener_adjustment"] = (
        ((0.65 * mover_signal) + (0.35 * active_signal)) * 0.0016 * screener_weight
    )

    abnormal_move = overlay["return_1d"].abs()
    event_signal = _rank_signal(abnormal_move, ascending=True)
    directional_event = event_signal * overlay["return_1d"].apply(lambda value: 1.0 if value >= 0 else -1.0)
    overlay["news_adjustment"] = (
        ((0.6 * directional_event) + (0.4 * active_signal)) * 0.0022 * news_weight
    )

    overlay["memory_adjustment"] = (
        overlay["Symbol"].map(symbol_memory).fillna(0.0).astype(float) * 0.0018 * memory_weight
    )

    conviction_proxy = (0.5 * mom_signal) + (0.3 * directional_event) + (0.2 * rank_signal)
    overlay["llm_adjustment"] = conviction_proxy * 0.0025 * llm_weight

    return apply_component_scales(overlay, component_scales)


def run_backtest(
    bars: pd.DataFrame,
    horizon_days: int,
    min_long_return: float,
    max_short_return: float,
    gross_leverage: float,
    top_k: int,
    max_position_pct: float,
    rebalance_frequency: str,
    tcost_bps: float,
    bear_leverage: float,
    lookback_days: int,
    min_price: float,
    min_dollar_vol: float,
    vol_target: float,
    vol_window: int,
    max_drawdown: float,
    min_leverage: float,
    miss_rebalance_prob: float,
    rebalance_delay_days: int,
    sim_seed: int,
    technical_weight: float = 1.0,
    snapshot_weight: float = 0.8,
    screener_weight: float = 0.7,
    news_weight: float = 0.9,
    memory_weight: float = 0.8,
    llm_weight: float = 0.8,
    sector_map_path: str = "",
    max_sector_exposure_pct: float = 0.35,
    max_correlated_exposure_pct: float = 0.35,
    correlation_threshold: float = 0.85,
    correlation_window: int = 90,
) -> pd.DataFrame:
    features = build_features(bars)
    features = features[features["Symbol"] != "SPY"].copy()
    features["next_return"] = build_labels(features, horizon_days=horizon_days)

    dates = sorted(features["timestamp"].unique())
    if len(dates) < 60:
        raise RuntimeError("Not enough data to backtest.")

    # Determine rebalance dates (weekly by default)
    dates_df = pd.DataFrame({"timestamp": sorted(features["timestamp"].unique())})
    dates_df["timestamp"] = pd.to_datetime(dates_df["timestamp"])
    dates_df["rebalance_bucket"] = dates_df["timestamp"].dt.to_period(rebalance_frequency)
    rebalance_dates = set(dates_df.groupby("rebalance_bucket")["timestamp"].max().tolist())

    daily_returns = []
    current_weights: dict[str, float] = {}
    symbol_history: dict[str, list[float]] = {}
    symbol_memory: dict[str, float] = {}
    pending_memory_updates: list[tuple[pd.Timestamp, str, float]] = []

    equity = 1.0
    equity_curve: list[float] = [equity]

    rng = random.Random(sim_seed)
    pending_rebalance_dt = None
    sector_map = load_sector_map(sector_map_path)

    for ts in sorted(features["timestamp"].unique()):
        ts_dt = pd.to_datetime(ts)
        slice_df = features[features["timestamp"] == ts].copy()

        matured = [item for item in pending_memory_updates if item[0] <= ts_dt]
        if matured:
            for _, symbol, signed_return in matured:
                history = symbol_history.setdefault(symbol, [])
                history.append(float(signed_return))
                symbol_memory[symbol] = _memory_score(history)
            pending_memory_updates = [item for item in pending_memory_updates if item[0] > ts_dt]

        if min_price > 0:
            slice_df = slice_df[slice_df["close"] >= min_price]
        if min_dollar_vol > 0 and "dollar_vol_20d" in slice_df.columns:
            slice_df = slice_df[slice_df["dollar_vol_20d"] >= min_dollar_vol]
        slice_df = slice_df.dropna(subset=["next_return"])

        if slice_df.empty:
            # No eligible symbols today; hold weights and record flat return.
            gross_exposure = sum(abs(weight) for weight in current_weights.values())
            long_count = sum(1 for weight in current_weights.values() if weight > 0)
            short_count = sum(1 for weight in current_weights.values() if weight < 0)
            daily_returns.append((ts_dt, 0.0, 0.0, gross_exposure, long_count, short_count))
            equity_curve.append(equity)
            continue

        should_rebalance = ts_dt in rebalance_dates
        if pending_rebalance_dt is not None and ts_dt >= pending_rebalance_dt:
            should_rebalance = True
            pending_rebalance_dt = None

        if should_rebalance:
            if miss_rebalance_prob > 0 and rng.random() < miss_rebalance_prob:
                if rebalance_delay_days > 0:
                    pending_rebalance_dt = ts_dt + pd.Timedelta(days=rebalance_delay_days)
                # Skip rebalancing but still compute daily returns with existing weights.
                should_rebalance = False

        if should_rebalance:
            market_df = bars[bars["Symbol"] == "SPY"]
            regime = classify_market_regime(
                market_df[market_df["timestamp"] <= ts_dt],
                gross_leverage=gross_leverage,
                bear_leverage=bear_leverage,
                vol_target=vol_target,
                vol_window=vol_window,
            )
            regime_lev = regime.leverage

            # Walk-forward retraining (rolling window)
            train_start = ts_dt - pd.Timedelta(days=lookback_days)
            train_df = features[
                (pd.to_datetime(features["timestamp"]) < ts_dt)
                & (pd.to_datetime(features["timestamp"]) >= train_start)
            ].copy()
            if min_price > 0:
                train_df = train_df[train_df["close"] >= min_price]
            if min_dollar_vol > 0 and "dollar_vol_20d" in train_df.columns:
                train_df = train_df[train_df["dollar_vol_20d"] >= min_dollar_vol]
            if len(train_df) > 0:
                model, _ = train_model(train_df, horizon_days=horizon_days)
                slice_df["pred_return"] = predict_return(model, slice_df)
            else:
                slice_df["pred_return"] = 0.0

            slice_df = _apply_ensemble_overlay(
                slice_df,
                technical_weight=technical_weight,
                snapshot_weight=snapshot_weight,
                screener_weight=screener_weight,
                news_weight=news_weight,
                memory_weight=memory_weight,
                llm_weight=llm_weight,
                symbol_memory=symbol_memory,
            )

            # Drawdown guardrail
            if max_drawdown > 0:
                peak = max(equity_curve) if equity_curve else equity
                dd = (peak - equity) / peak if peak > 0 else 0.0
                if dd > max_drawdown:
                    regime_lev *= max(max_drawdown / dd, 0.1)

            regime_lev = max(min_leverage, min(regime_lev, gross_leverage))

            new_weights = _inverse_vol_weights(
                slice_df,
                top_k=top_k,
                min_long_return=min_long_return,
                max_short_return=max_short_return,
                gross_leverage=regime_lev,
                max_position_pct=max_position_pct,
                allow_shorts=True,
            )
            correlation_clusters = estimate_correlation_clusters(
                bars[bars["timestamp"] <= ts_dt],
                list(new_weights),
                threshold=correlation_threshold,
                window=correlation_window,
            )
            new_weights, _ = apply_portfolio_risk_limits(
                new_weights,
                sector_map=sector_map,
                correlation_clusters=correlation_clusters,
                max_sector_exposure_pct=max_sector_exposure_pct,
                max_correlated_exposure_pct=max_correlated_exposure_pct,
            )
            longs = (
                slice_df[slice_df["pred_return"] >= min_long_return]
                .sort_values("pred_return", ascending=False)
                .head(top_k)
            )
            shorts = (
                slice_df[slice_df["pred_return"] <= max_short_return]
                .sort_values("pred_return", ascending=True)
                .head(top_k)
            )
            eval_dt = ts_dt + pd.Timedelta(days=horizon_days)
            for _, row in longs.iterrows():
                pending_memory_updates.append((eval_dt, row["Symbol"], float(row["next_return"])))
            for _, row in shorts.iterrows():
                pending_memory_updates.append((eval_dt, row["Symbol"], -float(row["next_return"])))
            turnover = sum(abs(new_weights.get(sym, 0.0) - current_weights.get(sym, 0.0)) for sym in set(new_weights) | set(current_weights))
            current_weights = new_weights
            cost = (tcost_bps / 10000.0) * turnover
            long_count = len(longs)
            short_count = len(shorts)
        else:
            cost = 0.0
            turnover = 0.0
            long_count = sum(1 for weight in current_weights.values() if weight > 0)
            short_count = sum(1 for weight in current_weights.values() if weight < 0)

        if slice_df.empty:
            continue

        daily_ret = 0.0
        for _, row in slice_df.iterrows():
            weight = current_weights.get(row["Symbol"], 0.0)
            daily_ret += weight * float(row["next_return"])

        daily_ret -= cost
        gross_exposure = sum(abs(weight) for weight in current_weights.values())
        daily_returns.append((ts_dt, daily_ret, turnover, gross_exposure, long_count, short_count))
        equity = equity * (1 + daily_ret)
        equity_curve.append(equity)

    result = pd.DataFrame(
        daily_returns,
        columns=["timestamp", "strategy_return", "turnover", "gross_exposure", "long_count", "short_count"],
    ).sort_values("timestamp")
    result["strategy_equity"] = (1 + result["strategy_return"]).cumprod()
    market = bars[bars["Symbol"] == "SPY"].sort_values("timestamp")[["timestamp", "close"]].copy()
    market["spy_return"] = market["close"].shift(-max(int(horizon_days), 1)) / market["close"] - 1.0
    result = result.merge(market[["timestamp", "spy_return"]], on="timestamp", how="left")
    result["alpha"] = result["strategy_return"] - result["spy_return"].fillna(0.0)
    return result
