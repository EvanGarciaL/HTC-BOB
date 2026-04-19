"""
export_latest_trends.py

Rebuilds the frontend's `latest_trends.json` snapshot from the local temporary
trend dataset so the Next.js app reflects the same data source as the Python
pipeline each time the frontend starts.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from combined_trends import build_combined_trend_records
from gemini_compliance import get_competitors_and_recommendations


ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = ROOT / "frontend/src/app/latest_trends.json"
INSIGHTS_CACHE_PATH = ROOT / "product_insights_cache.json"
LEGACY_SAMPLE_COMPETITORS = {
    "Olly — mass-market wellness brand with strong retail distribution",
    "Garden of Life — premium natural products, Whole Foods presence",
    "Herbaland — gummy-focused brand expanding in North America",
}
LEGACY_SAMPLE_RECOMMENDATIONS = {
    "Probiotic Gummies — adds digestive health angle aligned with POP wellness focus",
    "Ube Gummies — leverages trending Asian flavor for differentiation",
    "Collagen Gummies — taps into beauty-from-within trend",
    "Taro Milk Tea Gummies — bridges snack + tea category synergy",
}


def clamp(value, low, high):
    return max(low, min(high, value))


def load_insights_cache():
    if not INSIGHTS_CACHE_PATH.exists():
        return {}
    try:
        return json.loads(INSIGHTS_CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_insights_cache(cache):
    INSIGHTS_CACHE_PATH.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def get_record_category(record):
    return (
        record.get("business_filter", {}).get("category")
        or record.get("business_filter", {}).get("product_format")
        or "uncategorized"
    )


def is_legacy_sample_insights(insights):
    competitors = set(insights.get("competitors", []))
    recommendations = set(insights.get("recommendations", []))
    return (
        competitors == LEGACY_SAMPLE_COMPETITORS
        or recommendations == LEGACY_SAMPLE_RECOMMENDATIONS
    )


def get_product_insights(record, cache):
    term = record["term"]
    category = get_record_category(record)
    cache_key = f"{term}::{category}"
    cached = cache.get(cache_key)
    if cached and not is_legacy_sample_insights(cached):
        return cached

    try:
        insights = get_competitors_and_recommendations(term, category)
    except Exception as e:
        print(f"[INSIGHTS ERROR] {term}: {e}")
        if cached:
            return cached
        return {
            "competitors": [],
            "recommendations": [],
        }
    normalized = {
        "competitors": insights.get("competitors", []),
        "recommendations": insights.get("recommendations", []),
    }
    cache[cache_key] = normalized
    return normalized


def build_trust_breakdown(record):
    google_score = record["combined_signals"].get("google_opportunity_score") or 0.0
    amazon_score = record["combined_signals"].get("amazon_opportunity_score") or 0.0
    passes = bool(record["business_filter"].get("passes"))
    google_velocity = (record.get("google_trends") or {}).get("trend_velocity", 0.0)
    format_bonus = 2.0 if record["business_filter"].get("product_format") else 0.0
    category_bonus = 2.0 if record["business_filter"].get("category") not in (None, "uncategorized") else 0.0
    source_bonus = 6.0 if record.get("google_trends") and record.get("amazon_trends") else 2.5

    trajectory_30 = round(clamp((google_velocity / 100.0) * 30.0, 6.0, 30.0), 1)
    risk_20 = 20.0 if passes else 8.0
    uniqueness_20 = round(
        clamp(
            6.0 + source_bonus + format_bonus + category_bonus + max(0.0, (google_score - amazon_score) * 0.08),
            4.0,
            20.0,
        ),
        1,
    )
    sourcing_15 = 14.0 if passes else 9.0
    translation_15 = round(
        clamp(
            7.0 + ((amazon_score / 100.0) * 5.0) + (3.0 if record["business_filter"].get("category") else 0.0),
            5.0,
            15.0,
        ),
        1,
    )
    total_score = round(trajectory_30 + risk_20 + uniqueness_20 + sourcing_15 + translation_15, 1)
    risk_notes = (
        "Cleared: Verified >12 mo ambient shelf-stable and contains no restricted ingredients."
        if passes
        else "Monitoring: Does not yet pass shelf-life or restriction screening."
    )

    return {
        "trajectory_30": trajectory_30,
        "risk_20": risk_20,
        "uniqueness_20": uniqueness_20,
        "sourcing_15": sourcing_15,
        "translation_15": translation_15,
        "total_score": total_score,
        "risk_notes": risk_notes,
        "passed": passes,
    }


def enrich_record(record, insights_cache):
    trust_breakdown = build_trust_breakdown(record)
    product_insights = get_product_insights(record, insights_cache)
    return {
        **record,
        "ai_compliance": {
            "risk_compliance_pass": trust_breakdown["passed"],
            "risk_notes": trust_breakdown["risk_notes"],
            "sourcing_feasibility_score": trust_breakdown["sourcing_15"],
            "translation_to_market_score": trust_breakdown["translation_15"],
        },
        "trust_breakdown": trust_breakdown,
        "product_insights": product_insights,
    }


def main():
    insights_cache = load_insights_cache()
    records, source_errors = build_combined_trend_records(
        amazon_max_keywords=100,
        use_temporary_demo_data=True,
    )
    print(f"\n[INFO] Starting AI processing for {len(records)} records. The Google API may take 30-60s to detect quota/availability issues. Please do not close...")
    enriched_records = []
    for i, record in enumerate(records):
        print(f"Processing {i+1}/{len(records)}: {record['term']}")
        enriched_records.append(enrich_record(record, insights_cache))
    save_insights_cache(insights_cache)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "record_count": len(records),
        "source_errors": source_errors,
        "trusted_trends": enriched_records,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} records to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
