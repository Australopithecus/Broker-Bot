from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable

import pandas as pd
from alpaca.data import StockBarsRequest
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame

from .config import Config, get_bot_account_config

@dataclass
class MarketData:
    bars: pd.DataFrame


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def fetch_daily_bars(
    config: Config,
    symbols: Iterable[str],
    start: datetime,
    end: datetime,
    bot_name: str = "ml",
) -> MarketData:
    account = get_bot_account_config(config, bot_name)
    client = StockHistoricalDataClient(account.api_key, account.secret_key)
    request = StockBarsRequest(
        symbol_or_symbols=list(symbols),
        timeframe=TimeFrame.Day,
        start=_to_utc(start),
        end=_to_utc(end),
        feed=account.data_feed,
    )
    bars = client.get_stock_bars(request).df
    if bars.empty:
        raise RuntimeError("No historical bars returned. Check symbols, dates, or data feed access.")
    bars = bars.reset_index().rename(columns={"symbol": "Symbol"})
    return MarketData(bars=bars)


def default_lookback_window(days: int) -> tuple[datetime, datetime]:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    return start, end


def fetch_latest_close(config: Config, symbol: str, bot_name: str = "ml") -> float | None:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=10)
    data = fetch_daily_bars(config, [symbol], start, end, bot_name=bot_name).bars
    if data.empty:
        return None
    latest = data.sort_values("timestamp").iloc[-1]
    return float(latest["close"])
