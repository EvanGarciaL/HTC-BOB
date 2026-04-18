from pytrends.request import TrendReq
import pandas as pd
from food_terms import (
    DISCOVERY_SEED_KEYWORDS,
    FOOD_TERMS,
    INGREDIENT_TERMS,
    NOISE_PATTERNS,
    PRODUCT_FORMAT_TERMS,
)

BREAKOUT_GROWTH = 5000
MAX_ROWS = 40

# Intent buckets help the product team distinguish curiosity from purchase-like demand.
INTENT_PATTERNS = {
    "make_at_home": [
        "recipe",
        "how to make",
        "homemade",
        "diy",
        "copycat",
    ],
    "learn": [
        "what is",
        "benefits",
        "healthy",
        "nutrition",
        "good for",
        "ingredients",
    ],
    "eat_or_buy": [
        "where to buy",
        "near me",
        "best",
        "drink",
        "snack",
        "tea",
        "soda",
        "bar",
        "chips",
        "candy",
    ],
}


def normalize_rising_value(value):
    # Google Trends may label extreme growth as "Breakout" instead of a number.
    if pd.isna(value):
        return 0
    if isinstance(value, str) and value.lower() == "breakout":
        return BREAKOUT_GROWTH
    return int(value)


def fetch_related_queries(pytrends, seed_keyword, timeframe, geo):
    # Each seed keyword is used to discover related top and rising searches.
    pytrends.build_payload([seed_keyword], timeframe=timeframe, geo=geo)
    related_queries = pytrends.related_queries().get(seed_keyword, {})
    return related_queries.get("top"), related_queries.get("rising")


def detect_intent(query):
    # Map raw search phrasing into a simple intent label for downstream scoring.
    lowered = query.lower()

    for intent, patterns in INTENT_PATTERNS.items():
        if any(pattern in lowered for pattern in patterns):
            return intent

    return "general_interest"


def is_food_relevant(query):
    # Check the query against our shared food vocabulary in food_terms.py.
    lowered = query.lower()
    return any(keyword in lowered for keyword in FOOD_TERMS)


def is_noise(query):
    # Filter obvious non-product noise that can appear in Google Trends results.
    lowered = query.lower()
    return any(pattern in lowered for pattern in NOISE_PATTERNS)


def classify_market_signal(intent):
    if intent == "eat_or_buy":
        return "commercial_demand"
    if intent == "make_at_home":
        return "at_home_creation"
    if intent == "learn":
        return "consumer_education"
    return "emerging_interest"


def detect_trend_type(query):
    # Separate ingredient-led trends from product-format trends for the frontend.
    lowered = query.lower()
    if any(keyword in lowered for keyword in INGREDIENT_TERMS):
        return "ingredient"
    if any(keyword in lowered for keyword in PRODUCT_FORMAT_TERMS):
        return "product_format"
    return "product_or_query"


def build_food_trends_dataframe(
    seed_keywords=None,
    timeframe="today 3-m",
    geo="US",
):
    # Build a ranked table of food-related Google Trends opportunities.
    seed_keywords = seed_keywords or DISCOVERY_SEED_KEYWORDS
    pytrends = TrendReq(hl="en-US", tz=360)
    trend_map = {}

    for seed_keyword in seed_keywords:
        top_df, rising_df = fetch_related_queries(
            pytrends,
            seed_keyword,
            timeframe=timeframe,
            geo=geo,
        )

        if top_df is not None:
            for row in top_df.itertuples(index=False):
                query = row.query.strip().lower()
                # Keep the strongest popularity score we see for a query across seeds.
                entry = trend_map.setdefault(
                    query,
                    {
                        "query": query,
                        "source_seed": seed_keyword,
                        "popularity_score": 0,
                        "search_growth": 0,
                    },
                )
                entry["popularity_score"] = max(entry["popularity_score"], int(row.value))

        if rising_df is not None:
            for row in rising_df.itertuples(index=False):
                query = row.query.strip().lower()
                # Keep the strongest growth score we see for a query across seeds.
                entry = trend_map.setdefault(
                    query,
                    {
                        "query": query,
                        "source_seed": seed_keyword,
                        "popularity_score": 0,
                        "search_growth": 0,
                    },
                )
                entry["search_growth"] = max(
                    entry["search_growth"],
                    normalize_rising_value(row.value),
                )

    trend_df = pd.DataFrame(trend_map.values())
    if trend_df.empty:
        return trend_df

    # Enrich each query with labels the frontend and later filtering steps can use.
    trend_df["intent_bucket"] = trend_df["query"].apply(detect_intent)
    trend_df["market_signal"] = trend_df["intent_bucket"].apply(classify_market_signal)
    trend_df["trend_type"] = trend_df["query"].apply(detect_trend_type)
    trend_df["food_relevant"] = trend_df["query"].apply(is_food_relevant)
    trend_df["is_noise"] = trend_df["query"].apply(is_noise)

    trend_df = trend_df[
        (trend_df["food_relevant"])
        & (~trend_df["is_noise"])
    ].copy()

    if trend_df.empty:
        return trend_df

    max_growth = trend_df["search_growth"].max()
    if max_growth > 0:
        trend_df["trend_velocity"] = (trend_df["search_growth"] / max_growth) * 100
    else:
        trend_df["trend_velocity"] = 0

    # Weight intent slightly so buy/eat behavior ranks above passive curiosity.
    intent_weight_map = {
        "eat_or_buy": 1.2,
        "make_at_home": 1.05,
        "learn": 0.95,
        "general_interest": 1.0,
    }
    trend_df["intent_weight"] = trend_df["intent_bucket"].map(intent_weight_map).fillna(1.0)

    trend_df["opportunity_score"] = (
        (
            trend_df["popularity_score"] * 0.5
            + trend_df["trend_velocity"] * 0.5
        ) * trend_df["intent_weight"]
    ).round(2)

    trend_df = trend_df.sort_values(
        by=["opportunity_score", "trend_velocity", "popularity_score"],
        ascending=False,
    ).reset_index(drop=True)

    return trend_df[
        [
            "query",
            "source_seed",
            "intent_bucket",
            "trend_type",
            "market_signal",
            "popularity_score",
            "search_growth",
            "trend_velocity",
            "opportunity_score",
        ]
    ]


def build_google_trend_records(
    seed_keywords=None,
    timeframe="today 3-m",
    geo="US",
):
    # Convert the DataFrame into JSON-friendly records for the frontend/API layer.
    trend_df = build_food_trends_dataframe(
        seed_keywords=seed_keywords,
        timeframe=timeframe,
        geo=geo,
    )

    if trend_df.empty:
        return []

    return trend_df.to_dict(orient="records")


def build_google_trends_payload(
    seed_keywords=None,
    timeframe="today 3-m",
    geo="US",
):
    # Wrap records with metadata so other parts of the app know how they were generated.
    records = build_google_trend_records(
        seed_keywords=seed_keywords,
        timeframe=timeframe,
        geo=geo,
    )

    return {
        "source": "google_trends",
        "meta": {
            "timeframe": timeframe,
            "geo": geo,
            "seed_keywords": seed_keywords or DISCOVERY_SEED_KEYWORDS,
            "food_term_count": len(FOOD_TERMS),
            "record_count": len(records),
        },
        "records": records,
    }


def build_google_trends_lookup(
    seed_keywords=None,
    timeframe="today 3-m",
    geo="US",
):
    # Create a merge-friendly structure for combining Google and Amazon signals later.
    payload = build_google_trends_payload(
        seed_keywords=seed_keywords,
        timeframe=timeframe,
        geo=geo,
    )

    return {
        record["query"]: {
            "term": record["query"],
            "google_trends": record,
            "amazon_trends": None,
            "combined_signals": {},
        }
        for record in payload["records"]
    }


if __name__ == "__main__":
    payload = build_google_trends_payload()

    print("\n=== GOOGLE TRENDS PAYLOAD READY ===\n")
    print(f"Records collected: {payload['meta']['record_count']}")

    if not payload["records"]:
        print("No relevant food search trends were returned by pytrends.")
    else:
        preview_df = pd.DataFrame(payload["records"]).head(MAX_ROWS)
        print(preview_df.to_string(index=False))
