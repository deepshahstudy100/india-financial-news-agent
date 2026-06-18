import logging
from agent.scraper import fetch_all_news
from agent.sentiment import rate_batch
from agent.database import insert_articles
from agent.trend_analyzer import compute_all_trends
from agent.index_tracker import fetch_all_indices
from agent.reporter import generate_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run_agent():
    logger.info("🚀 Financial News Agent starting...")

    articles  = fetch_all_news()
    logger.info(f"📰 Fetched {len(articles)} articles")

    rated     = rate_batch(articles)
    new_count = insert_articles(rated)
    logger.info(f"💾 {new_count} new articles stored in Supabase")

    trends  = compute_all_trends()
    indices = fetch_all_indices()
    generate_report(trends, indices)

    logger.info("✅ Run complete")
    return trends, indices


if __name__ == "__main__":
    run_agent()
