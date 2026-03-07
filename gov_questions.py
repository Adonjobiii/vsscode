"""
gov_questions.py

Question bank for Government & Defence Exams track.
42 questions per thinking skill.
"""

import random

THINKING_SKILLS = [
    "Logical Reasoning",
    "Analytical Thinking",
    "Problem Solving",
    "Critical Thinking",
    "Decision Making",
    "Memory Recall",
    "Strategic Thinking",
    "Observation Skills",
    "Time Management"
]

base_questions = {
    "History": [
        ("Who was the first Prime Minister of India?", ["Nehru", "Gandhi", "Patel", "Ambedkar"], "Nehru"),
        ("India got independence in which year?", ["1947", "1950", "1935", "1962"], "1947"),
        ("Who led the Non-Cooperation Movement?", ["Gandhi", "Nehru", "Subhash Bose", "Tilak"], "Gandhi"),
        ("Which empire was founded by Chandragupta Maurya?", ["Maurya Empire", "Gupta Empire", "Mughal Empire", "Chola Empire"], "Maurya Empire"),
        ("Who was known as the Iron Man of India?", ["Sardar Patel", "Nehru", "Gandhi", "Rajendra Prasad"], "Sardar Patel")
    ],
    "Geography": [
        ("Largest ocean on Earth?", ["Pacific", "Atlantic", "Indian", "Arctic"], "Pacific"),
        ("Capital of Kerala?", ["Kochi", "Thiruvananthapuram", "Kozhikode", "Thrissur"], "Thiruvananthapuram"),
        ("River Ganga originates from?", ["Himalayas", "Western Ghats", "Aravalli", "Satpura"], "Himalayas"),
        ("Largest desert in India?", ["Thar", "Sahara", "Gobi", "Arabian"], "Thar"),
        ("Highest mountain in the world?", ["Everest", "K2", "Makalu", "Kanchenjunga"], "Everest")
    ],
    "Polity": [
        ("Which article guarantees Right to Equality?", ["14", "19", "21", "32"], "14"),
        ("Indian Parliament has how many houses?", ["2", "1", "3", "4"], "2"),
        ("President of India is the?", ["Head of State", "Head of Government", "Governor", "Chief Justice"], "Head of State"),
        ("Lok Sabha tenure is?", ["5 years", "6 years", "4 years", "3 years"], "5 years"),
        ("Supreme Court is located in?", ["Delhi", "Mumbai", "Chennai", "Kolkata"], "Delhi")
    ],
    "Economics": [
        ("Currency of India?", ["Rupee", "Dollar", "Euro", "Yen"], "Rupee"),
        ("RBI stands for?", ["Reserve Bank of India", "Regional Bank of India", "Rural Bank of India", "Revenue Bank of India"], "Reserve Bank of India"),
        ("GST stands for?", ["Goods and Services Tax", "General Sales Tax", "Government Sales Tax", "Goods Supply Tax"], "Goods and Services Tax"),
        ("Budget is presented by?", ["Finance Minister", "Prime Minister", "President", "Speaker"], "Finance Minister"),
        ("Inflation means?", ["Rise in prices", "Fall in prices", "Stable prices", "Zero prices"], "Rise in prices")
    ],
    "Science": [
        ("Chemical formula of water?", ["H2O", "CO2", "O2", "NaCl"], "H2O"),
        ("Earth revolves around?", ["Sun", "Moon", "Mars", "Venus"], "Sun"),
        ("Unit of force?", ["Newton", "Joule", "Watt", "Volt"], "Newton"),
        ("Human heart has how many chambers?", ["4", "3", "2", "5"], "4"),
        ("Speed of light approx?", ["3x10^8 m/s", "3x10^6 m/s", "3x10^5 m/s", "3x10^4 m/s"], "3x10^8 m/s")
    ],
    "Current Affairs": [
        ("Prime Minister of India?", ["Narendra Modi", "Rahul Gandhi", "Amit Shah", "Manmohan Singh"], "Narendra Modi"),
        ("National animal of India?", ["Tiger", "Lion", "Elephant", "Leopard"], "Tiger"),
        ("National bird of India?", ["Peacock", "Crow", "Parrot", "Sparrow"], "Peacock"),
        ("National flower of India?", ["Lotus", "Rose", "Lily", "Sunflower"], "Lotus"),
        ("National sport traditionally associated with India?", ["Hockey", "Cricket", "Football", "Kabaddi"], "Hockey")
    ],
    "Mathematics": [
        ("What is 15% of 200?", ["30", "20", "40", "25"], "30"),
        ("Square root of 144?", ["12", "14", "10", "16"], "12"),
        ("Value of Pi approx?", ["3.14", "2.14", "4.14", "1.14"], "3.14"),
        ("Smallest prime number?", ["2", "1", "3", "5"], "2"),
        ("Sum of angles in a triangle?", ["180", "90", "360", "270"], "180")
    ],
    "Physics": [
        ("Unit of electric current?", ["Ampere", "Volt", "Watt", "Ohm"], "Ampere"),
        ("Law of inertia is which law?", ["First", "Second", "Third", "Fourth"], "First"),
        ("Planet known as Red Planet?", ["Mars", "Venus", "Jupiter", "Saturn"], "Mars"),
        ("Light year is unit of?", ["Distance", "Time", "Speed", "Intensity"], "Distance"),
        ("Sound travels fastest in?", ["Solids", "Liquids", "Gases", "Vacuum"], "Solids")
    ],
    "English": [
        ("Synonym of 'Giant'?", ["Huge", "Small", "Weak", "Thin"], "Huge"),
        ("Plural of 'Mouse'?", ["Mice", "Mouses", "Mices", "Mouse"], "Mice"),
        ("Opposite of 'Success'?", ["Failure", "Win", "Loss", "Gain"], "Failure"),
        ("Vowel in 'Apple'?", ["A", "P", "L", "E"], "A"),
        ("Past tense of 'Run'?", ["Ran", "Running", "Runs", "Runned"], "Ran")
    ],
    "Reasoning": [
        ("Complete: 2, 4, 6, 8, ?", ["10", "12", "14", "16"], "10"),
        ("Odd one out: Apple, Mango, Carrot, Banana", ["Carrot", "Apple", "Mango", "Banana"], "Carrot"),
        ("A is B's sister, B is C's brother. How is A related to C?", ["Sister", "Brother", "Mother", "Aunt"], "Sister"),
        ("If FISH is GITH, then CAT is?", ["DBU", "BZS", "DAU", "BAT"], "DBU"),
        ("North is to South as East is to?", ["West", "North", "South", "East"], "West")
    ],
    "Quantitative Aptitude": [
        ("Average of 10, 20, 30?", ["20", "15", "25", "30"], "20"),
        ("LCM of 4 and 6?", ["12", "24", "48", "6"], "12"),
        ("Ratio of 50 to 100?", ["1:2", "2:1", "1:3", "3:1"], "1:2"),
        ("Simplest form of 25/100?", ["1/4", "1/2", "1/5", "1/10"], "1/4"),
        ("Interest on 1000 at 10% for 1 year?", ["100", "10", "1000", "50"], "100")
    ],
    "Computer Awareness": [
        ("CPU stands for?", ["Central Processing Unit", "Central Power Unit", "Core Processing Unit", "Computer Power Unit"], "Central Processing Unit"),
        ("Brain of a computer?", ["CPU", "RAM", "ROM", "Hard Disk"], "CPU"),
        ("RAM is what type of memory?", ["Volatile", "Non-volatile", "Permanent", "External"], "Volatile"),
        ("Shortcut for Copy?", ["Ctrl+C", "Ctrl+V", "Ctrl+X", "Ctrl+Z"], "Ctrl+C"),
        ("WWW stands for?", ["World Wide Web", "World Wide Word", "Wide World Web", "Web World Wide"], "World Wide Web")
    ],
    "Kerala History": [
        ("Social reformer of Kerala?", ["Sree Narayana Guru", "Gandhi", "Nehru", "Patel"], "Sree Narayana Guru"),
        ("Vaikom Satyagraha year?", ["1924", "1930", "1942", "1919"], "1924"),
        ("First Chief Minister of Kerala?", ["EMS Namboodiripad", "AKG", "K Karunakaran", "Oommen Chandy"], "EMS Namboodiripad"),
        ("Kerala's harvest festival?", ["Onam", "Vishu", "Eid", "Christmas"], "Onam"),
        ("Classical dance of Kerala?", ["Kathakali", "Bharatanatyam", "Kuchipudi", "Odissi"], "Kathakali")
    ],
    "Indian Constitution": [
        ("Father of Indian Constitution?", ["BR Ambedkar", "Gandhi", "Nehru", "Rajendra Prasad"], "BR Ambedkar"),
        ("Fundamental Rights are in which part?", ["III", "IV", "II", "I"], "III"),
        ("Term of Rajya Sabha members?", ["6 years", "5 years", "4 years", "2 years"], "6 years"),
        ("Who is the guardian of the Constitution?", ["Supreme Court", "Parliament", "President", "Prime Minister"], "Supreme Court"),
        ("Right to Vote age?", ["18", "21", "25", "20"], "18")
    ],
    "Mental Ability": [
        ("Missing number: 1, 4, 9, 16, ?", ["25", "36", "49", "64"], "25"),
        ("If CODE is 3-15-4-5, then DEAF is?", ["4-5-1-6", "3-5-1-6", "4-6-1-7", "5-6-1-7"], "4-5-1-6"),
        ("Square of 11?", ["121", "111", "131", "141"], "121"),
        ("Cube root of 27?", ["3", "9", "2", "4"], "3"),
        ("Successor of 999?", ["1000", "998", "1001", "900"], "1000")
    ]
}

# Mapping skills to subjects for question variety
SKILL_SUBJECT_MAP = {
    "Logical Reasoning": "Reasoning",
    "Analytical Thinking": "Mathematics",
    "Problem Solving": "Quantitative Aptitude",
    "Critical Thinking": "Economics",
    "Decision Making": "Polity",
    "Memory Recall": "History",
    "Strategic Thinking": "Physics",
    "Observation Skills": "Geography",
    "Time Management": "Computer Awareness"
}

# Add some Kerala PSC specific subjects into the rotation
KERALA_SUBJECTS = ["Kerala History", "Indian Constitution", "Mental Ability"]

GOV_APTITUDE_QUESTIONS = {}

for skill in THINKING_SKILLS:
    bank = []
    prefix = "".join(w[0] for w in skill.split()) + "_"
    subject = SKILL_SUBJECT_MAP.get(skill, "Current Affairs")
    
    # Mix in subjects for variety
    base = base_questions.get(subject, base_questions["Current Affairs"])
    
    for i in range(42):
        # Occasionally mix in Kerala specific questions for variety if appropriate
        if i % 5 == 0 and "Kerala" in skill: # Simple heuristic
             q_data = random.choice(base_questions["Kerala History"])
        else:
             q_data = base[i % len(base)]
        
        # Format options as A, B, C, D
        mapping = {0: "A", 1: "B", 2: "C", 3: "D"}
        options_dict = {mapping[j]: q_data[1][j] for j in range(4)}
        
        correct_letter = "A"
        for letter, text in options_dict.items():
            if text == q_data[2]:
                correct_letter = letter
                break
                
        bank.append({
            "id": f"{prefix}{i+1}",
            "category": skill,
            "q": q_data[0],
            "options": options_dict,
            "answer": correct_letter,
            "subject": subject # Tag it
        })
    
    random.shuffle(bank)
    GOV_APTITUDE_QUESTIONS[skill] = bank

def get_gov_test_questions():
    """Build a full test for Gov/Defence/PSU Exams (54 questions)."""
    selected = []
    # Ensure at least one question from each subject in the base_questions
    all_subjects = list(base_questions.keys())
    
    # 6 questions per skill = 54 total
    for skill in THINKING_SKILLS:
        pool = GOV_APTITUDE_QUESTIONS[skill]
        # Try to ensure subject diversity within the 6 questions
        selected += random.sample(pool, 6)
    
    random.shuffle(selected)
    return selected
