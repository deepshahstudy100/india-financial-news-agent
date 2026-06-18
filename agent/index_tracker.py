import yfinance as yf
from agent.database import save_index_snapshot
from config import INDICES
import logging

logger = logging.getLogger(__name__)


def fetch_index(name: str, ticker: str) -> dict:
    try:
        tkr  = yf.Ticker(ticker)
        hist = tkr.history(period="1d", interval="1m")
        if hist.empty:
            return {}
        latest     = hist.iloc[-1]
        prev_close = tkr.fast_info.get("previousClose") or float(latest["Close"])
        change_pct = (float(latest["Close"]) - prev_close) / prev_close * 100 if prev_close else 0
        snapshot = {
            "price":      round(float(latest["Close"]), 2),
            "change_pct": round(change_pct, 2),
            "open":       round(float(hist.iloc[0]["Open"]), 2),
            "high":       round(float(hist["High"].max()), 2),
            "low":        round(float(hist["Low"].min()), 2),
            "volume":     int(hist["Volume"].sum()),
        }
        save_index_snapshot(name, snapshot)
        logger.info(f"📈 {name}: ₹{snapshot['price']:,.2f} ({snapshot['change_pct']:+.2f}%)")
        return snapshot
    except Exception as e:
        logger.error(f"Index fetch failed [{name}]: {e}")
        return {}


def fetch_all_indices() -> dict:
    return {name: fetch_index(name, ticker) for name, ticker in INDICES.items()}
