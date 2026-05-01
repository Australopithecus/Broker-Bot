from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from .backtest import _apply_ensemble_overlay, _inverse_vol_weights, _memory_score
from .bots import ML_BOT_NAME, bot_label, normalize_bot_name
from .config import Config
from .data import fetch_daily_bars
from .features import FEATURE_COLUMNS, build_features
from .logging_db import log_strategy_report
from .model import predict_return, train_model
from .overlay_learning import COMPONENT_COLUMNS, load_component_scales


@dataclass
class ModelEvalReport:
    ts: str
    headline: str
    summary: str
    metrics: dict[str, float]
    report_path: str


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:+.2%}"


def _fmt_float(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.3f}"


def _markdown_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    return [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
        *["| " + " | ".join(row) + " |" for row in rows],
    ]


def _max_drawdown(equity_curve: list[float]) -> float:
    peak = 0.0
    max_dd = 0.0
    for value in equity_curve:
        peak = max(peak, value)
        if peak > 0:
            max_dd = max(max_dd, (peak - value) / peak)
    return max_dd


def _prepare_features(config: Config, symbols: list[str], bot_name: str) -> pd.DataFrame:
    end = datetime.now(timezone.utc)
    lookback_days = max(config.training_lookback_days * 2, config.training_lookback_days + 180, 540)
    start = end - timedelta(days=lookback_days)
    bars = fetch_daily_bars(config, symbols + ["SPY"], start, end, bot_name=bot_name).bars

    features = build_features(bars)
    features["timestamp"] = pd.to_datetime(features["timestamp"])
    features = features[features["Symbol"] != "SPY"].copy()
    if config.min_price > 0:
        features = features[features["close"] >= config.min_price]
    if config.min_dollar_vol > 0 and "dollar_vol_20d" in features.columns:
        features = features[features["dollar_vol_20d"] >= config.min_dollar_vol]

    features["next_return"] = features.groupby("Symbol", group_keys=False)["close"].transform(
        lambda series: series.pct_change(periods=config.prediction_horizon_days).shift(
            -config.prediction_horizon_days
        )
    )

    market = bars[bars["Symbol"] == "SPY"].sort_values("timestamp")[["timestamp", "close"]].copy()
    market["timestamp"] = pd.to_datetime(market["timestamp"])
    market["spy_next_return"] = (
        market["close"].pct_change(periods=config.prediction_horizon_days).shift(-config.prediction_horizon_days)
    )
    features = features.merge(market[["timestamp", "spy_next_return"]], on="timestamp", how="left")
    features = features.dropna(subset=FEATURE_COLUMNS + ["next_return"])
    return features.sort_values(["timestamp", "Symbol"]).reset_index(drop=True)


def _build_oos_predictions(config: Config, features: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, float]]]:
    dates = sorted(pd.to_datetime(features["timestamp"]).dropna().unique())
    if len(dates) < 80:
        raise RuntimeError("Not enough history to run out-of-sample model evaluation.")

    n_splits = 5
    gap = max(1, int(config.prediction_horizon_days))
    test_size = max(10, min(45, len(dates) // (n_splits + 1)))
    predictions: list[pd.DataFrame] = []
    fold_summaries: list[dict[str, float]] = []

    for fold_idx in range(n_splits):
        test_start = len(dates) - test_size * (n_splits - fold_idx)
        test_end = min(len(dates), test_start + test_size)
        if test_start <= gap or test_end <= test_start:
            continue

        train_cutoff = pd.Timestamp(dates[test_start - gap])
        test_dates = set(pd.Timestamp(value) for value in dates[test_start:test_end])
        train_start = train_cutoff - pd.Timedelta(days=config.training_lookback_days)
        train_df = features[
            (pd.to_datetime(features["timestamp"]) < train_cutoff)
            & (pd.to_datetime(features["timestamp"]) >= train_start)
        ].copy()
        test_df = features[pd.to_datetime(features["timestamp"]).isin(test_dates)].copy()
        if len(train_df) < 100 or test_df.empty:
            continue

        model, _ = train_model(train_df, horizon_days=config.prediction_horizon_days)
        test_df["pred_return"] = predict_return(model, test_df).values
        test_df["fold"] = float(fold_idx + 1)
        predictions.append(test_df)
        fold_summaries.append(
            {
                "fold": float(fold_idx + 1),
                "train_rows": float(len(train_df)),
                "test_rows": float(len(test_df)),
                "test_start": float(pd.Timestamp(min(test_dates)).timestamp()),
                "test_end": float(pd.Timestamp(max(test_dates)).timestamp()),
            }
        )

    if not predictions:
        raise RuntimeError("Not enough eligible train/test folds for out-of-sample model evaluation.")
    return pd.concat(predictions, ignore_index=True), fold_summaries


def _rebalance_dates(dates: list[pd.Timestamp], frequency: str) -> set[pd.Timestamp]:
    dates_df = pd.DataFrame({"timestamp": pd.to_datetime(dates)})
    if dates_df["timestamp"].dt.tz is not None:
        dates_df["timestamp"] = dates_df["timestamp"].dt.tz_convert(None)
    dates_df["bucket"] = dates_df["timestamp"].dt.to_period(frequency)
    return set(pd.Timestamp(value) for value in dates_df.groupby("bucket")["timestamp"].max().tolist())


def _variant_weights(config: Config, disabled_component: str | None = None) -> dict[str, float]:
    weights = {
        "technical_weight": config.technical_weight,
        "snapshot_weight": config.snapshot_weight,
        "screener_weight": config.screener_weight,
        "news_weight": config.news_weight,
        "memory_weight": config.memory_weight,
        "llm_weight": config.llm_weight,
    }
    if disabled_component:
        weight_name = disabled_component.replace("_adjustment", "_weight")
        if weight_name in weights:
            weights[weight_name] = 0.0
    return weights


def _score_variant(
    predictions: pd.DataFrame,
    config: Config,
    component_scales: dict[str, float],
    *,
    disabled_component: str | None = None,
    base_only: bool = False,
) -> dict[str, float]:
    predictions = predictions.copy()
    predictions["timestamp"] = pd.to_datetime(predictions["timestamp"])
    if predictions["timestamp"].dt.tz is not None:
        predictions["timestamp"] = predictions["timestamp"].dt.tz_convert(None)
    dates = sorted(pd.Timestamp(value) for value in pd.to_datetime(predictions["timestamp"]).unique())
    rebalance_dates = _rebalance_dates(dates, config.rebalance_frequency)
    symbol_history: dict[str, list[float]] = {}
    symbol_memory: dict[str, float] = {}
    pending_memory_updates: list[tuple[pd.Timestamp, str, float]] = []
    current_weights: dict[str, float] = {}

    selected_signed: list[float] = []
    selected_alpha: list[float] = []
    long_returns: list[float] = []
    short_signed_returns: list[float] = []
    turnover_values: list[float] = []
    equity = 1.0
    equity_curve = [equity]
    long_count = 0
    short_count = 0

    for ts in dates:
        matured = [item for item in pending_memory_updates if item[0] <= ts]
        if matured:
            for _, symbol, signed_return in matured:
                history = symbol_history.setdefault(symbol, [])
                history.append(float(signed_return))
                symbol_memory[symbol] = _memory_score(history)
            pending_memory_updates = [item for item in pending_memory_updates if item[0] > ts]

        if ts not in rebalance_dates:
            continue

        slice_df = predictions[predictions["timestamp"] == ts].copy()
        if slice_df.empty:
            continue

        weights = {name: 0.0 for name in _variant_weights(config)}
        scales = {name: 1.0 for name in COMPONENT_COLUMNS}
        if not base_only:
            weights = _variant_weights(config, disabled_component=disabled_component)
            scales = dict(component_scales)
            if disabled_component:
                scales[disabled_component] = 0.0

        scored = _apply_ensemble_overlay(
            slice_df,
            technical_weight=weights["technical_weight"],
            snapshot_weight=weights["snapshot_weight"],
            screener_weight=weights["screener_weight"],
            news_weight=weights["news_weight"],
            memory_weight=weights["memory_weight"],
            llm_weight=weights["llm_weight"],
            symbol_memory=symbol_memory,
            component_scales=scales,
        )

        longs = (
            scored[scored["pred_return"] >= config.min_long_return]
            .sort_values("pred_return", ascending=False)
            .head(config.rebalance_top_k)
        )
        shorts = (
            scored[scored["pred_return"] <= config.max_short_return]
            .sort_values("pred_return", ascending=True)
            .head(config.rebalance_top_k)
        )
        long_count += len(longs)
        short_count += len(shorts)

        for _, row in longs.iterrows():
            signed_return = float(row["next_return"])
            selected_signed.append(signed_return)
            long_returns.append(signed_return)
            if pd.notna(row.get("spy_next_return")):
                selected_alpha.append(signed_return - float(row["spy_next_return"]))
            pending_memory_updates.append((ts + pd.Timedelta(days=config.prediction_horizon_days), row["Symbol"], signed_return))
        for _, row in shorts.iterrows():
            signed_return = -float(row["next_return"])
            selected_signed.append(signed_return)
            short_signed_returns.append(signed_return)
            if pd.notna(row.get("spy_next_return")):
                selected_alpha.append(signed_return - float(row["spy_next_return"]))
            pending_memory_updates.append((ts + pd.Timedelta(days=config.prediction_horizon_days), row["Symbol"], signed_return))

        new_weights = _inverse_vol_weights(
            scored,
            top_k=config.rebalance_top_k,
            min_long_return=config.min_long_return,
            max_short_return=config.max_short_return,
            gross_leverage=config.gross_leverage,
            max_position_pct=config.max_position_pct,
            allow_shorts=True,
        )
        turnover = sum(
            abs(new_weights.get(symbol, 0.0) - current_weights.get(symbol, 0.0))
            for symbol in set(new_weights) | set(current_weights)
        )
        portfolio_return = 0.0
        for _, row in scored.iterrows():
            portfolio_return += new_weights.get(row["Symbol"], 0.0) * float(row["next_return"])
        portfolio_return -= (config.tcost_bps / 10000.0) * turnover
        turnover_values.append(turnover)
        current_weights = new_weights
        equity *= 1.0 + portfolio_return
        equity_curve.append(equity)

    selected_count = len(selected_signed)
    return {
        "selected_count": float(selected_count),
        "long_count": float(long_count),
        "short_count": float(short_count),
        "selected_hit_rate": (
            sum(1 for value in selected_signed if value > 0) / selected_count if selected_count else 0.0
        ),
        "selected_avg_signed_return": sum(selected_signed) / selected_count if selected_count else 0.0,
        "long_bucket_return": sum(long_returns) / len(long_returns) if long_returns else 0.0,
        "short_bucket_return": sum(short_signed_returns) / len(short_signed_returns) if short_signed_returns else 0.0,
        "avg_spy_alpha": sum(selected_alpha) / len(selected_alpha) if selected_alpha else 0.0,
        "portfolio_total_return": equity - 1.0,
        "max_drawdown": _max_drawdown(equity_curve),
        "avg_turnover": sum(turnover_values) / len(turnover_values) if turnover_values else 0.0,
        "rebalance_count": float(len(turnover_values)),
    }


def generate_model_eval_report(
    config: Config,
    symbols: list[str],
    bot_name: str = ML_BOT_NAME,
) -> ModelEvalReport:
    normalized_bot = normalize_bot_name(bot_name)
    features = _prepare_features(config, symbols, normalized_bot)
    predictions, fold_summaries = _build_oos_predictions(config, features)
    component_scales = load_component_scales(config.learned_policy_path)

    base_directional_accuracy = float(
        ((predictions["next_return"] >= 0) == (predictions["pred_return"] >= 0)).mean()
    )
    base_mae = float((predictions["next_return"] - predictions["pred_return"]).abs().mean())

    variant_metrics: dict[str, dict[str, float]] = {
        "base_model": _score_variant(predictions, config, component_scales, base_only=True),
        "learned_overlays": _score_variant(predictions, config, component_scales),
    }
    for component_name in COMPONENT_COLUMNS:
        label = f"without_{component_name.replace('_adjustment', '')}"
        variant_metrics[label] = _score_variant(
            predictions,
            config,
            component_scales,
            disabled_component=component_name,
        )

    full = variant_metrics["learned_overlays"]
    base = variant_metrics["base_model"]
    summary = (
        f"OOS {len(fold_summaries)} folds over {len(predictions)} symbol-days; "
        f"base directional accuracy {base_directional_accuracy:.1%}; "
        f"learned overlays returned {_fmt_pct(full['portfolio_total_return'])} "
        f"vs base {_fmt_pct(base['portfolio_total_return'])}."
    )
    ts = datetime.now(timezone.utc).isoformat()
    headline = f"{bot_label(normalized_bot)} Model Evaluation"

    metric_rows = []
    for name, values in variant_metrics.items():
        metric_rows.append(
            [
                name.replace("_", " "),
                str(int(values["selected_count"])),
                _fmt_pct(values["selected_hit_rate"]),
                _fmt_pct(values["selected_avg_signed_return"]),
                _fmt_pct(values["long_bucket_return"]),
                _fmt_pct(values["short_bucket_return"]),
                _fmt_pct(values["avg_spy_alpha"]),
                _fmt_pct(values["portfolio_total_return"]),
                _fmt_pct(-values["max_drawdown"]),
                _fmt_float(values["avg_turnover"]),
            ]
        )

    ablation_rows = []
    for component_name in COMPONENT_COLUMNS:
        label = f"without_{component_name.replace('_adjustment', '')}"
        values = variant_metrics[label]
        ablation_rows.append(
            [
                component_name.replace("_adjustment", "").replace("_", " "),
                _fmt_pct(full["portfolio_total_return"] - values["portfolio_total_return"]),
                _fmt_pct(full["selected_avg_signed_return"] - values["selected_avg_signed_return"]),
                _fmt_pct(component_scales.get(component_name, 1.0) - 1.0),
            ]
        )

    fold_rows = []
    for fold in fold_summaries:
        fold_rows.append(
            [
                str(int(fold["fold"])),
                str(int(fold["train_rows"])),
                str(int(fold["test_rows"])),
                datetime.fromtimestamp(fold["test_start"], tz=timezone.utc).date().isoformat(),
                datetime.fromtimestamp(fold["test_end"], tz=timezone.utc).date().isoformat(),
            ]
        )

    body = "\n".join(
        [
            f"# {headline}",
            "",
            f"Generated at {ts}",
            "",
            "## Executive summary",
            summary,
            "",
            "## Base prediction diagnostics",
            f"- Symbol-days scored out of sample: {len(predictions)}",
            f"- Directional accuracy: {base_directional_accuracy:.1%}",
            f"- Mean absolute error: {base_mae:.4f}",
            "",
            "## Portfolio-style evaluation",
            *_markdown_table(
                [
                    "Variant",
                    "Selected",
                    "Hit Rate",
                    "Avg Signed",
                    "Long Bucket",
                    "Short Bucket",
                    "Avg SPY Alpha",
                    "Total Return",
                    "Max DD",
                    "Avg Turnover",
                ],
                metric_rows,
            ),
            "",
            "## Overlay ablations",
            "Positive deltas mean the full learned-overlay stack beat the ablated version.",
            "",
            *_markdown_table(
                ["Removed Component", "Total Return Delta", "Avg Signed Delta", "Learned Scale Delta"],
                ablation_rows,
            ),
            "",
            "## Fold coverage",
            *_markdown_table(["Fold", "Train Rows", "Test Rows", "Test Start", "Test End"], fold_rows),
            "",
            "## Learned overlay scales",
            json.dumps(component_scales, indent=2, sort_keys=True),
        ]
    )

    reports_dir = Path(config.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"model_eval_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(body, encoding="utf-8")

    flat_metrics: dict[str, float] = {
        "oos_symbol_days": float(len(predictions)),
        "fold_count": float(len(fold_summaries)),
        "base_directional_accuracy": base_directional_accuracy,
        "base_mae": base_mae,
    }
    for variant_name, values in variant_metrics.items():
        for metric_name, value in values.items():
            flat_metrics[f"{variant_name}_{metric_name}"] = float(value)

    log_strategy_report(
        config.db_path,
        ts,
        "model_eval",
        headline,
        summary,
        body,
        json.dumps(flat_metrics, sort_keys=True),
        json.dumps({"component_scales": component_scales}, sort_keys=True),
        bot_name=normalized_bot,
    )

    return ModelEvalReport(
        ts=ts,
        headline=headline,
        summary=summary,
        metrics=flat_metrics,
        report_path=str(report_path),
    )
