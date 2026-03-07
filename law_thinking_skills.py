"""
law_thinking_skills.py

Module: Law Thinking Skills Distribution
Description: Stores approximate thinking skill distribution for different legal fields 
and provides utilities to analyze the data.
"""

law_thinking_skills = {
    "General Law": {
        "Critical Thinking": 20,
        "Analytical Thinking": 18,
        "Logical Reasoning": 15,
        "Problem Solving": 12,
        "Decision Making": 10,
        "Creative Thinking": 8,
        "Research Thinking": 7,
        "Ethical Reasoning": 5,
        "Strategic Thinking": 5
    }
}

def get_skills_for_stream(stream_name):
    """Returns thinking skill distribution for a given law stream."""
    return law_thinking_skills.get(stream_name, {})

def get_all_streams():
    """Returns list of all law streams."""
    return list(law_thinking_skills.keys())

def dominant_skill(stream_name):
    """Returns the most dominant thinking skill for a given stream."""
    skills = law_thinking_skills.get(stream_name)
    if not skills:
        return "Stream not found"
    return max(skills, key=skills.get)

if __name__ == "__main__":
    print("Thinking Skills Required for Litigation & Advocacy:\n")
    skills = get_skills_for_stream("Litigation & Advocacy")
    for skill, percentage in skills.items():
        print(f"{skill} : {percentage}%")
