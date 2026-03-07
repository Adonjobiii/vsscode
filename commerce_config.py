
# ─────────────────────────────────────────────────────────────────────────────
# Commerce Track Configuration & Recommendation Logic
# ─────────────────────────────────────────────────────────────────────────────

COMMERCE_PREDEFINED_SKILLS = [
    "Accounting", "Financial Analysis", "Investment Banking", "Economics", 
    "Taxation", "Audit", "Business Management", "Public Speaking", 
    "Mathematics", "Journalism", "Hospitality",
    "Equity Research", "Risk Assessment", "Portfolio Management", "Financial Modeling",
    "Data Analytics", "Corporate Governance", "Audit & Assurance", "Treasury Management",
    "Fund Management", "Actuarial Science", "Derivatives Trading", "Wealth Management"
]

COMMERCE_PREDEFINED_INTERESTS = [
    "Stock Market", "Entrepreneurship", "Banking", 
    "Politics", "Social Media", "Travel & Tourism", "Data Analytics",
    "Fintech", "Cryptocurrency", "Algorithmic Trading", "Venture Capital",
    "Private Equity", "Real Estate Investment", "Sustainable Finance", "Central Banking",
    "Microfinance", "Behavioral Economics", "Global Markets", "Insurance Tech"
]

COMMERCE_OPTIONAL_COURSES = [
    "Personal Finance 101",
    "Stock Market Trading Basics",
    "Advanced Accounting Standards",
    "Principles of Marketing",
    "Supply Chain Management Basics",
    "Digital Journalism",
    "Basic Hotel Management",
    "Investment Banking & Equity Research",
    "Fintech & Digital Transformation",
    "Mergers & Acquisitions (M&A)",
    "Risk Management & Financial Derivatives",
    "Chartered Financial Analyst (CFA) Prep",
    "Quantitative Finance & Excel modeling",
    "Asset & Wealth Management Strategies",
    "Corporate Finance for Managers",
    "Financial Statement Analysis Expert",
    "Commercial Banking Operations",
    "International Economics & Trade",
    "Insurance & Risk Underwriting",
    "E-Commerce & Digital Business",
    "Tax Planning & Wealth Preservation",
    "Strategic Management & Leadership",
    "Technical Analysis for Traders",
    "Forex & Currency Markets",
    "Sustainability & ESG Investing"
]

# User-provided thinking skills mapping
COURSES_THINKING_SKILLS = {
    "B.Com": {"Analytical Thinking": 25, "Numerical Ability": 30, "Logical Reasoning": 15, "Creativity": 5, "Communication": 15, "Problem Solving": 10},
    "BBA": {"Analytical Thinking": 20, "Numerical Ability": 15, "Logical Reasoning": 15, "Creativity": 15, "Communication": 25, "Problem Solving": 10},
    "CA (Chartered Accountant)": {"Analytical Thinking": 30, "Numerical Ability": 35, "Logical Reasoning": 20, "Creativity": 0, "Communication": 5, "Problem Solving": 10},
    "CS (Company Secretary)": {"Analytical Thinking": 20, "Numerical Ability": 20, "Logical Reasoning": 20, "Creativity": 5, "Communication": 25, "Problem Solving": 10},
    "CMA": {"Analytical Thinking": 30, "Numerical Ability": 35, "Logical Reasoning": 20, "Creativity": 0, "Communication": 5, "Problem Solving": 10},
    "BBA Finance": {"Analytical Thinking": 30, "Numerical Ability": 30, "Logical Reasoning": 15, "Creativity": 5, "Communication": 10, "Problem Solving": 10},
    "B.Com Accounting & Finance": {"Analytical Thinking": 30, "Numerical Ability": 35, "Logical Reasoning": 15, "Creativity": 0, "Communication": 10, "Problem Solving": 10},
    "BA Economics": {"Analytical Thinking": 35, "Numerical Ability": 30, "Logical Reasoning": 20, "Creativity": 0, "Communication": 5, "Problem Solving": 10},
    "BCA": {"Analytical Thinking": 25, "Numerical Ability": 20, "Logical Reasoning": 30, "Creativity": 5, "Communication": 5, "Problem Solving": 15},
    "BSc IT": {"Analytical Thinking": 25, "Numerical Ability": 20, "Logical Reasoning": 30, "Creativity": 5, "Communication": 5, "Problem Solving": 15},
    "BMS": {"Analytical Thinking": 20, "Numerical Ability": 15, "Logical Reasoning": 15, "Creativity": 15, "Communication": 25, "Problem Solving": 10},
    "BBM": {"Analytical Thinking": 20, "Numerical Ability": 15, "Logical Reasoning": 15, "Creativity": 15, "Communication": 25, "Problem Solving": 10},
    "BBA Business Analytics": {"Analytical Thinking": 35, "Numerical Ability": 30, "Logical Reasoning": 20, "Creativity": 0, "Communication": 5, "Problem Solving": 10},
    "B.Com Banking & Insurance": {"Analytical Thinking": 25, "Numerical Ability": 30, "Logical Reasoning": 20, "Creativity": 0, "Communication": 10, "Problem Solving": 15},
    "BFM (Financial Markets)": {"Analytical Thinking": 30, "Numerical Ability": 35, "Logical Reasoning": 20, "Creativity": 0, "Communication": 5, "Problem Solving": 10},
    "BBA Logistics & Supply Chain": {"Analytical Thinking": 25, "Numerical Ability": 20, "Logical Reasoning": 20, "Creativity": 5, "Communication": 10, "Problem Solving": 20}
}

def determine_commerce_course_by_aptitude(aptitude_scores):
    """
    Match aptitude scores to commerce fields based on required thinking skills percentage.
    aptitude_scores: dict { skill_name: score_percentage }
    """
    field_match_scores = {}
    
    for course, requirements in COURSES_THINKING_SKILLS.items():
        match_score = 0
        total_weight = sum(requirements.values())
        if total_weight == 0: continue
        
        for skill, weight in requirements.items():
            user_score = aptitude_scores.get(skill, 0)
            # Each skill contributes to the match weighted by its importance
            match_score += (user_score * (weight / total_weight))
            
        field_match_scores[course] = match_score
        
    best_match = max(field_match_scores, key=field_match_scores.get)
    # probabilities for charts
    total_match = sum(field_match_scores.values()) or 1
    probabilities = {k: (v / total_match) * 100 for k, v in field_match_scores.items()}
    # Filter to top 5 for cleaner chart
    top_probabilities = dict(sorted(probabilities.items(), key=lambda x: x[1], reverse=True)[:5])

    return {
        "recommended_stream": best_match,
        "probabilities": top_probabilities,
        "all_scores": field_match_scores,
        "confidence": field_match_scores[best_match]
    }

def determine_commerce_interests(skills, interests):
    """Interest-based heuristic for commerce tracks."""
    skills_lower = [s.lower() for s in skills]
    interests_lower = [i.lower() for i in interests]
    
    # Generic mapping
    mapping = {
        "Banking & Finance": ["banking", "stock", "investing", "financial"],
        "Business Management": ["management", "bba", "entrepreneurship", "leadership"],
        "Accounting & Audit": ["audit", "tax", "accounting", "company secretary"],
        "Travel & Hospitality": ["tourism", "hotel", "hospitality", "travel"],
        "Information Tech (Commerce)": ["data analytics", "bca", "bsc it", "business analytics"]
    }
    
    scores = {k: 0 for k in mapping}
    for category, keywords in mapping.items():
        for k in keywords:
            if any(k in s for s in skills_lower): scores[category] += 1
            if any(k in i for i in interests_lower): scores[category] += 1
            
    best_match = max(scores, key=scores.get) if any(scores.values()) else "B.Com General"
    confidence = min(95.0, 60.0 + (scores.get(best_match, 0) * 10))
    
    return {"course": best_match, "confidence": confidence}
