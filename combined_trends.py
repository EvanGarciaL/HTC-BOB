import pandas as pd

from amazon_api import build_amazon_trends_payload
from google_api import build_google_trends_payload
from restriction_list import restriction_list
from temporary_demo_data import (
    TEMPORARY_AMAZON_TRENDS_RECORDS,
    TEMPORARY_GOOGLE_TRENDS_RECORDS,
)


LONG_SHELF_LIFE_FORMATS = {
    "bar",
    "biscuit",
    "bites",
    "broth",
    "candy",
    "capsule",
    "cereal",
    "chews",
    "chips",
    "cookie",
    "cracker",
    "dip",
    "drink",
    "elixir",
    "gel",
    "gummies",
    "gum",
    "juice",
    "mix",
    "mocktail",
    "powder",
    "seasoning",
    "shake",
    "shot",
    "snack",
    "soda",
    "sparkling water",
    "supplement",
    "syrup",
    "tea",
    "tonic",
    "trail mix",
    "water",
    "wellness shot",
}

POPPI_CATEGORY_KEYWORDS = {
    "beverages": {
        "beverage",
        "coffee",
        "drink",
        "elixir",
        "juice",
        "latte",
        "lemonade",
        "mocktail",
        "shake",
        "shot",
        "smoothie",
        "soda",
        "sparkling water",
        "tea",
        "tonic",
        "water",
        "wellness shot",
        "yogurt drink",
    },
    "confections": {
        "brownie",
        "candy",
        "chews",
        "chocolate",
        "cookie",
        "dessert",
        "fudge",
        "gummies",
        "marshmallow",
        "popsicle",
        "sour candy",
        "wafer",
    },
    "snacks": {
        "bar",
        "biscuit",
        "bites",
        "cereal",
        "chips",
        "cracker",
        "granola",
        "jerky",
        "noodles",
        "popcorn",
        "pretzel",
        "snack",
        "trail mix",
        "wrap",
    },
    "dry goods": {
        "broth",
        "capsule",
        "mix",
        "powder",
        "recipe",
        "seasoning",
        "supplement",
        "syrup",
    },
    "health & wellness": {
        "adaptogen",
        "collagen",
        "electrolyte",
        "fiber",
        "functional",
        "gut health",
        "prebiotic",
        "probiotic",
        "protein",
        "superfood",
        "vitamin",
        "wellness",
    },
}


def normalize_term(term):
    return " ".join(str(term).strip().lower().split())


def detect_product_format(term):
    normalized = normalize_term(term)
    for candidate in sorted(LONG_SHELF_LIFE_FORMATS, key=len, reverse=True):
        if candidate in normalized:
            return candidate
    return None


def categorize_term(term):
    normalized = normalize_term(term)
    for category, keywords in POPPI_CATEGORY_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return category
    return "uncategorized"


def has_long_shelf_life(term):
    return detect_product_format(term) in LONG_SHELF_LIFE_FORMATS


def hits_restriction_list(term):
    normalized = normalize_term(term)
    restrictions = [normalize_term(item) for item in restriction_list]
    return any(item in normalized for item in restrictions if item and item != "...")


def build_business_filter(term):
    product_format = detect_product_format(term)
    category = categorize_term(term)
    restricted = hits_restriction_list(term)
    shelf_life_ok = has_long_shelf_life(term)

    return {
        "passes": shelf_life_ok and not restricted,
        "shelf_life_ok": shelf_life_ok,
        "restriction_flag": restricted,
        "category": category,
        "product_format": product_format,
    }


def build_combined_trend_records(
    google_seed_keywords=None,
    google_timeframe="today 3-m",
    google_geo="US",
    amazon_seed_keywords=None,
    amazon_max_keywords=None,
    use_temporary_demo_data=False,
):
    source_errors = {}

    if use_temporary_demo_data:
        google_payload = {
            "source": "google_trends",
            "meta": {
                "timeframe": google_timeframe,
                "geo": google_geo,
                "record_count": len(TEMPORARY_GOOGLE_TRENDS_RECORDS),
                "temporary_demo_data": True,
            },
            "records": TEMPORARY_GOOGLE_TRENDS_RECORDS,
        }
        amazon_payload = {
            "source": "amazon_trends",
            "meta": {
                "record_count": len(TEMPORARY_AMAZON_TRENDS_RECORDS),
                "temporary_demo_data": True,
            },
            "records": TEMPORARY_AMAZON_TRENDS_RECORDS,
        }
    else:
        try:
            google_payload = build_google_trends_payload(
                seed_keywords=google_seed_keywords,
                timeframe=google_timeframe,
                geo=google_geo,
            )
        except Exception as exc:
            google_payload = {
                "source": "google_trends",
                "meta": {
                    "timeframe": google_timeframe,
                    "geo": google_geo,
                    "record_count": 0,
                },
                "records": [],
            }
            source_errors["google_trends"] = str(exc)

        try:
            amazon_payload = build_amazon_trends_payload(
                seed_keywords=amazon_seed_keywords,
                max_keywords=amazon_max_keywords,
            )
        except Exception as exc:
            amazon_payload = {
                "source": "amazon_trends",
                "meta": {
                    "record_count": 0,
                },
                "records": [],
            }
            source_errors["amazon_trends"] = str(exc)

    combined_lookup = {}

    for google_record in google_payload["records"]:
        term = normalize_term(google_record["query"])
        combined_lookup[term] = {
            "term": term,
            "google_trends": google_record,
            "amazon_trends": None,
            "business_filter": build_business_filter(term),
            "combined_signals": {
                "google_opportunity_score": google_record["opportunity_score"],
                "amazon_opportunity_score": None,
                "google_market_signal": google_record["market_signal"],
                "amazon_market_signal": None,
            },
        }

    for amazon_record in amazon_payload["records"]:
        term = normalize_term(amazon_record["query"])
        existing = combined_lookup.setdefault(
            term,
            {
                "term": term,
                "google_trends": None,
                "amazon_trends": None,
                "business_filter": build_business_filter(term),
                "combined_signals": {
                    "google_opportunity_score": None,
                    "amazon_opportunity_score": None,
                    "google_market_signal": None,
                    "amazon_market_signal": None,
                },
            },
        )
        existing["amazon_trends"] = amazon_record
        existing["combined_signals"]["amazon_opportunity_score"] = amazon_record[
            "amazon_opportunity_score"
        ]
        existing["combined_signals"]["amazon_market_signal"] = amazon_record[
            "amazon_market_signal"
        ]

    for record in combined_lookup.values():
        record["combined_signals"]["business_filter_pass"] = record["business_filter"][
            "passes"
        ]

    return list(combined_lookup.values()), source_errors


def build_combined_trends_payload(
    google_seed_keywords=None,
    google_timeframe="today 3-m",
    google_geo="US",
    amazon_seed_keywords=None,
    amazon_max_keywords=None,
    use_temporary_demo_data=False,
):
    records, source_errors = build_combined_trend_records(
        google_seed_keywords=google_seed_keywords,
        google_timeframe=google_timeframe,
        google_geo=google_geo,
        amazon_seed_keywords=amazon_seed_keywords,
        amazon_max_keywords=amazon_max_keywords,
        use_temporary_demo_data=use_temporary_demo_data,
    )

    return {
        "source": "combined_trends",
        "meta": {
            "google_timeframe": google_timeframe,
            "google_geo": google_geo,
            "record_count": len(records),
            "source_errors": source_errors,
            "temporary_demo_data": use_temporary_demo_data,
        },
        "records": records,
    }


def build_combined_trends_dataframe(
    google_seed_keywords=None,
    google_timeframe="today 3-m",
    google_geo="US",
    amazon_seed_keywords=None,
    amazon_max_keywords=None,
    use_temporary_demo_data=False,
):
    records, _source_errors = build_combined_trend_records(
        google_seed_keywords=google_seed_keywords,
        google_timeframe=google_timeframe,
        google_geo=google_geo,
        amazon_seed_keywords=amazon_seed_keywords,
        amazon_max_keywords=amazon_max_keywords,
        use_temporary_demo_data=use_temporary_demo_data,
    )

    rows = []
    for record in records:
        rows.append(
            {
                "term": record["term"],
                "google_score": record["combined_signals"]["google_opportunity_score"],
                "amazon_score": record["combined_signals"]["amazon_opportunity_score"],
                "google_signal": record["combined_signals"]["google_market_signal"],
                "amazon_signal": record["combined_signals"]["amazon_market_signal"],
                "category": record["business_filter"]["category"],
                "product_format": record["business_filter"]["product_format"],
                "shelf_life_ok": record["business_filter"]["shelf_life_ok"],
                "restriction_flag": record["business_filter"]["restriction_flag"],
                "business_filter_pass": record["business_filter"]["passes"],
            }
        )

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)


if __name__ == "__main__":
    payload = build_combined_trends_payload(amazon_max_keywords=10)
    print("\n=== COMBINED GOOGLE + AMAZON TREND PAYLOAD READY ===\n")
    print(f"Records collected: {payload['meta']['record_count']}")

    preview_df = build_combined_trends_dataframe(amazon_max_keywords=10)
    if preview_df.empty:
        print("No combined records were generated.")
    else:
        print(preview_df.head(40).to_string(index=False))
