"""
Lead Scoring — weights TA relevance, seniority, activity, email, and signals.
Leads < 40 go to manual review only; never contacted automatically.
"""


def score_lead(
    lead: dict, user_target_role: str, company_signal_score: float
) -> dict:
    """
    Score a lead from 0-100. Returns both score and breakdown.
    Components:
      - TA/recruiting relevance (30 pts)
      - Seniority level (20 pts)
      - Recent post activity (20 pts)
      - Email found (15 pts)
      - Company signal strength (15 pts)
    """
    score = 0.0
    breakdown = {}
    title = lead.get("title", "").lower()

    # 1. Relevance to TA / recruiting function (30pts)
    ta_keywords = [
        "recruiter", "talent", "sourcer", "ta partner",
        "people ops", "hrbp", "talent acquisition",
    ]
    hm_keywords = ["manager", "director", "head of", "vp"]

    if any(kw in title for kw in ta_keywords):
        score += 30
        breakdown["relevance"] = {"score": 30, "reason": "TA/recruiting role"}
    elif any(kw in title for kw in hm_keywords):
        score += 18
        breakdown["relevance"] = {"score": 18, "reason": "Hiring manager"}
    else:
        breakdown["relevance"] = {"score": 0, "reason": "No direct match"}

    # 2. Seniority (20pts)
    senior_keywords = ["senior", "lead", "head", "director", "principal", "vp"]
    junior_keywords = ["associate", "coordinator", "junior", "intern"]

    if any(kw in title for kw in senior_keywords):
        pts = 20
        breakdown["seniority"] = {"score": 20, "reason": "Senior-level"}
    elif any(kw in title for kw in junior_keywords):
        pts = 8
        breakdown["seniority"] = {"score": 8, "reason": "Junior-level"}
    else:
        pts = 12
        breakdown["seniority"] = {"score": 12, "reason": "Mid-level"}
    score += pts

    # 3. Recent activity — has posts (20pts)
    posts = lead.get("recent_posts", [])
    if len(posts) >= 3:
        score += 20
        breakdown["activity"] = {"score": 20, "reason": f"{len(posts)} recent posts"}
    elif len(posts) >= 1:
        score += 10
        breakdown["activity"] = {"score": 10, "reason": f"{len(posts)} recent post(s)"}
    else:
        breakdown["activity"] = {"score": 0, "reason": "No recent posts"}

    # 4. Email found (15pts)
    if lead.get("email"):
        score += 15
        breakdown["email"] = {"score": 15, "reason": "Email found"}
    else:
        breakdown["email"] = {"score": 0, "reason": "No email"}

    # 5. Company signal strength (15pts)
    signal_pts = min(15, company_signal_score * 0.15)
    score += signal_pts
    breakdown["signal"] = {
        "score": round(signal_pts, 1),
        "reason": f"Company signal: {company_signal_score}",
    }

    return {
        "score": round(score, 1),
        "breakdown": breakdown,
        "auto_contact": score >= 40,
    }
