import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# News RSS Sources (Indian Financial News)
NEWS_SOURCES = [
    {"name": "Economic Times Markets",  "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"},
    {"name": "Moneycontrol",            "url": "https://www.moneycontrol.com/rss/MCtopnews.xml"},
    {"name": "Business Standard",       "url": "https://www.business-standard.com/rss/markets-106.rss"},
    {"name": "LiveMint Markets",        "url": "https://www.livemint.com/rss/markets"},
    {"name": "NDTV Profit",             "url": "https://feeds.feedburner.com/ndtvprofit-latest"},
    {"name": "Financial Express",       "url": "https://www.financialexpress.com/market/feed/"},
]

# Indian Indices (via yfinance)
INDICES = {
    "SENSEX":       "^BSESN",
    "NIFTY_50":     "^NSEI",
    "NIFTY_BANK":   "^NSEBANK",
    "NIFTY_IT":     "^CNXIT",
    "NIFTY_AUTO":   "^CNXAUTO",
    "NIFTY_PHARMA": "^CNXPHARMA",
    "NIFTY_FMCG":   "^CNXFMCG",z
    "NIFTY_METAL":  "^CNXMETAL",
    "NIFTY_REALTY": "^CNXREALTY",
}

# Sectors
SECTORS = ["banking", "IT", "auto", "pharma", "FMCG", "metal", "realty", "energy", "infra"]

# Trend thresholds
TREND_WINDOW_HOURS       = 24
NEGATIVE_TREND_THRESHOLD = -3
POSITIVE_TREND_THRESHOLD =  3
