from __future__ import annotations

import json
import os
from dataclasses import dataclass

from dotenv import load_dotenv

from .bots import LLM_BOT_NAME, ML_BOT_NAME, normalize_bot_name

load_dotenv()


@dataclass(frozen=True)
class BrokerAccountConfig:
    bot_name: str
    api_key: str
    secret_key: str
    paper_url: str
    data_feed: str


@dataclass(frozen=True)
class Config:
    alpaca_api_key: str
    alpaca_secret_key: str
    alpaca_paper_url: str
    alpaca_data_feed: str
    llm_alpaca_api_key: str
    llm_alpaca_secret_key: str
    llm_alpaca_paper_url: str
    llm_alpaca_data_feed: str
    universe_path: str
    db_path: str
    model_dir: str
    reports_dir: str
    advisor_overrides_path: str
    learned_policy_path: str
    sector_map_path: str
    training_lookback_days: int
    prediction_horizon_days: int
    rebalance_top_k: int
    min_long_return: float
    max_short_return: float
    min_signal_abs_score: float
    llm_min_conviction: float
    llm_skeptic_enabled: bool
    llm_skeptic_veto_enabled: bool
    max_position_pct: float
    gross_leverage: float
    bear_leverage: float
    rebalance_frequency: str
    tcost_bps: float
    min_price: float
    min_dollar_vol: float
    vol_target: float
    vol_window: int
    max_drawdown: float
    min_leverage: float
    drawdown_window: int
    miss_rebalance_prob: float
    rebalance_delay_days: int
    sim_seed: int
    advisor_auto_apply: bool
    llm_enabled: bool
    llm_model: str
    research_candidate_limit: int
    news_lookback_days: int
    technical_weight: float
    snapshot_weight: float
    screener_weight: float
    news_weight: float
    memory_weight: float
    llm_weight: float
    execution_order_mode: str
    bracket_take_profit_pct: float
    bracket_stop_loss_pct: float
    adaptive_exits_enabled: bool
    stop_loss_vol_multiple: float
    take_profit_reward_multiple: float
    min_stop_loss_pct: float
    max_stop_loss_pct: float
    trailing_stop_enabled: bool
    trailing_stop_percent: float
    trailing_stop_price: float
    trailing_stop_time_in_force: str
    max_sector_exposure_pct: float
    max_correlated_exposure_pct: float
    correlation_threshold: float
    correlation_window: int
    options_min_dte: int
    options_max_dte: int
    options_idea_limit: int
    options_spread_width_pct: float
    options_min_reward_risk: float
    options_max_debit_pct_of_width: float
    caretaker_trailing_stop_enabled: bool
    caretaker_trailing_stop_percent: float
    caretaker_daily_drawdown_limit: float


def _load_json_overrides(path: str) -> dict[str, float]:
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle) or {}
    except Exception:
        return {}

    if isinstance(payload, dict) and isinstance(payload.get("weights"), dict):
        payload = payload["weights"]
    if not isinstance(payload, dict):
        return {}
    return payload


def load_config() -> Config:
    api_key = os.getenv("ALPACA_API_KEY", "").strip()
    secret_key = os.getenv("ALPACA_SECRET_KEY", "").strip()
    paper_url = os.getenv("ALPACA_PAPER_URL", "https://paper-api.alpaca.markets").strip()
    data_feed = os.getenv("ALPACA_DATA_FEED", "iex").strip() or "iex"
    llm_api_key = os.getenv("ALPACA_LLM_API_KEY", "").strip()
    llm_secret_key = os.getenv("ALPACA_LLM_SECRET_KEY", "").strip()
    llm_paper_url = os.getenv("ALPACA_LLM_PAPER_URL", paper_url).strip() or paper_url
    llm_data_feed = os.getenv("ALPACA_LLM_DATA_FEED", data_feed).strip() or data_feed
    overrides_path = os.getenv("ADVISOR_OVERRIDES_PATH", "data/advisor_overrides.json").strip()
    learned_policy_path = os.getenv("LEARNED_POLICY_PATH", "data/learned_policy.json").strip()
    auto_apply_flag = os.getenv("ADVISOR_AUTO_APPLY", "1").strip().lower() in {"1", "true", "yes", "y"}
    sector_map_path = os.getenv("SECTOR_MAP_PATH", "data/sector_map.csv").strip()

    if not api_key or not secret_key:
        raise RuntimeError("Missing ALPACA_API_KEY or ALPACA_SECRET_KEY in environment.")

    advisor_overrides = _load_json_overrides(overrides_path)
    learned_policy = _load_json_overrides(learned_policy_path)

    def _advisor_override(name: str, default: float) -> float:
        try:
            return float(advisor_overrides.get(name, default))
        except Exception:
            return default

    def _advisor_override_int(name: str, default: int) -> int:
        try:
            return int(advisor_overrides.get(name, default))
        except Exception:
            return default

    def _policy_override(name: str, default: float) -> float:
        try:
            return float(learned_policy.get(name, default))
        except Exception:
            return default

    return Config(
        alpaca_api_key=api_key,
        alpaca_secret_key=secret_key,
        alpaca_paper_url=paper_url,
        alpaca_data_feed=data_feed,
        llm_alpaca_api_key=llm_api_key,
        llm_alpaca_secret_key=llm_secret_key,
        llm_alpaca_paper_url=llm_paper_url,
        llm_alpaca_data_feed=llm_data_feed,
        universe_path=os.getenv("UNIVERSE_PATH", "data/sp500.csv"),
        db_path=os.getenv("BROKER_BOT_DB", "data/broker_bot.sqlite"),
        model_dir=os.getenv("MODEL_DIR", "data/models"),
        reports_dir=os.getenv("REPORTS_DIR", "data/reports"),
        advisor_overrides_path=overrides_path,
        learned_policy_path=learned_policy_path,
        sector_map_path=sector_map_path,
        training_lookback_days=int(os.getenv("TRAIN_LOOKBACK_DAYS", "252")),
        prediction_horizon_days=int(os.getenv("PRED_HORIZON_DAYS", "1")),
        rebalance_top_k=_advisor_override_int("rebalance_top_k", int(os.getenv("REBALANCE_TOP_K", "40"))),
        min_long_return=_advisor_override("min_long_return", float(os.getenv("MIN_LONG_RETURN", "0.001"))),
        max_short_return=_advisor_override("max_short_return", float(os.getenv("MAX_SHORT_RETURN", "-0.001"))),
        min_signal_abs_score=_advisor_override("min_signal_abs_score", float(os.getenv("MIN_SIGNAL_ABS_SCORE", "0.0015"))),
        llm_min_conviction=float(os.getenv("LLM_MIN_CONVICTION", "0.55")),
        llm_skeptic_enabled=os.getenv("LLM_SKEPTIC_ENABLED", "1").strip().lower() in {"1", "true", "yes", "y"},
        llm_skeptic_veto_enabled=os.getenv("LLM_SKEPTIC_VETO_ENABLED", "1").strip().lower() in {"1", "true", "yes", "y"},
        max_position_pct=_advisor_override("max_position_pct", float(os.getenv("MAX_POSITION_PCT", "0.06"))),
        gross_leverage=_advisor_override("gross_leverage", float(os.getenv("GROSS_LEVERAGE", "1.5"))),
        bear_leverage=_advisor_override("bear_leverage", float(os.getenv("BEAR_LEVERAGE", "0.6"))),
        rebalance_frequency=os.getenv("REBALANCE_FREQUENCY", "W-FRI"),
        tcost_bps=_advisor_override("tcost_bps", float(os.getenv("TCOST_BPS", "5"))),
        min_price=_advisor_override("min_price", float(os.getenv("MIN_PRICE", "5"))),
        min_dollar_vol=_advisor_override("min_dollar_vol", float(os.getenv("MIN_DOLLAR_VOL", "5000000"))),
        vol_target=_advisor_override("vol_target", float(os.getenv("VOL_TARGET", "0.02"))),
        vol_window=_advisor_override_int("vol_window", int(os.getenv("VOL_WINDOW", "20"))),
        max_drawdown=_advisor_override("max_drawdown", float(os.getenv("MAX_DRAWDOWN", "0.10"))),
        min_leverage=_advisor_override("min_leverage", float(os.getenv("MIN_LEVERAGE", "0.2"))),
        drawdown_window=_advisor_override_int("drawdown_window", int(os.getenv("DRAWDOWN_WINDOW", "120"))),
        miss_rebalance_prob=_advisor_override("miss_rebalance_prob", float(os.getenv("MISS_REBALANCE_PROB", "0.0"))),
        rebalance_delay_days=_advisor_override_int("rebalance_delay_days", int(os.getenv("REBALANCE_DELAY_DAYS", "0"))),
        sim_seed=_advisor_override_int("sim_seed", int(os.getenv("SIM_SEED", "42"))),
        advisor_auto_apply=auto_apply_flag,
        llm_enabled=os.getenv("LLM_ENABLED", "0").strip().lower() in {"1", "true", "yes", "y"},
        llm_model=os.getenv("LLM_MODEL", "gpt-5-mini").strip() or "gpt-5-mini",
        research_candidate_limit=int(os.getenv("RESEARCH_CANDIDATE_LIMIT", "18")),
        news_lookback_days=int(os.getenv("NEWS_LOOKBACK_DAYS", "3")),
        technical_weight=_policy_override("technical_weight", float(os.getenv("TECHNICAL_WEIGHT", "1.0"))),
        snapshot_weight=_policy_override("snapshot_weight", float(os.getenv("SNAPSHOT_WEIGHT", "0.8"))),
        screener_weight=_policy_override("screener_weight", float(os.getenv("SCREENER_WEIGHT", "0.7"))),
        news_weight=_policy_override("news_weight", float(os.getenv("NEWS_WEIGHT", "0.9"))),
        memory_weight=_policy_override("memory_weight", float(os.getenv("MEMORY_WEIGHT", "0.8"))),
        llm_weight=_policy_override("llm_weight", float(os.getenv("LLM_WEIGHT", "0.8"))),
        execution_order_mode=os.getenv("EXECUTION_ORDER_MODE", "simple").strip().lower() or "simple",
        bracket_take_profit_pct=float(os.getenv("BRACKET_TAKE_PROFIT_PCT", "0.04")),
        bracket_stop_loss_pct=float(os.getenv("BRACKET_STOP_LOSS_PCT", "0.02")),
        adaptive_exits_enabled=os.getenv("ADAPTIVE_EXITS_ENABLED", "1").strip().lower() in {"1", "true", "yes", "y"},
        stop_loss_vol_multiple=float(os.getenv("STOP_LOSS_VOL_MULTIPLE", "1.25")),
        take_profit_reward_multiple=float(os.getenv("TAKE_PROFIT_REWARD_MULTIPLE", "2.0")),
        min_stop_loss_pct=float(os.getenv("MIN_STOP_LOSS_PCT", "0.015")),
        max_stop_loss_pct=float(os.getenv("MAX_STOP_LOSS_PCT", "0.12")),
        trailing_stop_enabled=os.getenv("TRAILING_STOP_ENABLED", "0").strip().lower() in {"1", "true", "yes", "y"},
        trailing_stop_percent=float(os.getenv("TRAILING_STOP_PERCENT", "0.0")),
        trailing_stop_price=float(os.getenv("TRAILING_STOP_PRICE", "0.0")),
        trailing_stop_time_in_force=os.getenv("TRAILING_STOP_TIF", "gtc").strip().lower() or "gtc",
        max_sector_exposure_pct=_advisor_override("max_sector_exposure_pct", float(os.getenv("MAX_SECTOR_EXPOSURE_PCT", "0.35"))),
        max_correlated_exposure_pct=_advisor_override("max_correlated_exposure_pct", float(os.getenv("MAX_CORRELATED_EXPOSURE_PCT", "0.35"))),
        correlation_threshold=_advisor_override("correlation_threshold", float(os.getenv("CORRELATION_THRESHOLD", "0.85"))),
        correlation_window=_advisor_override_int("correlation_window", int(os.getenv("CORRELATION_WINDOW", "90"))),
        options_min_dte=int(os.getenv("OPTIONS_MIN_DTE", "14")),
        options_max_dte=int(os.getenv("OPTIONS_MAX_DTE", "45")),
        options_idea_limit=int(os.getenv("OPTIONS_IDEA_LIMIT", "6")),
        options_spread_width_pct=float(os.getenv("OPTIONS_SPREAD_WIDTH_PCT", "0.05")),
        options_min_reward_risk=float(os.getenv("OPTIONS_MIN_REWARD_RISK", "0.9")),
        options_max_debit_pct_of_width=float(os.getenv("OPTIONS_MAX_DEBIT_PCT_OF_WIDTH", "0.55")),
        caretaker_trailing_stop_enabled=os.getenv("CARETAKER_TRAILING_STOP_ENABLED", "1").strip().lower() in {"1", "true", "yes", "y"},
        caretaker_trailing_stop_percent=float(os.getenv("CARETAKER_TRAILING_STOP_PERCENT", "0.0")),
        caretaker_daily_drawdown_limit=float(os.getenv("CARETAKER_DAILY_DRAWDOWN_LIMIT", "0.0")),
    )


def get_bot_account_config(config: Config, bot_name: str | None = None) -> BrokerAccountConfig:
    normalized = normalize_bot_name(bot_name)
    if normalized == LLM_BOT_NAME:
        if not config.llm_alpaca_api_key or not config.llm_alpaca_secret_key:
            raise RuntimeError(
                "Missing ALPACA_LLM_API_KEY or ALPACA_LLM_SECRET_KEY in environment for the LLM bot."
            )
        return BrokerAccountConfig(
            bot_name=LLM_BOT_NAME,
            api_key=config.llm_alpaca_api_key,
            secret_key=config.llm_alpaca_secret_key,
            paper_url=config.llm_alpaca_paper_url,
            data_feed=config.llm_alpaca_data_feed,
        )
    return BrokerAccountConfig(
        bot_name=ML_BOT_NAME,
        api_key=config.alpaca_api_key,
        secret_key=config.alpaca_secret_key,
        paper_url=config.alpaca_paper_url,
        data_feed=config.alpaca_data_feed,
    )


def configured_bot_names(config: Config) -> list[str]:
    bots = [ML_BOT_NAME]
    if config.llm_alpaca_api_key and config.llm_alpaca_secret_key:
        bots.append(LLM_BOT_NAME)
    return bots
