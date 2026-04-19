"""
fetch_product_insights.py

Fetch live product competitor/recommendation insights for a single term.
Caches successful Gemini responses and falls back to cached data if the live
call fails.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from gemini_compliance import get_competitors_and_recommendations


ROOT = Path(__file__).resolve().parent
INSIGHTS_CACHE_PATH = ROOT / "product_insights_cache.json"


def load_cache():
    if not INSIGHTS_CACHE_PATH.exists():
        return {}
    try:
        return json.loads(INSIGHTS_CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_cache(cache):
    INSIGHTS_CACHE_PATH.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def main():
    term = sys.argv[1] if len(sys.argv) > 1 else ""
    category = sys.argv[2] if len(sys.argv) > 2 else "uncategorized"
    cache_key = f"{term}::{category}"
    cache = load_cache()

    try:
        insights = get_competitors_and_recommendations(term, category)
        normalized = {
            "competitors": insights.get("competitors", []),
            "recommendations": insights.get("recommendations", []),
        }
        cache[cache_key] = normalized
        save_cache(cache)
        print(json.dumps(normalized))
        return
    except Exception:
        cached = cache.get(cache_key, {"competitors": [], "recommendations": []})
        print(json.dumps(cached))


if __name__ == "__main__":
    main()
