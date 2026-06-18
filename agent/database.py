"""Supabase database layer."""
import logging
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)
_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise EnvironmentError("SUPABASE_URL and SUPABASE_KEY must be set.")
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Supabase client initialised")
    return _client


def insert_articles(articles: list[dict]) -> int:
    if not articles:
        return 0
    db = get_client()
    new_count = 0
    for a in articles:
        row = {
            "id":           a["id"],
            "title":        a["title"],
            "summary":      a.get("summary", ""),
            "url":          a.get("url", ""),
            "source":       a.get("source", ""),
            "published_at": a.get("published_at"),
            "fetched_at":   a.get("fetched_at"),
            "score":        int(a.get("score", 0)),
            "sentiment":    a.get("sentiment", "neutral"),
            "sector":       a.get("sector", "general"),
            "keywords":     ",".join(a.get("keywords", [])),
            "reasoning":    a.get("reasoning", ""),
            "is_financial": bool(a.get("is_financial", True)),
        }
        try:
            resp = db.table("articles").upsert(row, on_conflict="id", ignore_duplicates=True).execute()
            if resp.data:
                new_count += len(resp.data)
        except Exception as e:
            logger.error(f"Insert error: {e}")
    logger.info(f"✅ {new_count} new articles upserted")
    return new_count


def get_recent_articles(hours: int = 24, sector: str | None = None) -> list[dict]:
    db    = get_client()
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    q = (
        db.table("articles")
        .select("*")
        .eq("is_financial", True)
        .gte("published_at", since)
        .order("published_at", desc=True)
        .limit(500)
    )
    if sector:
        q = q.eq("sector", sector)
    return q.execute().data or []


def save_trend(trend: dict):
    db = get_client()
    db.table("trends").insert({
        "timestamp":     datetime.now(timezone.utc).isoformat(),
        "window_hours":  trend["window_hours"],
        "avg_score":     trend["avg_score"],
        "trend_label":   trend["trend_label"],
        "article_count": trend["article_count"],
        "sector":        trend["sector"],
        "positive_pct":  trend["positive_pct"],
        "negative_pct":  trend["negative_pct"],
        "neutral_pct":   trend["neutral_pct"],
    }).execute()


def save_index_snapshot(index_name: str, data: dict):
    db = get_client()
    db.table("index_snapshots").insert({
        "timestamp":  datetime.now(timezone.utc).isoformat(),
        "index_name": index_name,
        "price":      data.get("price"),
        "change_pct": data.get("change_pct"),
        "open":       data.get("open"),
        "high":       data.get("high"),
        "low":        data.get("low"),
        "volume":     data.get("volume"),
    }).execute()


def get_trend_history(sector: str = "overall", limit: int = 200) -> list[dict]:
    db   = get_client()
    resp = (
        db.table("trends")
        .select("*")
        .eq("sector", sector)
        .order("timestamp", desc=True)
        .limit(limit)
        .execute()
    )
    return list(reversed(resp.data or []))


def get_index_history(index_name: str, limit: int = 200) -> list[dict]:
    db   = get_client()
    resp = (
        db.table("index_snapshots")
        .select("*")
        .eq("index_name", index_name)
        .order("timestamp", desc=True)
        .limit(limit)
        .execute()
    )
    return list(reversed(resp.data or []))


def get_latest_index_snapshot() -> list[dict]:
    db   = get_client()
    rows = (
        db.table("index_snapshots")
        .select("*")
        .order("timestamp", desc=True)
        .limit(100)
        .execute()
        .data or []
    )
    seen, latest = set(), []
    for r in rows:
        if r["index_name"] not in seen:
            seen.add(r["index_name"])
            latest.append(r)
    return latest
