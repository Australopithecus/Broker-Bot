import os
from urllib.parse import parse_qs, urlsplit

import pandas as pd
import requests
import streamlit as st

from broker_bot.dashboard_metrics import (
    WINDOW_OPTIONS,
    agreement_summary,
    bot_performance_metrics,
    comparison_table,
    extract_key_takeaways,
    filter_frame_to_window,
    freshness_status,
)


def _secret(name: str) -> str:
    value = os.getenv(name, "").strip()
    if value:
        return value
    try:
        secret_value = st.secrets.get(name, "")
    except Exception:
        secret_value = ""
    return str(secret_value).strip() if secret_value else ""


API_BASE = _secret("API_BASE_URL")
API_TOKEN = _secret("API_TOKEN")
DATA_URL = _secret("DATA_URL")
GITHUB_ACTIONS_TOKEN = _secret("GITHUB_ACTIONS_TOKEN")
GITHUB_REPOSITORY = _secret("GITHUB_REPOSITORY")
GITHUB_WORKFLOW_ID = _secret("GITHUB_WORKFLOW_ID") or "advisor_snapshot.yml"
GITHUB_WORKFLOW_REF = _secret("GITHUB_WORKFLOW_REF") or "main"
LLM_TREND_CUTOFF = pd.Timestamp("2026-04-23T00:00:00Z")

st.set_page_config(page_title="Broker Bot Dashboard", layout="wide")
st.title("Broker Bot Dashboard")
st.caption("A single trend graph sits at the top, while the sections below keep each bot's trades, reports, and positions separate.")


@st.cache_data(ttl=60)
def _load_snapshot() -> dict:
    if not DATA_URL:
        return {}
    resp = requests.get(
        DATA_URL,
        timeout=20,
        headers={
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    resp.raise_for_status()
    return resp.json()


def _bot_query(path: str) -> str | None:
    parsed = urlsplit(path)
    params = parse_qs(parsed.query)
    values = params.get("bot")
    return values[0] if values else None


def _github_repo_from_data_url() -> str:
    if GITHUB_REPOSITORY:
        return GITHUB_REPOSITORY
    if not DATA_URL:
        return ""
    parsed = urlsplit(DATA_URL)
    parts = [part for part in parsed.path.split("/") if part]
    if parsed.netloc == "raw.githubusercontent.com" and len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    if parsed.netloc in {"github.com", "www.github.com"} and len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return ""


def _github_actions_url(repo: str) -> str:
    if not repo:
        return ""
    return f"https://github.com/{repo}/actions/workflows/{GITHUB_WORKFLOW_ID}"


def _dispatch_github_workflow(repo: str) -> tuple[bool, str]:
    if not repo:
        return False, "Set GITHUB_REPOSITORY in Streamlit secrets, for example YOUR_USERNAME/YOUR_REPO."
    if not GITHUB_ACTIONS_TOKEN:
        return False, "Set GITHUB_ACTIONS_TOKEN in Streamlit secrets before triggering runs from the dashboard."

    url = f"https://api.github.com/repos/{repo}/actions/workflows/{GITHUB_WORKFLOW_ID}/dispatches"
    resp = requests.post(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_ACTIONS_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={"ref": GITHUB_WORKFLOW_REF},
        timeout=20,
    )
    if resp.status_code == 204:
        return True, f"Started Broker Bot Cloud Run on {GITHUB_WORKFLOW_REF}."
    try:
        detail = resp.json().get("message", resp.text)
    except Exception:
        detail = resp.text
    return False, f"GitHub returned {resp.status_code}: {detail}"


def fetch(path: str):
    route = urlsplit(path).path
    if API_BASE:
        headers = {"X-API-Token": API_TOKEN} if API_TOKEN else {}
        url = API_BASE.rstrip("/") + path
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        return resp.json()
    if DATA_URL:
        data = _load_snapshot()
        bots = data.get("bots", {})
        if not isinstance(bots, dict) or not bots:
            bots = {"ml": data}
        requested_bot = (_bot_query(path) or "ml").lower()
        bot_payload = bots.get(requested_bot, {})

        if route == "/api/bots":
            return {
                "data": [
                    {"name": name, "label": payload.get("label", name.upper())}
                    for name, payload in bots.items()
                ]
            }
        if route == "/api/summary":
            equity = bot_payload.get("equity", [])
            if not equity:
                return {"status": "empty", "message": "No equity snapshots yet."}
            latest = equity[-1]
            return {
                "status": "ok",
                "bot_name": requested_bot,
                "bot_label": bot_payload.get("label", requested_bot.upper()),
                "ts": latest["ts"],
                "equity": latest["equity"],
                "cash": latest.get("cash", 0.0),
                "portfolio": latest.get("portfolio_value", 0.0),
                "spy": latest.get("spy_value"),
            }
        if route == "/api/equity":
            rows = bot_payload.get("equity", [])
            return {
                "data": [
                    {
                        "ts": row.get("ts"),
                        "equity": row.get("equity"),
                        "portfolio_value": row.get("portfolio_value", row.get("equity")),
                        "spy": row.get("spy", row.get("spy_value")),
                    }
                    for row in rows
                ]
            }
        if route == "/api/positions":
            return {"data": bot_payload.get("positions", [])}
        if route == "/api/trades":
            return {"data": bot_payload.get("trades", [])}
        if route == "/api/advisor":
            return {"data": bot_payload.get("advisor_reports", [])}
        if route == "/api/strategy":
            return {"data": bot_payload.get("strategy_reports", [])}
        if route == "/api/decisions":
            return {"data": bot_payload.get("decisions", [])}
        return {}
    st.error("Set API_BASE_URL or DATA_URL in Streamlit secrets.")
    st.stop()


def _load_bot_names() -> list[tuple[str, str]]:
    try:
        response = fetch("/api/bots")
    except Exception:
        return [("ml", "ML Bot")]
    rows = response.get("data", [])
    names = []
    for row in rows:
        name = str(row.get("name", "")).strip().lower()
        label = str(row.get("label", name.upper())).strip()
        if name:
            names.append((name, label))
    return names or [("ml", "ML Bot")]


def _equity_df(bot_name: str) -> pd.DataFrame:
    rows = fetch(f"/api/equity?bot={bot_name}&limit=1000").get("data", [])
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    if "spy" not in df.columns and "spy_value" in df.columns:
        df["spy"] = df["spy_value"]
    df["equity"] = pd.to_numeric(df["equity"], errors="coerce")
    if "portfolio_value" in df.columns:
        df["portfolio_value"] = pd.to_numeric(df["portfolio_value"], errors="coerce")
    else:
        df["portfolio_value"] = df["equity"]
    if "spy" in df.columns:
        df["spy"] = pd.to_numeric(df["spy"], errors="coerce")
    df["ts"] = pd.to_datetime(df["ts"], errors="coerce", utc=True)
    df = df.dropna(subset=["ts", "equity"]).sort_values("ts")
    if df.empty:
        return df
    df = df.set_index("ts")
    return df[~df.index.duplicated(keep="last")]


def _alpha_tracking(df: pd.DataFrame) -> tuple[float | None, float | None]:
    if df.empty or "spy" not in df.columns:
        return None, None
    window = df[["equity", "spy"]].dropna().tail(21)
    if len(window) < 21:
        return None, None
    bot_ret = window["equity"].iloc[-1] / window["equity"].iloc[0] - 1
    spy_ret = window["spy"].iloc[-1] / window["spy"].iloc[0] - 1
    diffs = window["equity"].pct_change().dropna() - window["spy"].pct_change().dropna()
    return float(bot_ret - spy_ret), float(diffs.std())


def _normalized_series(series: pd.Series) -> pd.Series:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return clean
    base = float(clean.iloc[0])
    if base == 0:
        return clean
    return (clean / base) * 100.0


def _trend_source_df(bot_name: str, df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    if bot_name.lower() == "llm":
        return df[df.index >= LLM_TREND_CUTOFF].copy()
    return df


def _actual_value_series(df: pd.DataFrame) -> pd.Series:
    if "portfolio_value" in df.columns and df["portfolio_value"].notna().sum() > 0:
        return pd.to_numeric(df["portfolio_value"], errors="coerce")
    return pd.to_numeric(df["equity"], errors="coerce")


def _format_snapshot_timestamp(raw_ts: str | None) -> str | None:
    if not raw_ts:
        return None
    ts = pd.to_datetime(raw_ts, errors="coerce", utc=True)
    if pd.isna(ts):
        return raw_ts
    return ts.strftime("%Y-%m-%d %H:%M UTC")


def _fmt_money(value) -> str:
    if value is None:
        return "--"
    return f"${float(value):,.2f}"


def _fmt_pct(value) -> str:
    if value is None:
        return "--"
    return f"{float(value) * 100:.2f}%"


def _positions_df(bot_name: str) -> pd.DataFrame:
    rows = fetch(f"/api/positions?bot={bot_name}").get("data", [])
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    for column in ["qty", "avg_entry", "avg_entry_price", "market_value", "unreal_pl", "unrealized_pl"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def _holdings_slices(selected_bots: list[tuple[str, str]]) -> pd.DataFrame:
    slices: list[dict[str, object]] = []
    multi_bot = len(selected_bots) > 1
    for bot_name, bot_label in selected_bots:
        positions_df = _positions_df(bot_name)
        if positions_df.empty or "market_value" not in positions_df.columns:
            continue
        positions_df = positions_df.dropna(subset=["market_value"])
        positions_df = positions_df[positions_df["market_value"] != 0]
        if positions_df.empty:
            continue
        positions_df["abs_value"] = positions_df["market_value"].abs()
        positions_df["side"] = positions_df["market_value"].apply(lambda value: "Short" if value < 0 else "Long")
        for row in positions_df.to_dict(orient="records"):
            symbol = str(row.get("symbol", "")).strip() or "Unknown"
            label = f"{bot_label}: {symbol}" if multi_bot else symbol
            slices.append(
                {
                    "label": label,
                    "bot_label": bot_label,
                    "symbol": symbol,
                    "value": float(row.get("abs_value", 0.0)),
                    "side": row.get("side", "Long"),
                }
            )
    if not slices:
        return pd.DataFrame()
    holdings_df = pd.DataFrame(slices).sort_values("value", ascending=False)
    return holdings_df[holdings_df["value"] > 0]


def _bot_payload(bot_name: str, label: str, snapshot_meta: dict) -> dict:
    if DATA_URL and isinstance(snapshot_meta, dict):
        payload = (snapshot_meta.get("bots") or {}).get(bot_name, {})
        if isinstance(payload, dict):
            return payload
    equity = fetch(f"/api/equity?bot={bot_name}&limit=1000").get("data", [])
    positions = fetch(f"/api/positions?bot={bot_name}").get("data", [])
    trades = fetch(f"/api/trades?bot={bot_name}").get("data", [])
    strategy_reports = fetch(f"/api/strategy?bot={bot_name}").get("data", [])
    decisions = fetch(f"/api/decisions?bot={bot_name}&limit=150").get("data", [])
    return {
        "label": label,
        "equity": equity,
        "positions": positions,
        "trades": trades,
        "strategy_reports": strategy_reports,
        "decisions": decisions,
    }


def _fmt_metric_pct(value) -> str:
    return "n/a" if value is None else f"{float(value):+.2%}"


def _fmt_metric_num(value) -> str:
    return "n/a" if value is None else f"{float(value):,.2f}"


def _nearest_trend_value(trend_df: pd.DataFrame, label: str, ts) -> float | None:
    if trend_df.empty or label not in trend_df.columns:
        return None
    ts = pd.to_datetime(ts, errors="coerce", utc=True)
    if pd.isna(ts):
        return None
    series = trend_df[label].dropna()
    if series.empty:
        return None
    prior = series[series.index <= ts]
    if not prior.empty:
        return float(prior.iloc[-1])
    return float(series.iloc[0])


def _trade_markers(selected_bots: list[tuple[str, str]], trend_df: pd.DataFrame, selected_window: pd.Timedelta, global_latest) -> pd.DataFrame:
    markers: list[dict[str, object]] = []
    if global_latest is None:
        return pd.DataFrame()
    cutoff = global_latest - selected_window
    for bot_name, label in selected_bots:
        rows = fetch(f"/api/trades?bot={bot_name}").get("data", [])
        for row in rows:
            ts = pd.to_datetime(row.get("ts"), errors="coerce", utc=True)
            if pd.isna(ts) or ts < cutoff or ts > global_latest:
                continue
            y_value = _nearest_trend_value(trend_df, label, ts)
            if y_value is None:
                continue
            markers.append(
                {
                    "bot": label,
                    "ts": ts,
                    "y": y_value,
                    "symbol": row.get("symbol", ""),
                    "side": str(row.get("side", "")).lower(),
                    "qty": row.get("qty"),
                    "price": row.get("price"),
                    "status": row.get("status", ""),
                }
            )
    return pd.DataFrame(markers)


def _latest_reports_by_type(reports: list[dict]) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    for report in reports or []:
        report_type = str(report.get("report_type") or "report")
        if report_type not in latest:
            latest[report_type] = report
    return latest


def _render_system_health(snapshot_meta: dict, bots_payload: dict[str, dict]) -> None:
    st.subheader("System Health")
    health = snapshot_meta.get("health", {}) if isinstance(snapshot_meta, dict) else {}
    generated_at = health.get("generated_at") or snapshot_meta.get("generated_at") if isinstance(snapshot_meta, dict) else None
    fresh = freshness_status(generated_at)
    health_bots = {row.get("bot_name"): row for row in health.get("bots", [])} if isinstance(health.get("bots"), list) else {}

    cols = st.columns(5)
    cols[0].metric("Snapshot", fresh.get("status", "unknown").title(), f"{fresh.get('age_minutes', 0) or 0:.0f} min old" if fresh.get("age_minutes") is not None else None)
    cols[1].metric("Data Source", "Snapshot" if DATA_URL else "Live API")
    cols[2].metric("Bots Seen", str(len(bots_payload)))
    total_positions = sum(len(payload.get("positions", []) or []) for payload in bots_payload.values())
    cols[3].metric("Open Positions", str(total_positions))
    total_unprotected = 0
    total_positions_for_protection = 0
    for payload in bots_payload.values():
        positions = payload.get("positions", []) or []
        total_positions_for_protection += len(positions)
        total_unprotected += sum(
            1
            for row in positions
            if str(row.get("protection_mode") or "").strip().lower() in {"", "none", "unknown"}
        )
    cols[4].metric("Unprotected", str(total_unprotected), f"{total_positions_for_protection} total")

    if health_bots:
        rows = []
        for bot_name, payload in bots_payload.items():
            row = health_bots.get(bot_name, {})
            rows.append(
                {
                    "Bot": payload.get("label", bot_name.upper()),
                    "Trading Auth": row.get("trading_auth", "unknown"),
                    "Market Data": row.get("market_data_auth", "unknown"),
                    "Trading Detail": row.get("trading_message", ""),
                    "Data Detail": row.get("market_data_message", ""),
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.caption("Auth status appears after the next cloud snapshot build. Local API mode reports freshness from live requests.")

    _render_cloud_run_controls()


def _render_cloud_run_controls() -> None:
    repo = _github_repo_from_data_url()
    actions_url = _github_actions_url(repo)

    with st.expander("Run Bot Now", expanded=False):
        st.caption(
            "This starts the existing GitHub Actions cloud workflow. "
            "The full run can rebalance Alpaca paper portfolios and update the dashboard snapshot."
        )
        cols = st.columns(3)
        cols[0].metric("Workflow", GITHUB_WORKFLOW_ID)
        cols[1].metric("Branch", GITHUB_WORKFLOW_REF)
        cols[2].metric("Repository", repo or "not set")

        confirmed = st.checkbox(
            "I understand this may submit paper-trading orders.",
            key="confirm_cloud_run",
        )
        disabled = not confirmed or not repo or not GITHUB_ACTIONS_TOKEN
        if st.button("Start Cloud Run", disabled=disabled, type="primary"):
            ok, message = _dispatch_github_workflow(repo)
            if ok:
                st.success(message)
                if actions_url:
                    st.link_button("Open GitHub Actions", actions_url)
            else:
                st.error(message)

        if not repo:
            st.warning("Set GITHUB_REPOSITORY in Streamlit secrets to enable dashboard-triggered runs.")
        elif not GITHUB_ACTIONS_TOKEN:
            st.info("Add GITHUB_ACTIONS_TOKEN in Streamlit secrets to enable the button.")
            if actions_url:
                st.link_button("Run Manually In GitHub", actions_url)
        elif actions_url:
            st.caption("After starting a run, GitHub usually takes a few minutes to rebuild and commit the new snapshot.")
            st.link_button("View Workflow Runs", actions_url)


def _render_comparison_summary(bots_payload: dict[str, dict], selected_window_key: str) -> None:
    st.subheader("Bot Comparison")
    rows = comparison_table(bots_payload, selected_window_key)
    if rows:
        table = pd.DataFrame(
            [
                {
                    "Bot": row["label"],
                    "Return": _fmt_metric_pct(row.get("window_return")),
                    "Vs SPY": _fmt_metric_pct(row.get("window_alpha")),
                    "Max DD": _fmt_metric_pct(row.get("max_drawdown")),
                    "Win Rate": _fmt_metric_pct(row.get("win_rate")),
                    "Avg Trade Alpha": _fmt_metric_pct(row.get("avg_trade_alpha")),
                    "Gross Exposure": _fmt_metric_pct(row.get("gross_exposure_pct")),
                    "Protection": _fmt_metric_pct(row.get("protection_rate")),
                }
                for row in rows
            ]
        )
        st.dataframe(table, use_container_width=True, hide_index=True)
    agreement = agreement_summary(bots_payload)
    if agreement.get("overlap"):
        st.caption(
            f"ML/LLM overlap: {agreement['overlap']} names • "
            f"agreement rate {_fmt_metric_pct(agreement.get('agreement_rate'))}. "
            f"Agreements: {', '.join(agreement.get('agreements', [])[:6]) or 'none'}; "
            f"disagreements: {', '.join(agreement.get('disagreements', [])[:6]) or 'none'}."
        )
    else:
        st.caption("Not enough overlapping ML/LLM decisions yet to score agreement quality.")


def _render_risk_panel(bots_payload: dict[str, dict], selected_window_key: str) -> None:
    st.subheader("Risk Cockpit")
    window = WINDOW_OPTIONS[selected_window_key]
    rows = []
    for bot_name, payload in bots_payload.items():
        metrics = bot_performance_metrics(payload, window)
        latest_report = next(iter(payload.get("strategy_reports", []) or []), {})
        report_metrics = latest_report.get("metrics", {}) if isinstance(latest_report.get("metrics"), dict) else {}
        rows.append(
            {
                "Bot": payload.get("label", bot_name.upper()),
                "Gross Exposure": _fmt_metric_pct(metrics.get("gross_exposure_pct")),
                "Long $": _fmt_money(metrics.get("long_exposure")),
                "Short $": _fmt_money(metrics.get("short_exposure")),
                "Largest Pos": _fmt_metric_pct(metrics.get("largest_position_pct")),
                "Protected": _fmt_metric_pct(metrics.get("protection_rate")),
                "Max Sector": _fmt_metric_pct(report_metrics.get("max_sector_weight")),
                "Beta": _fmt_metric_num(report_metrics.get("beta")),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with st.expander("Current position protection details", expanded=False):
        protection_rows = []
        for bot_name, payload in bots_payload.items():
            for row in payload.get("positions", []) or []:
                protection_rows.append(
                    {
                        "Bot": payload.get("label", bot_name.upper()),
                        "Symbol": row.get("symbol"),
                        "Qty": row.get("qty"),
                        "Market Value": row.get("market_value"),
                        "Protection": row.get("protection_mode") or "Unknown",
                        "Summary": row.get("protection_summary") or "",
                    }
                )
        if protection_rows:
            st.dataframe(pd.DataFrame(protection_rows), use_container_width=True, hide_index=True)
        else:
            st.caption("No positions are available.")


def _render_report_cockpit(bots_payload: dict[str, dict]) -> None:
    st.subheader("Latest Reports")
    report_tabs = st.tabs([payload.get("label", name.upper()) for name, payload in bots_payload.items()])
    for tab, (bot_name, payload) in zip(report_tabs, bots_payload.items()):
        with tab:
            reports = payload.get("strategy_reports", []) or []
            if not reports:
                st.caption("No reports yet.")
                continue
            latest_by_type = _latest_reports_by_type(reports)
            report_types = ["strategy", "watchlist", "learning", "analyst_daily", "trader_daily", "coach", "llm_daily", "options_scaffold"]
            for report_type in report_types:
                report = latest_by_type.get(report_type)
                if not report:
                    continue
                with st.expander(f"{report.get('headline', report_type)} • {report.get('ts', '')}", expanded=report_type in {"strategy", "analyst_daily", "trader_daily", "coach"}):
                    st.write(report.get("summary", ""))
                    takeaways = extract_key_takeaways(report.get("body"), limit=5)
                    if takeaways:
                        st.markdown("**Key takeaways**")
                        for item in takeaways:
                            st.markdown(f"- {item}")
                    st.markdown(report.get("body", ""))


def _render_decision_explorer(bots_payload: dict[str, dict]) -> None:
    st.subheader("Why Did It Trade?")
    rows = []
    for bot_name, payload in bots_payload.items():
        for row in payload.get("decisions", []) or []:
            components = row.get("components") if isinstance(row.get("components"), dict) else {}
            component_summary = ", ".join(
                f"{key.replace('_adjustment', '')}={float(value):+.4f}"
                for key, value in sorted(components.items(), key=lambda item: abs(float(item[1])), reverse=True)
                if abs(float(value)) >= 0.0001
            )
            rows.append(
                {
                    "Bot": payload.get("label", bot_name.upper()),
                    "Time": row.get("ts"),
                    "Symbol": row.get("symbol"),
                    "Side": row.get("side"),
                    "Base": row.get("base_score"),
                    "Final": row.get("final_score"),
                    "Signed Return": row.get("signed_return"),
                    "Beat SPY": row.get("beat_spy"),
                    "Outcome": row.get("outcome_label") or "pending",
                    "Rationale": row.get("rationale") or "",
                    "Components": component_summary,
                }
            )
    if not rows:
        st.caption("No decision logs yet.")
        return

    df = pd.DataFrame(rows)
    col1, col2, col3 = st.columns(3)
    bot_filter = col1.multiselect("Bot", sorted(df["Bot"].dropna().unique()), default=sorted(df["Bot"].dropna().unique()))
    symbol_options = sorted(df["Symbol"].dropna().unique())
    symbol_filter = col2.multiselect("Symbol", symbol_options, default=symbol_options[: min(8, len(symbol_options))])
    outcome_filter = col3.multiselect("Outcome", sorted(df["Outcome"].dropna().unique()), default=sorted(df["Outcome"].dropna().unique()))
    filtered = df[df["Bot"].isin(bot_filter) & df["Symbol"].isin(symbol_filter) & df["Outcome"].isin(outcome_filter)].copy()
    for column in ["Base", "Final", "Signed Return", "Beat SPY"]:
        filtered[column] = pd.to_numeric(filtered[column], errors="coerce")
    st.dataframe(filtered, use_container_width=True, hide_index=True)


bot_names = _load_bot_names()
comparison_frames: dict[str, pd.DataFrame] = {name: _equity_df(name) for name, _ in bot_names}
snapshot_meta = _load_snapshot() if DATA_URL else {}
snapshot_updated = _format_snapshot_timestamp(snapshot_meta.get("generated_at") if isinstance(snapshot_meta, dict) else None)
bots_payload = {name: _bot_payload(name, label, snapshot_meta) for name, label in bot_names}

_render_system_health(snapshot_meta, bots_payload)

st.subheader("Trend Graph")
control_col1, control_col2, control_col3 = st.columns([1, 1.4, 1.6])
with control_col1:
    selected_window_key = st.selectbox("Date range", list(WINDOW_OPTIONS.keys()), index=4)
with control_col2:
    graph_mode = st.radio(
        "Graph scale",
        ["Indexed performance", "Actual holding value"],
        horizontal=True,
    )
display_labels = [label for _, label in bot_names]
display_options = ["Both models"] + display_labels
with control_col3:
    selected_display = st.radio("Show", display_options, horizontal=True)
selected_window = WINDOW_OPTIONS[selected_window_key]
if snapshot_updated:
    st.caption(f"Snapshot updated: {snapshot_updated}")
elif DATA_URL:
    st.caption("Snapshot source is configured, but no snapshot timestamp was found.")
else:
    st.caption("Using live API data.")
_render_comparison_summary(bots_payload, selected_window_key)
trend_series: list[pd.Series] = []
spy_series: list[pd.Series] = []
trend_frames = {name: _trend_source_df(name, df) for name, df in comparison_frames.items()}
global_latest = max((df.index.max() for df in trend_frames.values() if not df.empty), default=None)
excluded_labels: list[str] = []
selected_labels = set(display_labels if selected_display == "Both models" else [selected_display])
selected_bots = [(name, label) for name, label in bot_names if label in selected_labels]
for name, label in bot_names:
    df = trend_frames.get(name, pd.DataFrame())
    if df.empty:
        continue
    if label not in selected_labels:
        continue
    filtered = filter_frame_to_window(df, selected_window, anchor_ts=global_latest)
    if len(filtered) < 2:
        excluded_labels.append(label)
        continue
    value_series = _actual_value_series(filtered)
    equity_trend = (
        _normalized_series(value_series)
        if graph_mode == "Indexed performance"
        else value_series.dropna()
    ).rename(label)
    if equity_trend.dropna().shape[0] >= 2:
        trend_series.append(equity_trend)
    if "spy" in filtered.columns and filtered["spy"].notna().sum() > 1:
        spy_series.append(filtered["spy"].dropna())

if spy_series:
    spy_values = pd.concat(spy_series).sort_index()
    spy_values = spy_values[~spy_values.index.duplicated(keep="last")]
    if graph_mode == "Indexed performance":
        spy_trend = _normalized_series(spy_values).rename("SPY")
        if spy_trend.dropna().shape[0] >= 2:
            trend_series.append(spy_trend)

trend_df = pd.concat(trend_series, axis=1).sort_index() if trend_series else pd.DataFrame()
trade_marker_df = _trade_markers(selected_bots, trend_df, selected_window, global_latest)

trend_col, holdings_col = st.columns([2.2, 1])

with trend_col:
    if graph_mode == "Indexed performance":
        st.caption("Indexed to 100 at the first visible point in the selected window. LLM trend data before April 23, 2026 is hidden.")
    else:
        st.caption("Actual account holding value in dollars. LLM trend data before April 23, 2026 is hidden; SPY is omitted because it is a price, not an account value.")
    if not trend_df.empty:
        try:
            import plotly.graph_objects as go

            fig = go.Figure()
            for column in trend_df.columns:
                series = trend_df[column].dropna()
                if len(series) < 2:
                    continue
                trace_kwargs = {}
                if column == "SPY":
                    trace_kwargs["line"] = {"dash": "dash"}
                if graph_mode == "Actual holding value":
                    trace_kwargs["hovertemplate"] = "%{fullData.name}<br>%{x}<br>$%{y:,.2f}<extra></extra>"
                fig.add_trace(
                    go.Scatter(
                        x=series.index,
                        y=series,
                        mode="lines+markers",
                        name=column,
                        **trace_kwargs,
                    )
                )
            if not trade_marker_df.empty:
                for side, marker_symbol, color in [
                    ("buy", "triangle-up", "#16a34a"),
                    ("sell", "triangle-down", "#dc2626"),
                ]:
                    side_df = trade_marker_df[trade_marker_df["side"] == side]
                    if side_df.empty:
                        continue
                    fig.add_trace(
                        go.Scatter(
                            x=side_df["ts"],
                            y=side_df["y"],
                            mode="markers",
                            name=f"{side.title()} trades",
                            marker={"symbol": marker_symbol, "size": 11, "color": color, "line": {"width": 1, "color": "white"}},
                            customdata=side_df[["bot", "symbol", "qty", "price", "status"]].values,
                            hovertemplate=(
                                "%{customdata[0]} %{customdata[1]}<br>"
                                f"{side.title()} qty=%{{customdata[2]}} price=%{{customdata[3]}}<br>"
                                "Status: %{customdata[4]}<extra></extra>"
                            ),
                        )
                    )
            fig.update_layout(
                height=360,
                margin={"l": 10, "r": 10, "t": 10, "b": 10},
                yaxis_title="Indexed Performance",
                hovermode="x unified",
            )
            if graph_mode == "Actual holding value":
                fig.update_layout(yaxis_title="Actual Holding Value")
                fig.update_yaxes(tickprefix="$", separatethousands=True)
            y_values = pd.concat([trend_df[column].dropna() for column in trend_df.columns])
            if not y_values.empty:
                y_min = float(y_values.min())
                y_max = float(y_values.max())
                y_pad = max((y_max - y_min) * 0.08, 0.4)
                fig.update_yaxes(range=[y_min - y_pad, y_max + y_pad])
            if global_latest is not None:
                fig.update_xaxes(range=[global_latest - selected_window, global_latest])
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.line_chart(trend_df)
    else:
        st.caption("No bot equity history is available for the selected date range.")

with holdings_col:
    st.subheader("Current Holdings")
    holdings_df = _holdings_slices(selected_bots)
    if not holdings_df.empty:
        try:
            import plotly.graph_objects as go

            colors = ["#34d399" if side == "Long" else "#f87171" for side in holdings_df["side"]]
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=holdings_df["label"],
                        values=holdings_df["value"],
                        hole=0.56,
                        marker={"colors": colors},
                        hovertemplate="%{label}<br>$%{value:,.2f}<br>%{percent}<extra></extra>",
                    )
                ]
            )
            fig.update_layout(height=360, margin={"l": 10, "r": 10, "t": 10, "b": 10})
            st.plotly_chart(fig, use_container_width=True)
            long_count = int((holdings_df["side"] == "Long").sum())
            short_count = int((holdings_df["side"] == "Short").sum())
            st.caption(f"Long slices: {long_count} • Short slices: {short_count}")
        except Exception:
            st.dataframe(holdings_df[["label", "value", "side"]], use_container_width=True)
    else:
        st.caption("No current holdings are available for the selected model view.")

if excluded_labels:
    st.caption(f"No recent data in the selected date range for: {', '.join(excluded_labels)}")

_render_risk_panel(bots_payload, selected_window_key)
_render_report_cockpit(bots_payload)
_render_decision_explorer(bots_payload)

tabs = st.tabs([label for _, label in bot_names])

for tab, (bot_name, bot_label_text) in zip(tabs, bot_names):
    with tab:
        summary = fetch(f"/api/summary?bot={bot_name}")
        if summary.get("status") != "ok":
            st.warning(summary.get("message", f"No {bot_label_text} data yet."))
            continue

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Equity", _fmt_money(summary.get("equity")))
        col2.metric("Cash", _fmt_money(summary.get("cash")))
        col3.metric("Portfolio", _fmt_money(summary.get("portfolio")))
        col4.metric("SPY", _fmt_money(summary.get("spy")) if summary.get("spy") is not None else "--")

        df = comparison_frames.get(bot_name, pd.DataFrame())
        alpha, tracking_error = _alpha_tracking(df)
        col5.metric("Alpha 20D", _fmt_pct(alpha))
        col6.metric("Tracking Error", _fmt_pct(tracking_error))

        positions = fetch(f"/api/positions?bot={bot_name}").get("data", [])
        trades = fetch(f"/api/trades?bot={bot_name}").get("data", [])
        advisor = fetch(f"/api/advisor?bot={bot_name}").get("data", [])
        strategy_reports = fetch(f"/api/strategy?bot={bot_name}").get("data", [])
        decisions = fetch(f"/api/decisions?bot={bot_name}&limit=50").get("data", [])

        st.subheader("Positions")
        if positions:
            if any(row.get("protection_mode") for row in positions):
                st.caption("Broker-side protection is shown when Alpaca has exits resting for this bot's account.")
            st.dataframe(positions, use_container_width=True)
        else:
            st.caption("No positions logged yet.")

        st.subheader("Recent Trades")
        if trades:
            st.dataframe(trades, use_container_width=True)
        else:
            st.caption("No trades logged yet.")

        st.subheader("Reports")
        if advisor:
            st.markdown("**Advisor Reports**")
            for report in advisor[:3]:
                st.markdown(f"**{report.get('headline','Advisor Report')}** — {report.get('ts','')}")
                st.write(report.get("summary", ""))
                st.divider()

        if strategy_reports:
            for report in strategy_reports[:8]:
                st.markdown(f"**[{report.get('report_type','report')}] {report.get('headline','Report')}** — {report.get('ts','')}")
                st.write(report.get("summary", ""))
                with st.expander("Show report body"):
                    st.markdown(report.get("body", ""))
                st.divider()
        else:
            st.caption("No strategy reports yet.")

        st.subheader("Recent Decisions")
        if decisions:
            decision_df = pd.DataFrame(decisions)
            for column in ["base_score", "final_score", "signed_return", "beat_spy"]:
                if column in decision_df.columns:
                    decision_df[column] = pd.to_numeric(decision_df[column], errors="coerce")
            if "components" in decision_df.columns:
                decision_df["component_summary"] = decision_df["components"].apply(
                    lambda comp: ", ".join(
                        f"{k.replace('_adjustment', '')}={float(v):+.4f}"
                        for k, v in sorted((comp or {}).items(), key=lambda item: abs(float(item[1])), reverse=True)
                        if abs(float(v)) >= 0.0001
                    )[:220]
                    if isinstance(comp, dict)
                    else ""
                )
            display_cols = [
                col for col in [
                    "ts",
                    "symbol",
                    "side",
                    "base_score",
                    "final_score",
                    "signed_return",
                    "beat_spy",
                    "outcome_label",
                    "rationale",
                    "component_summary",
                ] if col in decision_df.columns
            ]
            st.dataframe(decision_df[display_cols], use_container_width=True)
        else:
            st.caption("No decision logs yet.")
