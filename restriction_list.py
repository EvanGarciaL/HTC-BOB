import os
import sys

from dotenv import load_dotenv

try:
    import gemini
except ImportError:  # pragma: no cover - handled at runtime for local setup
    gemini = None


load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-mini")

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


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set.")
    if gemini is None:
        raise RuntimeError(
            "The Gemini Python package is not installed. Run `python3 -m pip install gemini`."
        )
    return gemini


def check_fda_restrictions_with_ai(item):
    """
    Ask the model whether an item appears restricted, banned, recalled,
    or otherwise risky from an FDA/compliance perspective.
    """
    client = get_gemini_client()
    prompt = f"""
You are helping a product discovery team perform an FDA and safety risk screen.

Item: {item}

Respond in exactly this format:
Restriction Risk: <yes/no/unclear>
Reason: <one short sentence>

Only say "yes" if the item is commonly known to be banned, recalled, restricted,
or clearly unsafe for use in a food, beverage, supplement, or consumer product context.
If the answer depends on formulation or use context, say "unclear".
"""

    response = client.responses.create(
        model=GEMINI_MODEL,
        input=prompt,
    )
    return response.output_text.strip()


if __name__ == "__main__":
    item = " ".join(sys.argv[1:]).strip()
    if not item:
        item = input("Enter product/substance: ").strip()

    print(f"\nStatic restriction list hit: {item.lower() in restriction_list}\n")

    try:
        ai_result = check_fda_restrictions_with_ai(item)
        print(f"AI Analysis for FDA Restrictions on '{item}':\n")
        print(ai_result)
    except Exception as exc:
        print(f"Unable to run Gemini FDA check: {exc}")
