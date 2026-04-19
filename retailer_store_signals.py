import json
import re
from collections import defaultdict
from pathlib import Path

import requests

from food_terms import FOOD_TERMS


REQUEST_TIMEOUT_SECONDS = 20
DEFAULT_TOP_RECORDS = 50
CACHE_PATH = Path("retailer_store_signals_cache.json")

# Public pages that can act as a "what is on shelves / being featured" signal.
# These are not official search logs; they are shelf/feature/weekly-ad proxies.
SOURCE_CONFIGS = [
    {
        "source": "hmart_weekly_ads",
        "kind": "html",
        "url": "https://www.hmart.com/weekly-ads",
    },
    {
        "source": "hmart_homepage",
        "kind": "html",
        "url": "https://www.hmart.com/",
    },
    {
        "source": "costco_featured_products",
        "kind": "html",
        "url": "https://www.costco.com/costco-featured-products.html",
    },
    {
        "source": "costco_same_day",
        "kind": "html",
        "url": "https://www.costco.com/same-day.html",
    },
    {
        "source": "ranch99_weekly_ad",
        "kind": "html",
        "url": "https://www.yapik.com/us/99-ranch/weekly-ad",
    },
    {
        "source": "reddit_costco",
        "kind": "reddit_json",
        "url": "https://www.reddit.com/r/Costco/top.json?t=month&limit=100",
    },
]

REQUEST_HEADERS = {
    "User-Agent": (
        "CustomerTrendsResearchBot/1.0 "
        "(public shelf-signal research; contact: local-dev)"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def normalize_term(term):
    return " ".join(str(term).strip().lower().split())


NORMALIZED_FOOD_TERMS = sorted(
    {normalize_term(term) for term in FOOD_TERMS if term},
    key=len,
    reverse=True,
)


def build_term_regex(term):
    escaped = re.escape(term)
    return re.compile(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", re.IGNORECASE)


TERM_PATTERNS = {
    term: build_term_regex(term)
    for term in NORMALIZED_FOOD_TERMS
}


def fetch_source_content(source_config):
    response = requests.get(
        source_config["url"],
        headers=REQUEST_HEADERS,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response


def strip_html_to_text(html):
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_text_chunks_from_reddit_json(payload):
    chunks = []
    for child in payload.get("data", {}).get("children", []):
        data = child.get("data", {})
        chunks.extend(
            [
                data.get("title", ""),
                data.get("selftext", ""),
                data.get("link_flair_text", ""),
            ]
        )
    return " ".join(chunk for chunk in chunks if chunk)


def count_food_term_mentions(text):
    normalized_text = normalize_term(text)
    counts = {}

    for term, pattern in TERM_PATTERNS.items():
        matches = pattern.findall(normalized_text)
        if matches:
            counts[term] = len(matches)

    return counts


def build_retailer_signal_records(source_results, top_records=DEFAULT_TOP_RECORDS):
    term_map = defaultdict(
        lambda: {
            "term": None,
            "mention_count": 0,
            "source_count": 0,
            "sources": [],
            "source_mentions": {},
            "retailer_signal_score": 0,
        }
    )

    for source_result in source_results:
        source_name = source_result["source"]
        url = source_result["url"]

        for term, count in source_result["term_counts"].items():
            entry = term_map[term]
            entry["term"] = term
            entry["mention_count"] += count
            entry["source_count"] += 1
            entry["sources"].append(source_name)
            entry["source_mentions"][source_name] = count
            entry["retailer_signal_score"] = round(
                (entry["mention_count"] * 0.65) + (entry["source_count"] * 15),
                2,
            )
            entry["source_urls"] = entry.get("source_urls", {})
            entry["source_urls"][source_name] = url

    records = sorted(
        term_map.values(),
        key=lambda record: (
            record["retailer_signal_score"],
            record["mention_count"],
            record["source_count"],
        ),
        reverse=True,
    )

    return records[:top_records]


def build_retailer_store_signals_payload(
    top_records=DEFAULT_TOP_RECORDS,
    use_cache_fallback=True,
):
    source_results = []
    source_errors = {}

    for source_config in SOURCE_CONFIGS:
        try:
            response = fetch_source_content(source_config)
            if source_config["kind"] == "reddit_json":
                text = extract_text_chunks_from_reddit_json(response.json())
            else:
                text = strip_html_to_text(response.text)

            term_counts = count_food_term_mentions(text)
            source_results.append(
                {
                    "source": source_config["source"],
                    "url": source_config["url"],
                    "term_counts": term_counts,
                }
            )
        except Exception as exc:
            source_errors[source_config["source"]] = str(exc)

    if source_results:
        payload = {
            "source": "retailer_store_signals",
            "meta": {
                "record_count": 0,
                "source_errors": source_errors,
                "sources_scraped": [result["source"] for result in source_results],
                "cache_path": str(CACHE_PATH),
            },
            "records": build_retailer_signal_records(
                source_results,
                top_records=top_records,
            ),
        }
        payload["meta"]["record_count"] = len(payload["records"])
        CACHE_PATH.write_text(json.dumps(payload, indent=2))
        return payload

    if use_cache_fallback and CACHE_PATH.exists():
        cached_payload = json.loads(CACHE_PATH.read_text())
        cached_payload.setdefault("meta", {})
        cached_payload["meta"]["source_errors"] = source_errors
        cached_payload["meta"]["loaded_from_cache"] = True
        return cached_payload

    return {
        "source": "retailer_store_signals",
        "meta": {
            "record_count": 0,
            "source_errors": source_errors,
            "sources_scraped": [],
            "cache_path": str(CACHE_PATH),
        },
        "records": [],
    }


if __name__ == "__main__":
    payload = build_retailer_store_signals_payload()
    print(json.dumps(payload["meta"], indent=2))
    for record in payload["records"][:20]:
        print(
            f"{record['term']}: score={record['retailer_signal_score']} "
            f"mentions={record['mention_count']} sources={record['sources']}"
        )
