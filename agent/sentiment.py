import google.generativeai as genai
import json
import re
import logging
from config import GEMINI_API_KEY, SECTORS

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
logger = logging.getLogger(__name__)

RATING_PROMPT = """
You are a financial news analyst specialising in Indian markets.
Analyse this article and return ONLY a JSON object - no other text.

Title:   {title}
Summary: {summary}

JSON format:
{{
  "score":        <integer -10 to +10>,
  "sentiment":    "<negative|neutral|positive>",
  "sector":       "<one of: {sectors} | general>",
  "keywords":     ["<kw1>", "<kw2>", "<kw3>"],
  "reasoning":    "<one sentence>",
  "is_financial": <true|false>
}}

Scoring:
  -10 to -7 : Severely negative  (crash, fraud, crisis)
  -6  to -4 : Moderately negative (earnings miss, rate hike, layoffs)
  -3  to -1 : Mildly negative    (headwinds, cautious outlook)
   0        : Neutral             (informational)
  +1  to +3 : Mildly positive    (minor good news)
  +4  to +6 : Moderately positive (earnings beat, expansion)
  +7  to +10: Strongly positive  (record profits, major reforms)
"""


def rate_article(article: dict) -> dict:
    prompt = RATING_PROMPT.format(
        title=article["title"],
        summary=article.get("summary", ""),
        sectors=", ".join(SECTORS),
    )
    try:
        resp  = model.generate_content(
            prompt,
            generation_config={"temperature": 0.1, "max_output_tokens": 300},
        )
        text  = resp.text.strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON found")
        result = json.loads(match.group())
        result["score"] = max(-10, min(10, int(result.get("score", 0))))
        return result
    except Exception as e:
        logger.error(f"Rating failed for '{article['title']}': {e}")
        return {
            "score": 0, "sentiment": "neutral", "sector": "general",
            "keywords": [], "reasoning": "Rating failed", "is_financial": True,
        }


def rate_batch(articles: list[dict]) -> list[dict]:
    for article in articles:
        article.update(rate_article(article))
    return articles
