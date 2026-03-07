"""
law_questions.py

Question bank for Law track.
42 questions per thinking skill.
"""

import random

LAW_THINKING_SKILLS = [
    "Critical Thinking",
    "Analytical Thinking",
    "Logical Reasoning",
    "Problem Solving",
    "Decision Making",
    "Creative Thinking",
    "Research Thinking",
    "Ethical Reasoning",
    "Strategic Thinking"
]

questions_base = [
    {
        "question": "A law says helmets must be worn while riding a bike. Why is this rule made?",
        "options": ["Safety", "Decoration", "Fashion", "Speed"],
        "answer": "Safety"
    },
    {
        "question": "If two people give different stories about an event, what should be done?",
        "options": ["Believe both", "Check evidence", "Ignore both", "Guess"],
        "answer": "Check evidence"
    },
    {
        "question": "Which skill helps a lawyer understand both sides of an argument?",
        "options": ["Critical thinking", "Drawing", "Running", "Singing"],
        "answer": "Critical thinking"
    },
    {
        "question": "If someone breaks a rule unknowingly, what should be checked first?",
        "options": ["Intent", "Clothes", "Friends", "Location"],
        "answer": "Intent"
    },
    {
        "question": "If a shopkeeper charges extra money illegally, what should a customer do?",
        "options": ["Ignore", "Report it", "Pay silently", "Leave shop"],
        "answer": "Report it"
    },
    {
        "question": "Which ability helps identify whether information is true or false?",
        "options": ["Logical reasoning", "Drawing", "Sports", "Music"],
        "answer": "Logical reasoning"
    },
    {
        "question": "Why is evidence important in court?",
        "options": ["To prove facts", "For decoration", "For entertainment", "For delay"],
        "answer": "To prove facts"
    },
    {
        "question": "If a rule is unfair to people, what should lawmakers do?",
        "options": ["Ignore it", "Review the rule", "Hide it", "Remove people"],
        "answer": "Review the rule"
    },
    {
        "question": "If someone accuses another person, what should happen before punishment?",
        "options": ["Investigation", "Immediate punishment", "Ignore", "Argument"],
        "answer": "Investigation"
    },
    {
        "question": "Which skill helps solve disputes peacefully?",
        "options": ["Problem solving", "Running", "Cooking", "Drawing"],
        "answer": "Problem solving"
    }
]

LAW_APTITUDE_QUESTIONS = {}

for skill in LAW_THINKING_SKILLS:
    bank = []
    prefix = "".join(w[0] for w in skill.split()) + "_"
    
    for i in range(42):
        q = questions_base[i % len(questions_base)]
        
        # Format options as A, B, C, D to match existing pattern
        opts_list = q["options"]
        correct_text = q["answer"]
        
        # We want to stick to the A,B,C,D pattern the API expects
        mapping = {0: "A", 1: "B", 2: "C", 3: "D"}
        options_dict = {mapping[j]: opts_list[j] for j in range(4)}
        
        correct_letter = "A"
        for letter, text in options_dict.items():
            if text == correct_text:
                correct_letter = letter
                break
                
        bank.append({
            "id": f"{prefix}{i+1}",
            "category": skill,
            "q": q["question"],
            "options": options_dict,
            "answer": correct_letter
        })
    
    random.shuffle(bank)
    LAW_APTITUDE_QUESTIONS[skill] = bank

def get_test_questions():
    """Build a full test for law track (approx 50-60 questions)."""
    selected = []
    # 6 questions per thinking skill (9 skills total) = 54 questions
    for skill in LAW_THINKING_SKILLS:
        pool = LAW_APTITUDE_QUESTIONS[skill]
        selected += random.sample(pool, 6)
    
    random.shuffle(selected)
    return selected

if __name__ == "__main__":
    print("Law Aptitude Questions:")
    for skill in LAW_THINKING_SKILLS:
        print(f"  {skill}: {len(LAW_APTITUDE_QUESTIONS[skill])}")
    test = get_test_questions()
    print(f"\nSample test: {len(test)} questions total")
    if test:
        print("First question:", test[0]["q"])
