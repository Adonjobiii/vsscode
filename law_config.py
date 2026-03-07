"""
law_config.py
"""

LAW_PREDEFINED_SKILLS = [
    "Logical Reasoning", "Legal Research", "Argument Construction", 
    "Public Speaking", "Writing & Documentation", "Negotiation",
    "Evidence Analysis", "Case Study Analysis", "Ethics & Integrity"
]

LAW_PREDEFINED_INTERESTS = [
    "Criminal Justice", "Corporate Law", "Civil Rights", 
    "Intellectual Property", "International Law", "Environmental Law",
    "Judiciary", "Human Rights", "Public Policy", "Alternative Dispute Resolution"
]

LAW_OPTIONAL_COURSES = [
    "Constitutional Law Basics",
    "Legal Drafting & Conveyancing",
    "Introduction to Criminal Law",
    "Torts and Civil Liability",
    "Corporate Governance & Compliance",
    "Intellectual Property Rights 101",
    "Family Law & Personal Statutes",
    "International Human Rights Law",
    "Environmental Regulations & Policy",
    "Mediation & Arbitration Skills"
]

def determine_law_interests(skills, interests):
    """Interest-based heuristic for law tracks."""
    skills_lower = [s.lower() for s in skills]
    interests_lower = [i.lower() for i in interests]
    
    mapping = {
        "Litigation & Advocacy": ["criminal", "civil rights", "public speaking", "judiciary", "court"],
        "Corporate Law": ["corporate", "intellectual", "business", "tax", "contract", "mergers"],
        "Legal Research & Academia": ["research", "policy", "documentation", "international", "human rights", "environmental"],
    }
    
    scores = {k: 0 for k in mapping}
    for category, keywords in mapping.items():
        for k in keywords:
            if any(k in s for s in skills_lower): scores[category] += 1
            if any(k in i for i in interests_lower): scores[category] += 1
            
    best_match = max(scores, key=scores.get) if any(scores.values()) else "BA LLB (General)"
    confidence = min(95.0, 60.0 + (scores.get(best_match, 0) * 10))
    
    return {"course": best_match, "confidence": confidence}
