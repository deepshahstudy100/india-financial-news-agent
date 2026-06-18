import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def generate_report(trends: dict, indices: dict):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sep = "=" * 62
    print(f"\n{sep}")
    print(f"  📊 FINANCIAL NEWS SENTIMENT REPORT — {now}")
    print(sep)

    ov = trends.get("overall", {})
    print(f"\n🌐 OVERALL MARKET SENTIMENT")
    print(f"   Trend      : {ov.get('trend_label', 'N/A')}")
    print(f"   Avg Score  : {ov.get('avg_score', 0):+.2f} / 10")
    print(f"   Articles   : {ov.get('article_count', 0)}  (last {ov.get('window_hours', 24)}h)")
    print(f"   🟢 Positive : {ov.get('positive_pct', 0):.1f}%")
    print(f"   🔴 Negative : {ov.get('negative_pct', 0):.1f}%")
    print(f"   🟡 Neutral  : {ov.get('neutral_pct', 0):.1f}%")

    if indices:
        print(f"\n📈 INDEX SNAPSHOT")
        for name, data in indices.items():
            if data:
                sign = "+" if data.get("change_pct", 0) >= 0 else ""
                print(f"   {name:<15}: ₹{data.get('price', 0):>10,.2f}  "
                      f"({sign}{data.get('change_pct', 0):.2f}%)")

    print(f"\n🏭 SECTOR TRENDS")
    for sector in [k for k in trends if k != "overall"]:
        t = trends[sector]
        if t.get("article_count", 0) > 0:
            print(f"   {sector:<12}: {t['trend_label']}  "
                  f"score={t['avg_score']:+.2f}  n={t['article_count']}")

    top_neg = ov.get("top_negative", [])
    if top_neg:
        print(f"\n🔴 MOST NEGATIVE NEWS")
        for a in top_neg:
            print(f"   [{a['score']:+d}] {a['title'][:68]}")

    top_pos = ov.get("top_positive", [])
    if top_pos:
        print(f"\n🟢 MOST POSITIVE NEWS")
        for a in top_pos:
            print(f"   [{a['score']:+d}] {a['title'][:68]}")

    print(f"\n{sep}\n")
    logger.info("📄 Report generated")
