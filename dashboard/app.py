"""Streamlit dashboard - reads live from Supabase."""
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
from datetime import datetime, timezone, timedelta

st.set_page_config(
    page_title="📊 India Financial Sentiment",
    page_icon="📊",
    layout="wide",
)
st.title("📊 India Financial News Sentiment Tracker")
st.caption("AI-powered sentiment tracking across SENSEX, Nifty & Indian sectors · Powered by Supabase")


@st.cache_resource
def get_db():
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    return create_client(url, key)


db = get_db()


@st.cache_data(ttl=180)
def load_articles(hours: int, sector: str) -> pd.DataFrame:
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    q = (
        db.table("articles")
        .select("*")
        .eq("is_financial", True)
        .gte("published_at", since)
        .order("published_at", desc=True)
        .limit(500)
    )
    if sector != "all":
        q = q.eq("sector", sector)
    return pd.DataFrame(q.execute().data or [])


@st.cache_data(ttl=180)
def load_trend_history(sector: str = "overall") -> pd.DataFrame:
    data = (
        db.table("trends")
        .select("*")
        .eq("sector", sector)
        .order("timestamp", desc=True)
        .limit(300)
        .execute()
        .data or []
    )
    return pd.DataFrame(reversed(data))


@st.cache_data(ttl=180)
def load_index_history(index_name: str) -> pd.DataFrame:
    data = (
        db.table("index_snapshots")
        .select("*")
        .eq("index_name", index_name)
        .order("timestamp", desc=True)
        .limit(300)
        .execute()
        .data or []
    )
    return pd.DataFrame(reversed(data))


@st.cache_data(ttl=180)
def load_latest_indices() -> pd.DataFrame:
    data = (
        db.table("index_snapshots")
        .select("*")
        .order("timestamp", desc=True)
        .limit(100)
        .execute()
        .data or []
    )
    df = pd.DataFrame(data)
    return df.drop_duplicates(subset="index_name", keep="first") if not df.empty else df


# Sidebar
st.sidebar.header("⚙️ Filters")
hours      = st.sidebar.slider("Lookback window (hours)", 6, 168, 24, step=6)
min_score  = st.sidebar.slider("Min |Score| to display", 0, 10, 0)
sel_sector = st.sidebar.selectbox(
    "Sector filter",
    ["all", "banking", "IT", "auto", "pharma", "FMCG", "metal", "realty", "energy", "infra"],
)
st.sidebar.markdown("---")
st.sidebar.markdown("🔄 Data refreshes every **3 min**")

df = load_articles(hours, sel_sector)

if df.empty:
    st.warning("⚠️ No data yet - run `python main.py` first, then come back.")
    st.stop()

# KPI Row
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📰 Articles",  len(df))
c2.metric("📈 Avg Score", f"{df['score'].mean():+.2f}")
c3.metric("🟢 Positive",  int((df["score"] > 0).sum()))
c4.metric("🔴 Negative",  int((df["score"] < 0).sum()))
c5.metric("⚪ Neutral",   int((df["score"] == 0).sum()))

st.divider()

# Distribution + Sector
ca, cb = st.columns(2)
with ca:
    st.subheader("Score Distribution")
    fig = px.histogram(df, x="score", nbins=21, range_x=[-10, 10],
                       color_discrete_sequence=["#636EFA"])
    fig.add_vline(x=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig, use_container_width=True)

with cb:
    st.subheader("Avg Sentiment by Sector")
    sec_avg = df.groupby("sector")["score"].mean().sort_values()
    fig2 = px.bar(x=sec_avg.values, y=sec_avg.index, orientation="h",
                  color=sec_avg.values, color_continuous_scale="RdYlGn",
                  range_color=[-10, 10])
    st.plotly_chart(fig2, use_container_width=True)

# Trend vs SENSEX
st.subheader("📉 Sentiment Trend vs SENSEX")
trend_df  = load_trend_history("overall")
sensex_df = load_index_history("SENSEX")

if not trend_df.empty:
    fig3 = go.Figure()
    fig3.add_hrect(y0=-3, y1=3, fillcolor="yellow", opacity=0.06, line_width=0)
    fig3.add_trace(go.Scatter(
        x=trend_df["timestamp"], y=trend_df["avg_score"],
        name="Sentiment Score", line=dict(color="royalblue", width=2), yaxis="y1"
    ))
    if not sensex_df.empty:
        fig3.add_trace(go.Scatter(
            x=sensex_df["timestamp"], y=sensex_df["change_pct"],
            name="SENSEX %Δ", line=dict(color="orange", width=2, dash="dot"), yaxis="y2"
        ))
    fig3.update_layout(
        yaxis  = dict(title="Sentiment Score", range=[-10, 10]),
        yaxis2 = dict(title="SENSEX Change %", overlaying="y", side="right"),
        legend = dict(x=0, y=1.15, orientation="h"),
        hovermode="x unified",
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Trend history will appear after the first full agent run.")

# Index snapshot
idx_df = load_latest_indices()
if not idx_df.empty:
    st.subheader("📈 Latest Index Snapshot")
    show = idx_df[["index_name", "price", "change_pct", "high", "low", "volume"]].copy()
    def color_chg(val):
        return f"color: {'green' if val > 0 else 'red' if val < 0 else 'gray'}; font-weight:bold"
    st.dataframe(show.style.applymap(color_chg, subset=["change_pct"]), use_container_width=True)

# Articles table
st.subheader("📰 Recent Articles")
disp = df[["published_at", "source", "title", "score", "sentiment", "sector", "reasoning"]].copy()
disp = disp[df["score"].abs() >= min_score].head(300)

def bg_score(val):
    if val >= 4:  return "background-color:#d4edda"
    if val <= -4: return "background-color:#f8d7da"
    return "background-color:#fff3cd"

st.dataframe(disp.style.applymap(bg_score, subset=["score"]),
             use_container_width=True, height=450)
