from agent.database import get_recent_articles, save_trend
from config import TREND_WINDOW_HOURS, NEGATIVE_TREND_THRESHOLD, POSITIVE_TREND_THRESHOLD, SECTORS
import logging

logger = logging.getLogger(__name__)


def _classify(avg: float) -> str:
    if avg <= NEGATIVE_TREND_THRESHOLD:
        return "🔴 NEGATIVE"
    if avg >= POSITIVE_TREND_THRESHOLD:
        return "🟢 POSITIVE"
    return "🟡 NEUTRAL"


def compute_trend(sector: str = "overall", hours: int = TREND_WINDOW_HOURS) -> dict:
    articles = get_recent_articles(hours=hours, sector=(None if sector == "overall" else sector))
    if not articles:
        return {
            "sector": sector, "trend_label": "⚪ NO DATA",
            "avg_score": 0, "article_count": 0,
            "positive_pct": 0, "negative_pct": 0, "neutral_pct": 0,
            "window_hours": hours, "top_positive": [], "top_negative": [],
        }
    scores   = [a["score"] for a in articles]
    total    = len(scores)
    avg      = sum(scores) / total
    positive = sum(1 for s in scores if s > 0)
    negative = sum(1 for s in scores if s < 0)
    neutral  = total - positive - negative
    trend = {
        "sector":        sector,
        "avg_score":     round(avg, 2),
        "trend_label":   _classify(avg),
        "article_count": total,
        "positive_pct":  round(positive / total * 100, 1),
        "negative_pct":  round(negative / total * 100, 1),
        "neutral_pct":   round(neutral  / total * 100, 1),
        "window_hours":  hours,
        "top_negative":  sorted(articles, key=lambda x: x["score"])[:3],
        "top_positive":  sorted(articles, key=lambda x: x["score"], reverse=True)[:3],
    }
    save_trend(trend)
    logger.info(f"📊 [{sector}] {trend['trend_label']}  avg={avg:.2f}  n={total}")
    return trend


def compute_all_trends() -> dict:
    results = {"overall": compute_trend("overall")}
    for sector in SECTORS:
        results[sector] = compute_trend(sector)
    return results
