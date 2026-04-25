from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from alpaca.common.exceptions import APIError
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import ContractType
from alpaca.trading.requests import GetOptionContractsRequest

from .config import Config
from .logging_db import log_strategy_report
from .trader import Signal, generate_signals


@dataclass
class OptionsScaffoldReport:
    ts: str
    headline: str
    summary: str
    report_path: str


@dataclass
class VerticalSpreadIdea:
    symbol: str
    side: str
    structure: str
    expiry: str
    spot_price: float
    long_leg_symbol: str
    short_leg_symbol: str
    long_strike: float
    short_strike: float
    long_leg_price: float
    short_leg_price: float
    net_debit: float
    width: float
    max_profit: float
    max_loss: float
    breakeven: float
    signal_score: float
    base_score: float
    rationale: str
    thesis: str


def _safe_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except Exception:
        return None


def _fetch_option_contracts(
    trading: TradingClient,
    symbol: str,
    option_type: ContractType,
    spot_price: float,
    min_dte: int,
    max_dte: int,
) -> list:
    today = date.today()
    min_expiry = today + timedelta(days=max(1, min_dte))
    max_expiry = today + timedelta(days=max(min_dte + 1, max_dte))
    strike_floor = max(1.0, spot_price * 0.75)
    strike_ceiling = max(strike_floor + 1.0, spot_price * 1.25)
    request = GetOptionContractsRequest(
        underlying_symbols=[symbol],
        type=option_type,
        expiration_date_gte=min_expiry.isoformat(),
        expiration_date_lte=max_expiry.isoformat(),
        strike_price_gte=f"{strike_floor:.2f}",
        strike_price_lte=f"{strike_ceiling:.2f}",
        limit=500,
    )
    response = trading.get_option_contracts(request)
    contracts = list(getattr(response, "option_contracts", []) or [])
    return [contract for contract in contracts if bool(getattr(contract, "tradable", False))]


def _pick_contract_close(contract: object) -> float | None:
    return _safe_float(getattr(contract, "close_price", None))


def _choose_vertical_spread(
    signal: Signal,
    spot_price: float,
    contracts: list,
    width_pct: float,
    min_reward_risk: float,
    max_debit_pct_of_width: float,
) -> VerticalSpreadIdea | None:
    if not contracts or spot_price <= 0:
        return None

    desired_width = max(1.0, spot_price * max(width_pct, 0.01))
    expiries = sorted({getattr(contract, "expiration_date", None) for contract in contracts if getattr(contract, "expiration_date", None)})
    for expiry in expiries:
        expiry_contracts = [contract for contract in contracts if getattr(contract, "expiration_date", None) == expiry]
        priced_contracts = []
        for contract in expiry_contracts:
            price = _pick_contract_close(contract)
            strike = _safe_float(getattr(contract, "strike_price", None))
            if price is None or strike is None or price <= 0:
                continue
            priced_contracts.append((contract, strike, price))
        if len(priced_contracts) < 2:
            continue

        if signal.side == "LONG":
            priced_contracts.sort(key=lambda item: item[1])
            long_candidates = [item for item in priced_contracts if item[1] >= spot_price * 0.98] or priced_contracts
            long_leg, long_strike, long_price = min(long_candidates, key=lambda item: abs(item[1] - spot_price))
            short_candidates = [item for item in priced_contracts if item[1] > long_strike]
            if not short_candidates:
                continue
            short_leg, short_strike, short_price = min(
                short_candidates,
                key=lambda item: abs((item[1] - long_strike) - desired_width),
            )
            width = short_strike - long_strike
            net_debit = long_price - short_price
            breakeven = long_strike + net_debit
            structure = "Bull Call Debit Spread"
            thesis = "Uses a bullish stock signal with capped downside and capped upside."
        elif signal.side == "SHORT":
            priced_contracts.sort(key=lambda item: item[1], reverse=True)
            long_candidates = [item for item in priced_contracts if item[1] <= spot_price * 1.02] or priced_contracts
            long_leg, long_strike, long_price = min(long_candidates, key=lambda item: abs(item[1] - spot_price))
            short_candidates = [item for item in priced_contracts if item[1] < long_strike]
            if not short_candidates:
                continue
            short_leg, short_strike, short_price = min(
                short_candidates,
                key=lambda item: abs((long_strike - item[1]) - desired_width),
            )
            width = long_strike - short_strike
            net_debit = long_price - short_price
            breakeven = long_strike - net_debit
            structure = "Bear Put Debit Spread"
            thesis = "Uses a bearish stock signal with defined risk instead of naked short gamma exposure."
        else:
            return None

        max_profit = width - net_debit
        max_loss = net_debit
        if width <= 0 or net_debit <= 0 or max_profit <= 0:
            continue
        reward_risk = max_profit / max_loss if max_loss > 0 else 0.0
        debit_pct_of_width = net_debit / width if width > 0 else 1.0
        if min_reward_risk > 0 and reward_risk < min_reward_risk:
            continue
        if max_debit_pct_of_width > 0 and debit_pct_of_width > max_debit_pct_of_width:
            continue

        return VerticalSpreadIdea(
            symbol=signal.symbol,
            side=signal.side,
            structure=structure,
            expiry=str(expiry),
            spot_price=spot_price,
            long_leg_symbol=str(getattr(long_leg, "symbol", "")),
            short_leg_symbol=str(getattr(short_leg, "symbol", "")),
            long_strike=float(long_strike),
            short_strike=float(short_strike),
            long_leg_price=float(long_price),
            short_leg_price=float(short_price),
            net_debit=float(net_debit),
            width=float(width),
            max_profit=float(max_profit),
            max_loss=float(max_loss),
            breakeven=float(breakeven),
            signal_score=float(signal.score),
            base_score=float(signal.base_score if signal.base_score is not None else signal.score),
            rationale=signal.rationale or "",
            thesis=thesis,
        )
    return None


def _report_body(ideas: list[VerticalSpreadIdea], generated_ts: str) -> str:
    if not ideas:
        return (
            "## No options ideas generated\n\n"
            "The bot found no debit-spread structures that met the current signal and contract-selection rules. "
            "That usually means either the option chain was too sparse, the recent contract close prices were missing, "
            "or the available strikes made the risk/reward unattractive.\n"
        )

    lines = [
        "# Options Scaffold Report",
        "",
        f"Generated at: {generated_ts}",
        "",
        "This is a paper-only idea report. It converts the bot's strongest directional stock ideas into defined-risk vertical spreads.",
        "These are candidate structures for review, not unattended auto-execution.",
        "",
    ]
    for idea in ideas:
        reward_risk = idea.max_profit / idea.max_loss if idea.max_loss > 0 else 0.0
        lines.extend(
            [
                f"## {idea.symbol} — {idea.structure}",
                "",
                f"- Signal: {idea.side} idea with base score {idea.base_score:.2%} and final score {idea.signal_score:.2%}",
                f"- Underlying spot: ${idea.spot_price:,.2f}",
                f"- Expiry: {idea.expiry}",
                f"- Long leg: `{idea.long_leg_symbol}` at strike ${idea.long_strike:,.2f} using recent close ${idea.long_leg_price:,.2f}",
                f"- Short leg: `{idea.short_leg_symbol}` at strike ${idea.short_strike:,.2f} using recent close ${idea.short_leg_price:,.2f}",
                f"- Estimated net debit: ${idea.net_debit:,.2f}",
                f"- Max loss: ${idea.max_loss:,.2f}",
                f"- Max profit: ${idea.max_profit:,.2f}",
                f"- Breakeven at expiry: ${idea.breakeven:,.2f}",
                f"- Reward/risk estimate: {reward_risk:.2f}x",
                f"- Thesis: {idea.thesis}",
                f"- Bot rationale: {idea.rationale or 'No additional rationale captured.'}",
                "",
                "Risk notes:",
                "- This estimate uses Alpaca contract close prices, not live bid/ask spreads.",
                "- Actual fill quality can be materially worse around wide spreads or low liquidity.",
                "- The scaffold filters out spreads with weak estimated reward/risk or excessive debit relative to width.",
                "- Defined risk does not mean low risk; time decay and volatility compression still matter.",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def generate_options_scaffold_report(config: Config, symbols: list[str]) -> OptionsScaffoldReport:
    latest, signals, _, _, _ = generate_signals(config, symbols)
    latest_prices = {str(row["Symbol"]): float(row["close"]) for _, row in latest.iterrows()}
    selected = [signal for signal in signals if signal.selected and signal.side in {"LONG", "SHORT"}]
    selected.sort(key=lambda signal: abs(float(signal.score)), reverse=True)
    candidates = selected[: max(1, config.options_idea_limit)]

    trading = TradingClient(config.alpaca_api_key, config.alpaca_secret_key, paper=True)
    ideas: list[VerticalSpreadIdea] = []
    for signal in candidates:
        spot_price = latest_prices.get(signal.symbol)
        if spot_price is None or spot_price <= 0:
            continue
        contract_type = ContractType.CALL if signal.side == "LONG" else ContractType.PUT
        try:
            contracts = _fetch_option_contracts(
                trading,
                signal.symbol,
                contract_type,
                spot_price,
                config.options_min_dte,
                config.options_max_dte,
            )
        except APIError:
            continue
        idea = _choose_vertical_spread(
            signal,
            spot_price,
            contracts,
            config.options_spread_width_pct,
            config.options_min_reward_risk,
            config.options_max_debit_pct_of_width,
        )
        if idea is not None:
            ideas.append(idea)

    ideas.sort(key=lambda idea: abs(float(idea.signal_score)), reverse=True)
    ideas = ideas[: config.options_idea_limit]

    generated_ts = datetime.now(timezone.utc).isoformat()
    headline = "Options Scaffold Report"
    if ideas:
        bullish = sum(1 for idea in ideas if idea.side == "LONG")
        bearish = sum(1 for idea in ideas if idea.side == "SHORT")
        summary = (
            f"Generated {len(ideas)} defined-risk vertical spread ideas "
            f"({bullish} bullish, {bearish} bearish) from the strongest current stock signals."
        )
    else:
        summary = "No defined-risk vertical spread ideas passed the current contract-selection rules."

    body = _report_body(ideas, generated_ts)
    reports_dir = Path(config.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    filename_ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_path = reports_dir / f"options_scaffold_{filename_ts}.md"
    report_path.write_text(body, encoding="utf-8")

    metrics = {
        "idea_count": len(ideas),
        "bullish_count": sum(1 for idea in ideas if idea.side == "LONG"),
        "bearish_count": sum(1 for idea in ideas if idea.side == "SHORT"),
        "min_dte": config.options_min_dte,
        "max_dte": config.options_max_dte,
        "target_width_pct": config.options_spread_width_pct,
        "min_reward_risk": config.options_min_reward_risk,
        "max_debit_pct_of_width": config.options_max_debit_pct_of_width,
    }
    changes = {
        "options_scaffold": "paper_only",
        "allowed_structures": ["bull_call_debit_spread", "bear_put_debit_spread"],
    }
    log_strategy_report(
        config.db_path,
        generated_ts,
        "options_scaffold",
        headline,
        summary,
        body,
        json.dumps(metrics, sort_keys=True),
        json.dumps(changes, sort_keys=True),
    )
    return OptionsScaffoldReport(
        ts=generated_ts,
        headline=headline,
        summary=summary,
        report_path=str(report_path),
    )
