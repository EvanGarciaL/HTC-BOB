"""
batch_etl.py: Scheduled Pipeline Runner (Cron target)

Extracts data from Google Trends and Amazon Bestsellers, applies AI compliance enrichment,
calculates the T.R.U.S.T. score, and loads the structured artifact into a JSON file
(or database in Vercel Postgres).
"""
import json
import os
from datetime import datetime
from combined_trends import build_combined_trend_records
from gemini_compliance import evaluate_opportunity_with_ai
from trust_scoring import calculate_trust_score

def run_pipeline():
    print("Beginning Batch ETL Pipeline (Vercel Cron Equivalent)...")
    
    # 1. EXTRACT: Pull leading indicators and validation metrics
    # Note: using temporary demo data if APIs fail or are missing keys to ensure robust execution
    # Quick override for demo ensuring no API costs are incurred.
    use_mock = True
    
    if use_mock:
         print("Running in DEMO mode to avoid API costs and demonstrate the pipeline.")
    
    records, errors = build_combined_trend_records(
        google_timeframe="today 3-m",
        google_geo="US",
        amazon_max_keywords=5,
        use_temporary_demo_data=use_mock
    )
    
    print(f"Extracted {len(records)} initial trend signals.")
    
    processed_records = []
    
    # 2. TRANSFORM (Enrich with AI and Score)
    for record in records:
        term = record["term"]
        category = record.get("business_filter", {}).get("category", "General")
        
        print(f" -> AI Compliance Check: {term}")
        record["ai_compliance"] = evaluate_opportunity_with_ai(term, category)
        
        # Calculate T.R.U.S.T score
        record = calculate_trust_score(record)
        processed_records.append(record)

    # Sort by total T.R.U.S.T score descending
    processed_records.sort(key=lambda x: x["trust_breakdown"]["total_score"], reverse=True)

    # 3. LOAD: Save artifact for frontend
    # In Vercel, this would be an INSERT to Vercel Postgres. 
    # Here, we save to a JSON artifact consumed by our Next.js frontend.
    output_payload = {
        "generated_at": datetime.utcnow().isoformat(),
        "record_count": len(processed_records),
        "source_errors": errors,
        "trusted_trends": processed_records
    }
    
    out_file = "latest_trends.json"
    with open(out_file, "w") as f:
        json.dump(output_payload, f, indent=2)
        
    print(f"\nETL Pipeline Complete. Saved {len(processed_records)} scored trends to {out_file}")

if __name__ == "__main__":
    run_pipeline()
