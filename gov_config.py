"""
gov_config.py

Configuration for Government & Defence track.
"""

GOV_PREDEFINED_SKILLS = [
    "Public Administration", "Constitutional Law", "Current affairs knowledge",
    "General Science", "Quantitative Aptitude", "Physical Fitness",
    "Discipline", "Situational Awareness", "Crisis Management"
]

GOV_PREDEFINED_INTERESTS = [
    "National Security", "Public Service", "Governance", "Indian History",
    "International Relations", "Aviation", "Maritime Affairs", "Law Enforcement",
    "Social Welfare"
]

GOV_OPTIONAL_COURSES = [
    "Ethics & Integrity in Governance",
    "Advanced SSB Preparation",
    "Disaster Management",
    "Intelligence & Espionage Basics",
    "Public Policy Analysis"
]

def determine_gov_interests(hobbies, priority_list):
    """Simple logic to decide dominant gov stream from priorities."""
    priority_str = " ".join(priority_list).lower()
    
    if any(x in priority_str for x in ["defence", "army", "navy", "air force", "nda", "cds"]):
        return "Defence"
    if any(x in priority_str for x in ["upsc", "ias", "ips", "civil services"]):
        return "Civil Services"
    return "State/Central Gov"
