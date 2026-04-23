import os
from urllib.parse import parse_qs, urlsplit

import pandas as pd
import requests
import streamlit as st


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
WINDOW_OPTIONS = {
    "24h": pd.Timedelta(hours=24),
    "7d": pd.Timedelta(days=7),
    "14d": pd.Timedelta(days=14),
    "28d": pd.Timedelta(days=28),
    "90d": pd.Timedelta(days=90),
    "180d": pd.Timedelta(days=180),
    "360d": pd.Timedelta(days=360),
}

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
    if "spy" in df.columns:
        df["spy"] = pd.to_numeric(df["spy"], errors="coerce")
    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
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


def _filter_frame_to_window(df: pd.DataFrame, window: pd.Timedelta, anchor_ts=None) -> pd.DataFrame:
    if df.empty:
        return df
    latest = anchor_ts if anchor_ts is not None else df.index.max()
    cutoff = latest - window
    filtered = df[df.index >= cutoff]
    return filtered.sort_index()


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


bot_names = _load_bot_names()
comparison_frames: dict[str, pd.DataFrame] = {name: _equity_df(name) for name, _ in bot_names}
snapshot_meta = _load_snapshot() if DATA_URL else {}
snapshot_updated = _format_snapshot_timestamp(snapshot_meta.get("generated_at") if isinstance(snapshot_meta, dict) else None)

st.subheader("Trend Graph")
control_col1, control_col2 = st.columns([1, 2])
with control_col1:
    selected_window_key = st.selectbox("Date range", list(WINDOW_OPTIONS.keys()), index=4)
display_labels = [label for _, label in bot_names]
display_options = ["Both models"] + display_labels
with control_col2:
    selected_display = st.radio("Show", display_options, horizontal=True)
selected_window = WINDOW_OPTIONS[selected_window_key]
if snapshot_updated:
    st.caption(f"Snapshot updated: {snapshot_updated}")
elif DATA_URL:
    st.caption("Snapshot source is configured, but no snapshot timestamp was found.")
else:
    st.caption("Using live API data.")
trend_df = pd.DataFrame()
global_latest = max((df.index.max() for df in comparison_frames.values() if not df.empty), default=None)
excluded_labels: list[str] = []
selected_labels = set(display_labels if selected_display == "Both models" else [selected_display])
for name, label in bot_names:
    df = comparison_frames.get(name, pd.DataFrame())
    if df.empty:
        continue
    if label not in selected_labels:
        continue
    filtered = _filter_frame_to_window(df, selected_window, anchor_ts=global_latest)
    if len(filtered) < 2:
        excluded_labels.append(label)
        continue
    trend_df[label] = filtered["equity"]

trend_df = trend_df.sort_index()

if not trend_df.empty:
    try:
        import plotly.graph_objects as go

        fig = go.Figure()
        for column in trend_df.columns:
            fig.add_trace(
                go.Scatter(
                    x=trend_df.index,
                    y=trend_df[column],
                    mode="lines",
                    name=column,
                )
            )
        fig.update_layout(
            height=360,
            margin={"l": 10, "r": 10, "t": 10, "b": 10},
            yaxis_title="Equity ($)",
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.line_chart(trend_df)
else:
    st.caption("No bot equity history is available for the selected date range.")

if excluded_labels:
    st.caption(f"No recent data in the selected date range for: {', '.join(excluded_labels)}")

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
