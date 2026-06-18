import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import hashlib
import logging
from config import NEWS_SOURCES

logger = logging.getLogger(__name__)


def fetch_all_news() -> list[dict]:
    all_articles = []
    for source in NEWS_SOURCES:
        try:
            articles = _fetch_rss(source["name"], source["url"])
            all_articles.extend(articles)
            logger.info(f"✅ {source['name']}: {len(articles)} articles")
        except Exception as e:
            logger.error(f"❌ {source['name']} failed: {e}")
    return all_articles


def _fetch_rss(source_name: str, url: str) -> list[dict]:
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:20]:
        published = datetime.now(timezone.utc)
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        raw_summary = getattr(entry, "summary", "") or ""
        summary     = BeautifulSoup(raw_summary, "html.parser").get_text()[:500]
        title       = getattr(entry, "title", "No Title")
        link        = getattr(entry, "link", "")
        articles.append({
            "id":           hashlib.md5(link.encode()).hexdigest(),
            "title":        title,
            "summary":      summary,
            "url":          link,
            "source":       source_name,
            "published_at": published.isoformat(),
            "fetched_at":   datetime.now(timezone.utc).isoformat(),
        })
    return articles
