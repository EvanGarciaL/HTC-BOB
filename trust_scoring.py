"""
trust_scoring.py: The POP Opportunity T.R.U.S.T. Score Engine

Calculates a comprehensive business score out of 100 based on the T.R.U.S.T. matrix:
T - Trajectory (30 pts, week-over-week velocity)
R - Risk & Compliance (Pass/Fail)
U - Uniqueness & Saturation (20 pts, Amazon whitespace)
S - Sourcing Feasibility (15 pts, logistics, evaluated by AI)
T - Translation to Market (15 pts, POP brand fit, evaluated by AI)

Missing 20 points? Ah, wait:
T: 30
R: +20 (or Pass/Fail, if pass, you get 20 points)
U: 20
S: 15
T: 15
Total = 100 points.
"""

def calculate_trust_score(record: dict) -> dict:
    """
    Takes a combined_trend record containing Google, Amazon, and AI compliance data,
    and returns an augmented record with the T.R.U.S.T score components.
    """
    
    # 1. T - Trajectory (30 pts)
    # Derived from Google Trends momentum
    google_data = record.get("google_trends") or {}
    velocity = google_data.get("trend_velocity", 0)
    # Map 0-100 velocity to a max of 30 points
    t_score = round((velocity / 100.0) * 30.0, 1)
    
    # 2. R - Risk & Compliance (20 pts / Fail)
    ai_data = record.get("ai_compliance") or {}
    passes_risk = ai_data.get("risk_compliance_pass", True)
    r_score = 20.0 if passes_risk else 0.0
    
    # 3. U - Uniqueness & Saturation (20 pts)
    # High Google Demand + Low Amazon Popularity = High Whitespace (Uniqueness)
    amazon_data = record.get("amazon_trends") or {}
    # We penalize if amazon_popularity_score is extremely high (market saturation)
    amz_pop = amazon_data.get("amazon_popularity_score", 0)
    # Let's say > 3000 reviews is heavily saturated.
    saturation_discount = min(amz_pop / 3000.0, 1.0)
    # The more velocity and LESS saturation, the better.
    # Base it on a combination: if velocity is high and saturation is low.
    whitespace_ratio = 1.0 - saturation_discount
    u_score = round(((velocity / 100.0) * whitespace_ratio) * 20.0, 1)
    if not amazon_data:
        # If no amazon data exists, assume average uniqueness (maybe the trend hasn't hit Amazon yet)
        u_score = round((velocity / 100.0) * 15.0, 1)

    # 4. S - Sourcing Feasibility (15 pts)
    s_score = float(ai_data.get("sourcing_feasibility_score", 10.0))
    # Cap at 15
    s_score = min(s_score, 15.0)

    # 5. T - Translation to Market (15 pts)
    t2_score = float(ai_data.get("translation_to_market_score", 10.0))
    # Cap at 15
    t2_score = min(t2_score, 15.0)
    
    total_trust_score = round(t_score + r_score + u_score + s_score + t2_score, 1)
    
    record["trust_breakdown"] = {
        "trajectory_30": t_score,
        "risk_20": r_score,
        "uniqueness_20": u_score,
        "sourcing_15": s_score,
        "translation_15": t2_score,
        "total_score": total_trust_score,
        "risk_notes": ai_data.get("risk_notes", ""),
        "passed": passes_risk
    }
    
    return record
