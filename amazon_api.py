import os

import pandas as pd
import requests
from food_terms import DISCOVERY_SEED_KEYWORDS, FOOD_TERMS

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - local environment fallback
    def load_dotenv():
        return False


load_dotenv()


API_KEY = os.environ.get("RAINFOREST_API_KEY", "YOUR_RAINFOREST_API_KEY_HERE")
SAMPLE_SIZE = 3
MAX_BSR_THRESHOLD = 50000
REQUEST_TIMEOUT_SECONDS = 20


def normalize_term(term):
    return " ".join(str(term).strip().lower().split())


def build_amazon_keyword_list(seed_keywords=None, max_keywords=None):
    keywords = seed_keywords or DISCOVERY_SEED_KEYWORDS
    normalized_keywords = []
    seen = set()

    for keyword in keywords:
        normalized = normalize_term(keyword)
        if not normalized or normalized in seen:
            continue
        normalized_keywords.append(normalized)
        seen.add(normalized)

    if max_keywords is not None:
        return normalized_keywords[:max_keywords]
    return normalized_keywords


def calculate_velocity_from_bsr(bsr_list):
    if not bsr_list:
        return 0

    avg_bsr = sum(bsr_list) / len(bsr_list)
    if avg_bsr > MAX_BSR_THRESHOLD:
        return 0

    velocity = ((MAX_BSR_THRESHOLD - avg_bsr) / MAX_BSR_THRESHOLD) * 100
    return round(velocity, 2)


def calculate_popularity_from_reviews(review_counts):
    if not review_counts:
        return 0
    return sum(review_counts) / len(review_counts)


def classify_amazon_market_signal(popularity, velocity):
    if popularity < 500 and velocity > 80:
        return "emerging_opportunity"
    if popularity > 3000 and velocity > 80:
        return "established_market"
    if popularity > 1000 and velocity < 30:
        return "declining_trend"
    return "niche_market"


def fetch_amazon_search_metrics(keyword):
    api_parameters = {
        "api_key": API_KEY,
        "type": "search",
        "amazon_domain": "amazon.com",
        "search_term": keyword,
    }

    response = requests.get(
        "https://api.rainforestapi.com/request",
        params=api_parameters,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    data = response.json()

    top_items = data.get("search_results", [])[:SAMPLE_SIZE]
    bsr_list = []
    review_list = []
    price_list = []

    for item in top_items:
        bsr_info = item.get("bestsellers_rank", [])
        if bsr_info:
            rank_str = str(bsr_info[0].get("rank", "0")).replace(",", "")
            if rank_str.isdigit() and int(rank_str) > 0:
                bsr_list.append(int(rank_str))

        reviews = item.get("ratings_total", 0)
        if reviews > 0:
            review_list.append(reviews)

        price_info = item.get("price", {})
        price_val = price_info.get("value")
        if price_val:
            price_list.append(float(price_val))

    return {
        "bsr_list": bsr_list,
        "review_list": review_list,
        "price_list": price_list,
    }


def build_amazon_trends_dataframe(seed_keywords=None, max_keywords=None):
    keywords = build_amazon_keyword_list(
        seed_keywords=seed_keywords,
        max_keywords=max_keywords,
    )
    amazon_rows = []

    print(f"Starting Amazon API research on {len(keywords)} keywords...\n")

    for keyword in keywords:
        print(f"  -> Querying Amazon for: '{keyword}'")

        if API_KEY == "YOUR_RAINFOREST_API_KEY_HERE":
            print("     [!] Skipping actual request since API key is not set.")
            continue

        try:
            metrics = fetch_amazon_search_metrics(keyword)
            amazon_velocity = calculate_velocity_from_bsr(metrics["bsr_list"])
            amazon_popularity = calculate_popularity_from_reviews(metrics["review_list"])
            avg_price = (
                sum(metrics["price_list"]) / len(metrics["price_list"])
                if metrics["price_list"]
                else 0.0
            )

            amazon_rows.append(
                {
                    "query": keyword,
                    "source_seed": keyword,
                    "amazon_market_signal": classify_amazon_market_signal(
                        amazon_popularity,
                        amazon_velocity,
                    ),
                    "amazon_popularity_score": round(amazon_popularity, 1),
                    "amazon_trend_velocity": amazon_velocity,
                    "avg_price": round(avg_price, 2),
                }
            )
        except Exception as exc:
            print(f"     [X] Error fetching {keyword}: {exc}")

    df = pd.DataFrame(amazon_rows)
    if df.empty:
        return df

    max_popularity = df["amazon_popularity_score"].max()
    if pd.notna(max_popularity) and max_popularity > 0:
        df["amazon_popularity_normalized"] = (
            df["amazon_popularity_score"] / max_popularity
        ) * 100
    else:
        df["amazon_popularity_normalized"] = 0

    df["amazon_opportunity_score"] = (
        (df["amazon_trend_velocity"] * 0.7)
        + ((100 - df["amazon_popularity_normalized"]) * 0.3)
    ).round(2)

    df["food_relevant"] = df["query"].apply(
        lambda query: any(term in query for term in FOOD_TERMS)
    )

    df = df.sort_values(
        by=["amazon_opportunity_score", "amazon_trend_velocity"],
        ascending=False,
    ).reset_index(drop=True)

    return df[
        [
            "query",
            "source_seed",
            "amazon_market_signal",
            "amazon_popularity_score",
            "amazon_trend_velocity",
            "amazon_opportunity_score",
            "avg_price",
            "food_relevant",
        ]
    ]


def build_amazon_trend_records(seed_keywords=None, max_keywords=None):
    trend_df = build_amazon_trends_dataframe(
        seed_keywords=seed_keywords,
        max_keywords=max_keywords,
    )

    if trend_df.empty:
        return []

    return trend_df.to_dict(orient="records")


def build_amazon_trends_payload(seed_keywords=None, max_keywords=None):
    records = build_amazon_trend_records(
        seed_keywords=seed_keywords,
        max_keywords=max_keywords,
    )
    effective_keywords = build_amazon_keyword_list(
        seed_keywords=seed_keywords,
        max_keywords=max_keywords,
    )

    return {
        "source": "amazon_trends",
        "meta": {
            "keyword_count": len(effective_keywords),
            "record_count": len(records),
            "keywords": effective_keywords,
        },
        "records": records,
    }


def build_amazon_trends_lookup(seed_keywords=None, max_keywords=None):
    payload = build_amazon_trends_payload(
        seed_keywords=seed_keywords,
        max_keywords=max_keywords,
    )

    return {
        record["query"]: {
            "term": record["query"],
            "google_trends": None,
            "amazon_trends": record,
            "combined_signals": {},
        }
        for record in payload["records"]
    }


if __name__ == "__main__":
    payload = build_amazon_trends_payload(max_keywords=10)

    print("\n=== AMAZON TRENDS PAYLOAD READY ===\n")
    print(f"Records collected: {payload['meta']['record_count']}")

    if not payload["records"]:
        print("No Amazon data was returned. Check the API key or network access.")
    else:
        preview_df = pd.DataFrame(payload["records"]).head(20)
        print(preview_df.to_string(index=False))
