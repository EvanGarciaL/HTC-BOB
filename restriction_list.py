import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

OPENFDA_BASE = "https://api.fda.gov"

# Shared restriction list used by the business-filtering pipeline.
restriction_list = [
    "ephedra",
    "tianeptine",
    "kratom",
    "phenibut",
    "dmha",
    "dmaa",
    "silver solution",
    "cyanide",
]


def check_fda_restrictions_with_api(item: str) -> dict:
    """
    Search OpenFDA enforcement (recalls) and drug adverse events
    for any records mentioning the item.
    Returns a summary dict with hit counts per endpoint.
    """
    results = {}
    endpoints = {
        "food_enforcement": f"{OPENFDA_BASE}/food/enforcement.json",
        "drug_enforcement": f"{OPENFDA_BASE}/drug/enforcement.json",
        "supplement_adverse_events": f"{OPENFDA_BASE}/food/event.json",
    }

    for label, url in endpoints.items():
        try:
            resp = requests.get(
                url,
                params={"search": item, "limit": 5},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                total = data.get("meta", {}).get("results", {}).get("total", 0)
                results[label] = {
                    "total_hits": total,
                    "sample": [
                        r.get("reason_for_recall") or r.get("outcomes") or "N/A"
                        for r in data.get("results", [])[:3]
                    ],
                }
            elif resp.status_code == 404:
                results[label] = {"total_hits": 0, "sample": []}
            else:
                results[label] = {"error": f"HTTP {resp.status_code}"}
        except requests.RequestException as exc:
            results[label] = {"error": str(exc)}

    return results


def format_fda_results(item: str, data: dict) -> str:
    lines = [f"OpenFDA results for '{item}':\n"]
    any_hits = False

    for endpoint, info in data.items():
        if "error" in info:
            lines.append(f"  [{endpoint}] Error: {info['error']}")
            continue

        total = info["total_hits"]
        if total > 0:
            any_hits = True
        lines.append(f"  [{endpoint}] Total records found: {total}")

        for i, sample in enumerate(info["sample"], 1):
            if isinstance(sample, list):
                sample = ", ".join(sample)
            lines.append(f"    {i}. {sample}")

    lines.append("")
    lines.append(
        f"Restriction Risk: {'yes' if any_hits else 'no'} "
        f"(based on OpenFDA enforcement/adverse event records)"
    )
    return "\n".join(lines)


if __name__ == "__main__":
    item = " ".join(sys.argv[1:]).strip()
    if not item:
        item = input("Enter product/substance: ").strip()

    print(f"\nStatic restriction list hit: {item.lower() in restriction_list}\n")

    try:
        raw = check_fda_restrictions_with_api(item)
        print(format_fda_results(item, raw))
    except Exception as exc:
        print(f"Unable to run OpenFDA check: {exc}")