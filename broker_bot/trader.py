from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from zoneinfo import ZoneInfo

import pandas as pd
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    GetOrdersRequest,
    MarketOrderRequest,
    StopLossRequest,
    TakeProfitRequest,
    TrailingStopOrderRequest,
)
from alpaca.trading.enums import OrderClass, OrderSide, TimeInForce
from alpaca.common.exceptions import APIError

from .config import Config, get_bot_account_config
from .data import fetch_daily_bars
from .features import build_features
from .learning import build_symbol_memory
from .model import load_model, predict_return
from .research import build_research_overlay
from .logging_db import read_latest_equity
from .risk import (
    apply_portfolio_risk_limits,
    classify_market_regime,
    estimate_correlation_clusters,
    load_sector_map,
)


@dataclass
class Signal:
    symbol: str
    score: float
    side: str  # LONG or SHORT or HOLD
    vol: float | None = None
    base_score: float | None = None
    selected: bool = False
    components: dict[str, float] | None = None
    rationale: str = ""


OrderLogRow = tuple[str, str, str, float, Optional[float], Optional[str], Optional[str]]


def _latest_date(df: pd.DataFrame) -> datetime:
    return pd.to_datetime(df["timestamp"]).max().to_pydatetime()


def _compute_drawdown(values: list[float]) -> float:
    if not values:
        return 0.0
    peak = values[0]
    max_dd = 0.0
    for v in values[1:]:
        if v > peak:
            peak = v
        dd = (peak - v) / peak if peak > 0 else 0.0
        if dd > max_dd:
            max_dd = dd
    return max_dd


def _asset_info(trading: TradingClient, symbol: str, cache: dict[str, dict[str, bool]]) -> dict[str, bool]:
    if symbol in cache:
        return cache[symbol]
    asset = trading.get_asset(symbol)
    info = {
        "shortable": bool(getattr(asset, "shortable", False)),
        "tradable": bool(getattr(asset, "tradable", True)),
    }
    cache[symbol] = info
    return info


def _is_shortable(trading: TradingClient, symbol: str, cache: dict[str, dict[str, bool]]) -> bool:
    info = _asset_info(trading, symbol, cache)
    return info["shortable"] and info["tradable"]


def _is_tradable(trading: TradingClient, symbol: str, cache: dict[str, dict[str, bool]]) -> bool:
    info = _asset_info(trading, symbol, cache)
    return info["tradable"]


def _round_order_price(price: float) -> float:
    decimals = 4 if price < 1.0 else 2
    return round(float(price), decimals)


def _is_whole_share_qty(qty: float) -> bool:
    return abs(qty - round(qty)) < 1e-6


def _time_in_force_from_name(name: str) -> TimeInForce:
    value = (name or "gtc").strip().lower()
    if value == "day":
        return TimeInForce.DAY
    return TimeInForce.GTC


def _build_bracket_order(
    symbol: str,
    qty: float,
    side: OrderSide,
    price: float,
    config: Config,
    take_profit_pct: float | None = None,
    stop_loss_pct: float | None = None,
) -> MarketOrderRequest | None:
    if qty <= 0 or price <= 0:
        return None

    take_profit_pct = config.bracket_take_profit_pct if take_profit_pct is None else take_profit_pct
    stop_loss_pct = config.bracket_stop_loss_pct if stop_loss_pct is None else stop_loss_pct

    if side == OrderSide.BUY:
        take_profit_price = _round_order_price(price * (1.0 + max(take_profit_pct, 0.0)))
        stop_price = _round_order_price(price * (1.0 - max(stop_loss_pct, 0.0)))
    else:
        take_profit_price = _round_order_price(price * (1.0 - max(take_profit_pct, 0.0)))
        stop_price = _round_order_price(price * (1.0 + max(stop_loss_pct, 0.0)))

    if take_profit_price <= 0 or stop_price <= 0:
        return None
    if side == OrderSide.BUY and take_profit_price <= stop_price:
        return None
    if side == OrderSide.SELL and take_profit_price >= stop_price:
        return None

    return MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=side,
        time_in_force=TimeInForce.GTC,
        order_class=OrderClass.BRACKET,
        take_profit=TakeProfitRequest(limit_price=take_profit_price),
        stop_loss=StopLossRequest(stop_price=stop_price),
    )


def _cancel_open_orders_for_symbols(
    trading: TradingClient,
    orders: list,
    symbols: set[str],
) -> None:
    for order in orders:
        symbol = getattr(order, "symbol", None)
        order_id = getattr(order, "id", None)
        if symbol not in symbols or not order_id:
            continue
        try:
            trading.cancel_order_by_id(order_id)
        except Exception:
            continue


def _load_open_orders(trading: TradingClient, nested: bool = False) -> list:
    try:
        try:
            from alpaca.trading.enums import OrderStatus  # type: ignore

            request = GetOrdersRequest(status=OrderStatus.OPEN, nested=nested)
        except Exception:
            request = GetOrdersRequest(status="open", nested=nested)
        return list(trading.get_orders(request))
    except Exception:
        return []


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except Exception:
        return None


def _iter_orders(order: Any) -> list[Any]:
    orders = [order]
    for leg in getattr(order, "legs", None) or []:
        orders.extend(_iter_orders(leg))
    return orders


def _flatten_orders(orders: list[Any]) -> list[Any]:
    flattened: list[Any] = []
    seen: set[str] = set()
    for order in orders:
        for item in _iter_orders(order):
            order_id = str(getattr(item, "id", "")) or f"anon-{id(item)}"
            if order_id in seen:
                continue
            seen.add(order_id)
            flattened.append(item)
    return flattened


def _protection_summary_for_position(qty: float, orders: list[Any]) -> dict[str, Any]:
    exit_side = "sell" if qty > 0 else "buy"
    take_profit_prices: list[float] = []
    stop_prices: list[float] = []
    trailing_bits: list[str] = []
    active_count = 0

    for order in orders:
        side_attr = getattr(order, "side", None)
        side_value = str(getattr(side_attr, "value", side_attr or "")).lower()
        if side_value != exit_side:
            continue

        active_count += 1
        trail_percent = _optional_float(getattr(order, "trail_percent", None))
        trail_price = _optional_float(getattr(order, "trail_price", None))
        stop_price = _optional_float(getattr(order, "stop_price", None))
        limit_price = _optional_float(getattr(order, "limit_price", None))

        if trail_percent is not None:
            trailing_bits.append(f"{trail_percent:.2f}% trail")
            continue
        if trail_price is not None:
            trailing_bits.append(f"${trail_price:,.2f} trail")
            continue
        if stop_price is not None:
            stop_prices.append(stop_price)
        if limit_price is not None:
            take_profit_prices.append(limit_price)

    mode = "None"
    if trailing_bits and (take_profit_prices or stop_prices):
        mode = "Mixed exits"
    elif trailing_bits:
        mode = "Trailing stop"
    elif take_profit_prices and stop_prices:
        mode = "Bracket exits"
    elif stop_prices:
        mode = "Stop loss"
    elif take_profit_prices:
        mode = "Take profit"
    elif active_count:
        mode = "Open exit order"

    summary_parts: list[str] = []
    if take_profit_prices:
        summary_parts.append(f"TP ${max(take_profit_prices):,.2f}")
    if stop_prices:
        summary_parts.append(f"SL ${min(stop_prices):,.2f}" if qty > 0 else f"SL ${max(stop_prices):,.2f}")
    if trailing_bits:
        summary_parts.append(", ".join(trailing_bits[:2]))

    return {
        "protection_mode": mode,
        "protection_summary": " | ".join(summary_parts) if summary_parts else ("No broker-side exits found." if active_count == 0 else "Open exit order without parsed thresholds."),
        "take_profit_price": max(take_profit_prices) if take_profit_prices else None,
        "stop_price": min(stop_prices) if stop_prices and qty > 0 else (max(stop_prices) if stop_prices else None),
        "trailing_stop": ", ".join(trailing_bits[:2]) if trailing_bits else None,
        "open_exit_order_count": active_count,
    }


def _build_trailing_stop_order(
    symbol: str,
    qty: float,
    side: OrderSide,
    config: Config,
    trail_percent_override: float | None = None,
) -> TrailingStopOrderRequest | None:
    if qty <= 0 or not _is_whole_share_qty(qty):
        return None

    trail_percent = trail_percent_override if trail_percent_override and trail_percent_override > 0 else None
    if trail_percent is None:
        trail_percent = config.trailing_stop_percent if config.trailing_stop_percent > 0 else None
    trail_price = None if trail_percent is not None else (_round_order_price(config.trailing_stop_price) if config.trailing_stop_price > 0 else None)
    if trail_percent is None and trail_price is None:
        return None

    return TrailingStopOrderRequest(
        symbol=symbol,
        qty=float(int(round(qty))),
        side=side,
        time_in_force=_time_in_force_from_name(config.trailing_stop_time_in_force),
        trail_percent=trail_percent,
        trail_price=trail_price,
    )


def _component_payload(row: pd.Series) -> dict[str, float]:
    return {
        "technical_adjustment": float(row.get("technical_adjustment", 0.0)),
        "snapshot_adjustment": float(row.get("snapshot_adjustment", 0.0)),
        "screener_adjustment": float(row.get("screener_adjustment", 0.0)),
        "news_adjustment": float(row.get("news_adjustment", 0.0)),
        "memory_adjustment": float(row.get("memory_adjustment", 0.0)),
        "llm_adjustment": float(row.get("llm_adjustment", 0.0)),
    }


def _adaptive_exit_pcts(signal: Signal | None, config: Config) -> tuple[float, float]:
    fixed_stop = max(config.bracket_stop_loss_pct, 0.0)
    fixed_take_profit = max(config.bracket_take_profit_pct, 0.0)
    if not config.adaptive_exits_enabled or signal is None or not signal.vol:
        return fixed_take_profit, fixed_stop

    stop_pct = float(signal.vol) * max(config.stop_loss_vol_multiple, 0.0)
    stop_pct = max(config.min_stop_loss_pct, fixed_stop, stop_pct)
    stop_pct = min(max(config.max_stop_loss_pct, stop_pct), 0.50)
    take_profit_pct = max(fixed_take_profit, stop_pct * max(config.take_profit_reward_multiple, 1.0))
    return take_profit_pct, stop_pct


def _adaptive_trail_percent(signal: Signal | None, config: Config) -> float | None:
    if config.trailing_stop_percent > 0 or not config.adaptive_exits_enabled or signal is None or not signal.vol:
        return None
    _, stop_pct = _adaptive_exit_pcts(signal, config)
    return round(stop_pct * 100.0, 2)


def _caretaker_trail_percent(config: Config) -> float | None:
    if config.caretaker_trailing_stop_percent > 0:
        return config.caretaker_trailing_stop_percent
    if config.trailing_stop_percent > 0:
        return config.trailing_stop_percent

    stop_pct = max(config.bracket_stop_loss_pct, config.min_stop_loss_pct, 0.0)
    return round(stop_pct * 100.0, 2) if stop_pct > 0 else None


def _current_day_drawdown(config: Config, bot_name: str, current_equity: float) -> float | None:
    if config.caretaker_daily_drawdown_limit <= 0 or current_equity <= 0:
        return None

    today = datetime.now(ZoneInfo("America/New_York")).date()
    intraday_values = [current_equity]
    for ts, equity, *_ in read_latest_equity(config.db_path, limit=500, bot_name=bot_name):
        parsed = pd.to_datetime(ts, errors="coerce", utc=True)
        if pd.isna(parsed):
            continue
        if parsed.tz_convert("America/New_York").date() == today:
            intraday_values.append(float(equity))

    peak = max(intraday_values)
    if peak <= 0:
        return None
    return max(0.0, (peak - current_equity) / peak)


def _flatten_position_order(
    position: Any,
    trading: TradingClient,
) -> tuple[str, str, str, float, float | None, str | None, str | None]:
    qty = float(position.qty)
    side = OrderSide.SELL if qty > 0 else OrderSide.BUY
    price = _optional_float(getattr(position, "current_price", None))
    submitted = trading.submit_order(
        MarketOrderRequest(
            symbol=position.symbol,
            qty=abs(qty),
            side=side,
            time_in_force=TimeInForce.DAY,
        )
    )
    return (
        datetime.now(timezone.utc).isoformat(),
        position.symbol,
        side.value,
        float(abs(qty)),
        price,
        submitted.id,
        f"{submitted.status} (caretaker_kill_switch)",
    )


def generate_signals(
    config: Config,
    symbols: list[str],
    bot_name: str = "ml",
) -> tuple[pd.DataFrame, list[Signal], float, float, dict]:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=260)
    bars = fetch_daily_bars(config, symbols + ["SPY"], start, end, bot_name=bot_name).bars

    features = build_features(bars)
    if features.empty:
        raise RuntimeError("Not enough data to build features for signals.")

    latest_ts = _latest_date(features)
    latest = features[pd.to_datetime(features["timestamp"]) == latest_ts].copy()
    latest = latest[latest["Symbol"] != "SPY"].copy()

    model = load_model(config.model_dir)
    preds = predict_return(model, latest)
    latest["pred_return"] = preds.values

    if config.min_price > 0:
        latest = latest[latest["close"] >= config.min_price]
    if config.min_dollar_vol > 0 and "dollar_vol_20d" in latest.columns:
        latest = latest[latest["dollar_vol_20d"] >= config.min_dollar_vol]

    symbol_memory = build_symbol_memory(config.db_path, bot_name=bot_name)
    latest, research_context = build_research_overlay(config, latest, symbol_memory=symbol_memory, bot_name=bot_name)

    long_candidates = latest[latest["pred_return"] >= config.min_long_return].sort_values("pred_return", ascending=False)
    short_candidates = latest[latest["pred_return"] <= config.max_short_return].sort_values("pred_return", ascending=True)

    longs = long_candidates.head(config.rebalance_top_k)
    shorts = short_candidates.head(config.rebalance_top_k)
    selected_symbols = set(longs["Symbol"]).union(set(shorts["Symbol"]))

    signals: list[Signal] = []
    for _, row in longs.iterrows():
        signals.append(
            Signal(
                symbol=row["Symbol"],
                score=float(row["pred_return"]),
                side="LONG",
                vol=float(row["vol_20d"]),
                base_score=float(row.get("base_pred_return", row["pred_return"])),
                selected=True,
                components=_component_payload(row),
                rationale=str(row.get("rationale", "")),
            )
        )
    for _, row in shorts.iterrows():
        signals.append(
            Signal(
                symbol=row["Symbol"],
                score=float(row["pred_return"]),
                side="SHORT",
                vol=float(row["vol_20d"]),
                base_score=float(row.get("base_pred_return", row["pred_return"])),
                selected=True,
                components=_component_payload(row),
                rationale=str(row.get("rationale", "")),
            )
        )

    for _, row in latest.iterrows():
        if row["Symbol"] not in selected_symbols:
            signals.append(
                Signal(
                    symbol=row["Symbol"],
                    score=float(row["pred_return"]),
                    side="HOLD",
                    vol=float(row["vol_20d"]),
                    base_score=float(row.get("base_pred_return", row["pred_return"])),
                    selected=False,
                    components=_component_payload(row),
                    rationale=str(row.get("rationale", "")),
                )
            )

    spy_df = bars[bars["Symbol"] == "SPY"]
    regime = classify_market_regime(
        spy_df,
        gross_leverage=config.gross_leverage,
        bear_leverage=config.bear_leverage,
        vol_target=config.vol_target,
        vol_window=config.vol_window,
    )
    correlation_clusters = estimate_correlation_clusters(
        bars,
        sorted(selected_symbols),
        threshold=config.correlation_threshold,
        window=config.correlation_window,
    )
    decision_context = {
        "candidate_count": int(len(latest)),
        "selected_long_count": int(len(longs)),
        "selected_short_count": int(len(shorts)),
        "memory_symbol_count": int(len(symbol_memory)),
        "market_regime": {
            "label": regime.label,
            "notes": regime.notes,
        },
        "correlation_clusters": correlation_clusters,
        "research": research_context.to_dict(),
    }
    return latest, signals, regime.leverage, regime.spy_vol, decision_context


def _target_weights(
    signals: list[Signal], gross_leverage: float, max_position_pct: float, top_k: int, allow_shorts: bool
) -> dict[str, float]:
    longs = [s for s in signals if s.side == "LONG"][:top_k]
    shorts = [s for s in signals if s.side == "SHORT"][:top_k] if allow_shorts else []

    weights: dict[str, float] = {}
    if not longs and not shorts:
        return weights

    if allow_shorts:
        long_gross = gross_leverage / 2.0
        short_gross = gross_leverage / 2.0
    else:
        long_gross = gross_leverage
        short_gross = 0.0

    if longs:
        inv_vol = [(1.0 / max(s.vol or 1e-6, 1e-6)) for s in longs]
        total = sum(inv_vol)
        for s, iv in zip(longs, inv_vol):
            weight = (iv / total) * long_gross
            weights[s.symbol] = min(max_position_pct, weight)
    if shorts:
        inv_vol = [(1.0 / max(s.vol or 1e-6, 1e-6)) for s in shorts]
        total = sum(inv_vol)
        for s, iv in zip(shorts, inv_vol):
            weight = (iv / total) * short_gross
            weights[s.symbol] = -min(max_position_pct, weight)

    return weights


def _apply_confidence_gate(signals: list[Signal], min_abs_score: float) -> tuple[list[Signal], list[dict[str, float | str]]]:
    if min_abs_score <= 0:
        return signals, []

    gated_signals: list[Signal] = []
    gated_details: list[dict[str, float | str]] = []
    for signal in signals:
        if signal.selected and signal.side in {"LONG", "SHORT"} and abs(float(signal.score)) < min_abs_score:
            components = dict(signal.components or {})
            components["confidence_gate_min_abs_score"] = float(min_abs_score)
            rationale = (signal.rationale or "").strip()
            gate_note = (
                f"Confidence gate changed this to HOLD because score {float(signal.score):+.4f} "
                f"was below minimum {min_abs_score:.4f}."
            )
            gated_signals.append(
                replace(
                    signal,
                    side="HOLD",
                    selected=False,
                    components=components,
                    rationale=f"{rationale} {gate_note}".strip(),
                )
            )
            gated_details.append(
                {
                    "symbol": signal.symbol,
                    "side": signal.side,
                    "score": float(signal.score),
                    "min_abs_score": float(min_abs_score),
                }
            )
            continue
        gated_signals.append(signal)
    return gated_signals, gated_details


def execute_signals(
    config: Config,
    latest: pd.DataFrame,
    signals: list[Signal],
    regime_lev: float,
    spy_vol: float,
    decision_context: dict,
    bot_name: str = "ml",
) -> tuple[str, list[OrderLogRow], list[Signal], dict]:
    account_config = get_bot_account_config(config, bot_name)
    trading = TradingClient(account_config.api_key, account_config.secret_key, paper=True)

    account = trading.get_account()
    shorting_flag = getattr(account, "shorting_enabled", False)
    if isinstance(shorting_flag, str):
        shorting_enabled = shorting_flag.strip().lower() in {"true", "1", "yes", "y"}
    else:
        shorting_enabled = bool(shorting_flag)
    asset_cache: dict[str, dict[str, bool]] = {}

    # Regime classification already applies SPY volatility targeting; drawdown adds an account-level guardrail.
    leverage = regime_lev
    dd_rows = read_latest_equity(config.db_path, limit=config.drawdown_window, bot_name=bot_name)
    equities = [row[1] for row in reversed(dd_rows)]
    dd = _compute_drawdown(equities) if len(equities) > 1 else 0.0
    if config.max_drawdown > 0 and dd > config.max_drawdown:
        leverage *= max(config.max_drawdown / dd, 0.1)

    leverage = max(config.min_leverage, min(leverage, config.gross_leverage))
    signals, confidence_gated = _apply_confidence_gate(signals, config.min_signal_abs_score)

    weights = _target_weights(
        signals,
        leverage,
        config.max_position_pct,
        config.rebalance_top_k,
        allow_shorts=shorting_enabled,
    )

    sector_map = load_sector_map(config.sector_map_path)
    weights, risk_summary = apply_portfolio_risk_limits(
        weights,
        sector_map=sector_map,
        correlation_clusters=decision_context.get("correlation_clusters", [])
        if isinstance(decision_context.get("correlation_clusters"), list)
        else [],
        max_sector_exposure_pct=config.max_sector_exposure_pct,
        max_correlated_exposure_pct=config.max_correlated_exposure_pct,
    )

    # Enforce tradable/shortable filters
    filtered: dict[str, float] = {}
    for sym, w in weights.items():
        if w < 0 and not _is_shortable(trading, sym, asset_cache):
            continue
        if w > 0 and not _is_tradable(trading, sym, asset_cache):
            continue
        filtered[sym] = w
    weights = filtered
    decision_context["effective_leverage"] = float(leverage)
    decision_context["regime_leverage"] = float(regime_lev)
    decision_context["spy_vol"] = float(spy_vol)
    decision_context["selected_weights"] = {symbol: float(weight) for symbol, weight in weights.items()}
    decision_context["shorting_enabled"] = bool(shorting_enabled)
    decision_context["portfolio_risk"] = risk_summary
    decision_context["min_signal_abs_score"] = float(config.min_signal_abs_score)
    decision_context["confidence_gated_count"] = len(confidence_gated)
    decision_context["confidence_gated"] = confidence_gated

    equity = float(account.equity)

    # Map latest prices
    latest_prices = {row["Symbol"]: float(row["close"]) for _, row in latest.iterrows()}

    # Current positions
    current_positions = {p.symbol: float(p.qty) for p in trading.get_all_positions()}
    signal_by_symbol = {signal.symbol: signal for signal in signals}

    orders_to_log: list[OrderLogRow] = []

    advanced_execution_enabled = config.execution_order_mode == "bracket" or config.trailing_stop_enabled
    open_orders = _load_open_orders(trading)
    managed_symbols = set(current_positions).union(set(weights))
    if advanced_execution_enabled and managed_symbols:
        _cancel_open_orders_for_symbols(trading, open_orders, managed_symbols)
        open_orders = _load_open_orders(trading)
    open_order_symbols = {o.symbol for o in open_orders}
    decision_context["execution_order_mode"] = config.execution_order_mode
    decision_context["trailing_stop_enabled"] = bool(
        config.trailing_stop_enabled and config.execution_order_mode != "bracket"
    )

    for symbol, target_weight in weights.items():
        if symbol not in latest_prices:
            continue
        if symbol in open_order_symbols:
            # Avoid submitting overlapping orders on the same symbol.
            continue
        target_value = equity * target_weight
        price = latest_prices[symbol]
        if price <= 0:
            continue
        target_qty = target_value / price
        if not shorting_enabled and target_qty < 0:
            target_qty = 0.0
        current_qty = current_positions.get(symbol, 0.0)
        delta_qty = target_qty - current_qty

        if abs(delta_qty) < 1e-3:
            continue

        side = OrderSide.BUY if delta_qty > 0 else OrderSide.SELL
        qty = abs(delta_qty)

        # Alpaca does not allow fractional short sells. If target is short, force whole shares.
        if target_qty < 0:
            qty = float(int(qty))
            if qty < 1:
                continue
        if not shorting_enabled and side == OrderSide.SELL:
            qty = min(qty, current_qty)
            if qty <= 0:
                continue

        market_order = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.DAY,
        )
        order = market_order
        used_bracket = False
        if (
            config.execution_order_mode == "bracket"
            and abs(current_qty) < 1e-3
            and _is_whole_share_qty(qty)
        ):
            bracket_order = _build_bracket_order(
                symbol=symbol,
                qty=float(int(round(qty))),
                side=side,
                price=price,
                config=config,
                take_profit_pct=_adaptive_exit_pcts(signal_by_symbol.get(symbol), config)[0],
                stop_loss_pct=_adaptive_exit_pcts(signal_by_symbol.get(symbol), config)[1],
            )
            if bracket_order is not None:
                order = bracket_order
                used_bracket = True
        try:
            submitted = trading.submit_order(order)
            orders_to_log.append((
                datetime.now(timezone.utc).isoformat(),
                symbol,
                side.value,
                float(qty),
                price,
                submitted.id,
                submitted.status,
            ))
        except APIError as exc:
            if used_bracket:
                try:
                    submitted = trading.submit_order(market_order)
                    orders_to_log.append((
                        datetime.now(timezone.utc).isoformat(),
                        symbol,
                        side.value,
                        float(qty),
                        price,
                        submitted.id,
                        f"{submitted.status} (bracket_fallback)",
                    ))
                    continue
                except APIError as fallback_exc:
                    exc = fallback_exc
            message = str(exc)
            if "40310000" in message or "insufficient qty available" in message:
                # If we attempted to short without borrow availability, fall back to closing only.
                if side == OrderSide.SELL and current_qty > 0:
                    close_qty = float(min(qty, current_qty))
                    if close_qty > 0:
                        close_order = MarketOrderRequest(
                            symbol=symbol,
                            qty=close_qty,
                            side=side,
                            time_in_force=TimeInForce.DAY,
                        )
                        try:
                            submitted = trading.submit_order(close_order)
                            orders_to_log.append((
                                datetime.now(timezone.utc).isoformat(),
                                symbol,
                                side.value,
                                float(close_qty),
                                price,
                                submitted.id,
                                submitted.status,
                            ))
                            continue
                        except APIError as exc2:
                            orders_to_log.append((
                                datetime.now(timezone.utc).isoformat(),
                                symbol,
                                side.value,
                                float(close_qty),
                                price,
                                None,
                                f"rejected: {exc2}",
                            ))
                            continue
                orders_to_log.append((
                    datetime.now(timezone.utc).isoformat(),
                    symbol,
                    side.value,
                    float(qty),
                    price,
                    None,
                    "skipped_insufficient_qty_or_open_order",
                ))
                continue
            raise

    # Close positions not in target weights
    for symbol, qty in current_positions.items():
        if symbol in weights:
            continue
        if abs(qty) < 1e-3:
            continue
        if symbol in open_order_symbols:
            continue
        side = OrderSide.SELL if qty > 0 else OrderSide.BUY
        order = MarketOrderRequest(
            symbol=symbol,
            qty=abs(qty),
            side=side,
            time_in_force=TimeInForce.DAY,
        )
        submitted = trading.submit_order(order)
        orders_to_log.append((
            datetime.now(timezone.utc).isoformat(),
            symbol,
            side.value,
            float(abs(qty)),
            latest_prices.get(symbol),
            submitted.id,
            submitted.status,
        ))

    if config.trailing_stop_enabled and config.execution_order_mode != "bracket":
        open_orders = _load_open_orders(trading)
        open_order_symbols = {o.symbol for o in open_orders}
        refreshed_positions = {p.symbol: float(p.qty) for p in trading.get_all_positions()}
        for symbol, qty in refreshed_positions.items():
            if symbol not in weights or abs(qty) < 1e-3 or symbol in open_order_symbols:
                continue
            trail_side = OrderSide.SELL if qty > 0 else OrderSide.BUY
            trailing_order = _build_trailing_stop_order(
                symbol,
                abs(qty),
                trail_side,
                config,
                trail_percent_override=_adaptive_trail_percent(signal_by_symbol.get(symbol), config),
            )
            if trailing_order is None:
                continue
            try:
                submitted = trading.submit_order(trailing_order)
                orders_to_log.append((
                    datetime.now(timezone.utc).isoformat(),
                    symbol,
                    trail_side.value,
                    float(abs(qty)),
                    latest_prices.get(symbol),
                    submitted.id,
                    f"{submitted.status} (trailing_stop)",
                ))
            except APIError as exc:
                orders_to_log.append((
                    datetime.now(timezone.utc).isoformat(),
                    symbol,
                    trail_side.value,
                    float(abs(qty)),
                    latest_prices.get(symbol),
                    None,
                    f"trailing_stop_rejected: {exc}",
                ))

    return datetime.now(timezone.utc).isoformat(), orders_to_log, signals, decision_context


def rebalance_portfolio(
    config: Config,
    symbols: list[str],
    bot_name: str = "ml",
) -> tuple[str, list[OrderLogRow], list[Signal], dict]:
    latest, signals, regime_lev, spy_vol, decision_context = generate_signals(config, symbols, bot_name=bot_name)
    return execute_signals(
        config,
        latest,
        signals,
        regime_lev,
        spy_vol,
        decision_context,
        bot_name=bot_name,
    )


def caretaker_portfolio(
    config: Config,
    bot_name: str = "ml",
) -> tuple[str, list[OrderLogRow], dict[str, Any]]:
    account_config = get_bot_account_config(config, bot_name)
    trading = TradingClient(account_config.api_key, account_config.secret_key, paper=True)
    account = trading.get_account()
    positions = list(trading.get_all_positions())
    ts = datetime.now(timezone.utc).isoformat()
    orders_to_log: list[OrderLogRow] = []
    summary: dict[str, Any] = {
        "bot_name": bot_name,
        "positions_seen": len(positions),
        "already_protected": 0,
        "protection_submitted": 0,
        "protection_rejected": 0,
        "skipped_fractional": 0,
        "skipped_open_order": 0,
        "kill_switch_triggered": False,
        "daily_drawdown": None,
    }

    daily_drawdown = _current_day_drawdown(config, bot_name, float(account.equity))
    summary["daily_drawdown"] = daily_drawdown
    if (
        daily_drawdown is not None
        and config.caretaker_daily_drawdown_limit > 0
        and daily_drawdown >= config.caretaker_daily_drawdown_limit
        and positions
    ):
        summary["kill_switch_triggered"] = True
        try:
            trading.cancel_orders()
        except Exception:
            pass
        for position in positions:
            try:
                orders_to_log.append(_flatten_position_order(position, trading))
            except APIError as exc:
                qty = abs(float(position.qty))
                side = OrderSide.SELL if float(position.qty) > 0 else OrderSide.BUY
                orders_to_log.append(
                    (
                        datetime.now(timezone.utc).isoformat(),
                        position.symbol,
                        side.value,
                        qty,
                        _optional_float(getattr(position, "current_price", None)),
                        None,
                        f"caretaker_kill_switch_rejected: {exc}",
                    )
                )
        return ts, orders_to_log, summary

    if not config.caretaker_trailing_stop_enabled:
        summary["protection_disabled"] = True
        return ts, orders_to_log, summary

    trail_percent = _caretaker_trail_percent(config)
    if trail_percent is None:
        summary["protection_disabled"] = True
        summary["protection_reason"] = "No trailing-stop percent or stop-loss percentage configured."
        return ts, orders_to_log, summary

    open_orders = _flatten_orders(_load_open_orders(trading, nested=True))
    for position in positions:
        qty = float(position.qty)
        if abs(qty) < 1e-6:
            continue
        symbol = position.symbol
        position_orders = [order for order in open_orders if getattr(order, "symbol", None) == symbol]
        protection = _protection_summary_for_position(qty, position_orders)
        if int(protection.get("open_exit_order_count") or 0) > 0:
            summary["already_protected"] += 1
            continue
        if position_orders:
            summary["skipped_open_order"] += 1
            continue
        if not _is_whole_share_qty(abs(qty)):
            summary["skipped_fractional"] += 1
            continue

        side = OrderSide.SELL if qty > 0 else OrderSide.BUY
        trailing_order = _build_trailing_stop_order(
            symbol,
            abs(qty),
            side,
            config,
            trail_percent_override=trail_percent,
        )
        if trailing_order is None:
            summary["skipped_fractional"] += 1
            continue
        try:
            submitted = trading.submit_order(trailing_order)
            summary["protection_submitted"] += 1
            orders_to_log.append(
                (
                    datetime.now(timezone.utc).isoformat(),
                    symbol,
                    side.value,
                    float(abs(qty)),
                    _optional_float(getattr(position, "current_price", None)),
                    submitted.id,
                    f"{submitted.status} (caretaker_trailing_stop)",
                )
            )
        except APIError as exc:
            summary["protection_rejected"] += 1
            orders_to_log.append(
                (
                    datetime.now(timezone.utc).isoformat(),
                    symbol,
                    side.value,
                    float(abs(qty)),
                    _optional_float(getattr(position, "current_price", None)),
                    None,
                    f"caretaker_trailing_stop_rejected: {exc}",
                )
            )

    summary["trail_percent"] = trail_percent
    return ts, orders_to_log, summary


def snapshot_positions(
    config: Config,
    bot_name: str = "ml",
) -> tuple[str, list[tuple[str, float, float | None, float | None, float | None]]]:
    account_config = get_bot_account_config(config, bot_name)
    trading = TradingClient(account_config.api_key, account_config.secret_key, paper=True)
    positions = trading.get_all_positions()
    rows = []
    for p in positions:
        rows.append((p.symbol, float(p.qty), float(p.avg_entry_price), float(p.market_value), float(p.unrealized_pl)))
    return datetime.now(timezone.utc).isoformat(), rows


def snapshot_positions_with_protection(config: Config, bot_name: str = "ml") -> tuple[str, list[dict[str, Any]]]:
    account_config = get_bot_account_config(config, bot_name)
    trading = TradingClient(account_config.api_key, account_config.secret_key, paper=True)
    positions = trading.get_all_positions()
    open_orders = _flatten_orders(_load_open_orders(trading, nested=True))
    ts = datetime.now(timezone.utc).isoformat()
    rows: list[dict[str, Any]] = []
    for position in positions:
        qty = float(position.qty)
        symbol = position.symbol
        position_orders = [order for order in open_orders if getattr(order, "symbol", None) == symbol]
        protection = _protection_summary_for_position(qty, position_orders)
        rows.append(
            {
                "symbol": symbol,
                "qty": qty,
                "avg_entry": float(position.avg_entry_price),
                "avg_entry_price": float(position.avg_entry_price),
                "market_value": float(position.market_value),
                "unreal_pl": float(position.unrealized_pl),
                "unrealized_pl": float(position.unrealized_pl),
                "side": "Short" if qty < 0 else "Long",
                **protection,
            }
        )
    rows.sort(key=lambda row: abs(float(row.get("market_value", 0.0))), reverse=True)
    return ts, rows


def snapshot_equity(config: Config, bot_name: str = "ml") -> tuple[str, float, float, float]:
    account_config = get_bot_account_config(config, bot_name)
    trading = TradingClient(account_config.api_key, account_config.secret_key, paper=True)
    account = trading.get_account()
    ts = datetime.now(timezone.utc).isoformat()
    return ts, float(account.equity), float(account.cash), float(account.portfolio_value)
