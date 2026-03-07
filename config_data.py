import os
import pymongo
from collections import defaultdict
import numpy as np

ENG_STREAMS = [
    "Computer Science (CSE)", "Information Technology (IT)", "Electronics & Communication (ECE)",
    "Electrical & Electronics (EEE)", "Mechanical Engineering (ME)", "Civil Engineering (CE)",
    "Aerospace Engineering", "Chemical Engineering (CH)", "Biotechnology", "Industrial Engineering"
]

BROAD_INTERESTS = [
    "Technology & Coding", "Mechanics & Machines", "Structures & Construction",
    "Electronics & Gadgets", "Chemistry & Biology", "Space & Aviation",
    "Management & Business", "Design & Creativity", "Mathematics & Physics"
]

PREDEFINED_SKILLS = [
    "Python Programming", "Java / C++", "Web Development", "Data Analysis",
    "Machine Learning", "CAD / 3D Modeling", "Circuit Design", "Project Management",
    "Public Speaking", "Creative Writing", "Robotics", "Graphic Design",
    "Cloud Computing", "UI/UX Design", "Content Creation", "Digital Marketing",
    "Leadership", "SQL & Databases", "App Development", "Blockchain",
    "Financial Modeling", "Game Design", "Animation", "Editing & Proofreading"
]

PREDEFINED_INTERESTS = [
    "Artificial Intelligence", "Game Development", "Renewable Energy", "Automotive",
    "Healthcare Tech", "Space Exploration", "Financial Markets", "Cybersecurity",
    "Digital Art", "Entrepreneurship", "Quantum Computing", "AR / VR", 
    "Sustainable Agriculture", "Social Media Trends", "E-sports", "Investing & Trading", 
    "Psychology & Behavior", "History & Culture", "Photography", "Music Production"
]

OPTIONAL_COURSES = [
    "AI & Data Science Fundamentals", "Advanced Web Architecture", "Robotics & Automation",
    "Sustainable Energy Systems", "Cybersecurity & Ethical Hacking", "Financial Engineering",
    "Digital Marketing & SEO", "UX/UI Design Principles", "Bioinformatics Fundamentals",
    "Blockchain and Cryptography", "Game Engineering Masterclass", "Cloud Infrastructure (AWS/Azure)",
    "Product Management 101", "3D Animation & Modeling", "Intro to Quantum Mechanics",
    "Behavioral Economics", "Machine Learning for Healthcare", "Advanced App Development"
]

# Medical & Commerce Specifics (Missing in previous modularization)
MEDICAL_OPTIONAL_COURSES = [
    "Introduction to Molecular Biology", "Human Physiology Advanced", "Clinical Research Ethics",
    "Medical Coding and Scribing", "Pharmacology Basics", "Health Informatics"
]

COMMERCE_OPTIONAL_COURSES = [
    "Stock Market Investment", "Advanced Excel for Finance", "Corporate Law Basics",
    "GST and Taxation", "Audit and Assurance", "Banking Operations"
]

# Predefined Skills & Interests for Other Tracks
MEDICAL_PREDEFINED_SKILLS = ["Biochemistry", "Clinical Observation", "Patient Care", "Laboratory Techniques"]
MEDICAL_PREDEFINED_INTERESTS = ["Anatomy", "Genetics", "Neuroscience", "Public Health"]

COMMERCE_PREDEFINED_SKILLS = ["Tally / ERP", "Financial Accounting", "Tax Planning", "Business Strategy"]
COMMERCE_PREDEFINED_INTERESTS = ["Investment Banking", "Mutual Funds", "FinTech", "Economic Policy"]

LAW_PREDEFINED_SKILLS = ["Legal Research", "Argument Construction", "Public Speaking", "Negotiation"]
LAW_PREDEFINED_INTERESTS = ["Criminal Justice", "Civil Rights", "Judiciary", "Human Rights"]

ENGINEERING_TASKS = {
    "Designing software algorithms and coding applications": ["CS", "IT"],
    "Developing mobile or web applications": ["CS", "IT"],
    "Building and programming robots": ["EC", "EE", "CS"],
    "Designing or troubleshooting electronic circuits": ["EC", "EE"],
    "Working with microprocessors and communication systems": ["EC", "IT"],
    "Designing and testing car engines or mechanical parts": ["ME", "AE"],
    "Understanding fluid dynamics and thermodynamics": ["ME", "CH"],
    "Planning and designing large structures like bridges or buildings": ["CE"],
    "Working with construction materials and surveying": ["CE"],
    "Experimenting with chemical reactions and industrial processes": ["CH", "ME"],
    "Studying DNA, genetics, or biological systems": ["BT"],
    "Analyzing system efficiency, supply chains, and logistics": ["IE"],
    "Designing aircraft, spacecraft, or propulsion systems": ["AE", "ME"],
    "Learning about renewable energy systems and power grids": ["EE", "ME"]
}

career_course_map = {i: stream for i, stream in enumerate(ENG_STREAMS)}
aptitude_course_map = career_course_map 

APTITUDE_MODEL_CATEGORIES = [
    "Algorithmic", "Computational", "Logical", "System", 
    "Critical", "Abstract", "Creative"
]

DUMMY_QUESTIONS = defaultdict(list)
DUMMY_CORRECT_ANSWERS = defaultdict(dict)
for cat in APTITUDE_MODEL_CATEGORIES:
    for i in range(10):
        DUMMY_QUESTIONS[cat].append({
            "id": i,
            "q": f"Mock Question {i+1} testing your {cat} skills. Which is correct?",
            "options": {"A": "Option A (Correct)", "B": "Option B", "C": "Option C", "D": "Option D"}
        })
        DUMMY_CORRECT_ANSWERS[cat][i] = "A"

# Mock training data
X_data_train_aptitude = np.random.rand(8, len(APTITUDE_MODEL_CATEGORIES))
y_labels_train_aptitude = [0, 1, 2, 3, 4, 5, 0, 1]
# Updated to 14 features to match the revised 14 ENGINEERING_TASKS
X_data_train_career = np.random.rand(20, 14)
y_labels_train_career = np.random.randint(0, 10, 20)
MONGODB_TIMEOUT_MS = 5000

# ===============================
# MongoDB Configuration
# ===============================
_mongo_client = None
db = None
users_collection = None
MONGO_PASS = os.getenv("MONGO_PASSWORD", "anoop123")
CONNECTION_STRING = f"mongodb+srv://anoop:{MONGO_PASS}@cluster0.rd6nzal.mongodb.net/CareerAssessmentDB?retryWrites=true&w=majority"

def get_mongodb_connection():
    global _mongo_client, db, users_collection
    if _mongo_client is None:
        mongo_pass = os.getenv("MONGO_PASSWORD", "anoop123")
        uri = f"mongodb+srv://anoop:{mongo_pass}@cluster0.rd6nzal.mongodb.net/CareerAssessmentDB?retryWrites=true&w=majority"
        try:
            _mongo_client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=MONGODB_TIMEOUT_MS)
            db = _mongo_client.get_database()
            # Note: We'll use specific collections in specific apps/modules
            users_collection = db["users"]
            assessment_history = db["assessment_history"]
            print("\n[DB] MongoDB Atlas connection: SUCCESSFUL")
        except Exception as e:
            print(f"[DB] MongoDB connection failed: {e}")
            _mongo_client = None
    return _mongo_client, db

# Initialize once at module level for shared use
_client, _db = get_mongodb_connection()
if _db is not None:
    users_collection = _db["users"]
    personality_collection = _db["Personality"]
    assessment_history = _db["assessment_history"]

# ---------------- THEME & STYLING ----------------
COLOR_BG_SIDEBAR = "#2C3E50"
COLOR_BG_MAIN = "#F8F9FA"
COLOR_PRIMARY = "#3498DB"
COLOR_SUCCESS = "#2ECC71"
COLOR_TEXT_MAIN = "#2C3E50"
COLOR_WHITE = "#FFFFFF"

# ---------------- DATA & FACET MAPPING ----------------
TRAITS = {
    'O': {"name": "Openness", "color": "#3498db"},
    'C': {"name": "Conscientiousness", "color": "#2ecc71"},
    'E': {"name": "Extraversion", "color": "#f1c40f"},
    'A': {"name": "Agreeableness", "color": "#9b59b6"},
    'N': {"name": "Neuroticism", "color": "#e74c3c"},
}

# Sub-trait mapping as per BFI-44 scoring guidelines
FACET_MAP = {
    1: 'Sociability', 6: 'Sociability', 21: 'Sociability', 36: 'Sociability',
    26: 'Assertiveness', 31: 'Assertiveness', 11: 'Energy', 16: 'Energy',
    2: 'Compliance', 12: 'Compliance', 37: 'Compliance', 7: 'Altruism', 
    17: 'Altruism', 32: 'Altruism', 22: 'Trust', 27: 'Trust', 42: 'Trust',
    3: 'Achievement', 13: 'Achievement', 28: 'Achievement', 38: 'Achievement',
    8: 'Order', 18: 'Order', 33: 'Order', 23: 'Dutifulness', 43: 'Dutifulness',
    4: 'Anxiety', 14: 'Anxiety', 19: 'Anxiety', 39: 'Anxiety',
    9: 'Stability', 24: 'Stability', 34: 'Stability', 29: 'Moodiness',
    5: 'Imagination', 15: 'Imagination', 20: 'Imagination', 25: 'Imagination',
    30: 'Artistic', 41: 'Artistic', 44: 'Artistic', 10: 'Curiosity', 
    35: 'Curiosity', 40: 'Curiosity'
}

QUESTIONNAIRE = {
    1:['E',"Is talkative.",False], 2:['A',"Tends to find fault with others.",True],
    3:['C',"Does a thorough job.",False], 4:['N',"Is depressed, blue.",False],
    5:['O',"Is original, comes up with new ideas.",False], 6:['E',"Is reserved.",True],
    7:['A',"Is helpful and unselfish with others.",False], 8:['C',"Can be somewhat careless.",True],
    9:['N',"Is relaxed, handles stress well.",True], 10:['O',"Is curious about many different things.",False],
    11:['E',"Is full of energy.",False], 12:['A',"Starts quarrels with others.",True],
    13:['C',"Is a reliable worker.",False], 14:['N',"Can be tense.",False],
    15:['O',"Is ingenious, a deep thinker.",False], 16:['E',"Generates a lot of enthusiasm.",False],
    17:['A',"Has a forgiving nature.",False], 18:['C',"Tends to be disorganized.",True],
    19:['N',"Worries a lot.",False], 20:['O',"Has an active imagination.",False],
    21:['E',"Tends to be quiet.",True], 22:['A',"Is generally trusting.",False],
    23:['C',"Tends to be lazy.",True], 24:['N',"Is emotionally stable, not easily upset.",True],
    25:['O',"Is inventive.",False], 26:['E',"Has an assertive personality.",False],
    27:['A',"Can be cold and aloof.",True], 28:['C',"Perseveres until the task is finished.",False],
    29:['N',"Can be moody.",False], 30:['O',"Values artistic experiences.",False],
    31:['E',"Is sometimes shy, inhibited.",True], 32:['A',"Is considerate and kind.",False],
    33:['C',"Does things efficiently.",False], 34:['N',"Remains calm in tense situations.",True],
    35:['O',"Prefers routine work.",True], 36:['E',"Is outgoing, sociable.",False],
    37:['A',"Is sometimes rude.",True], 38:['C',"Makes plans and follows through.",False],
    39:['N',"Gets nervous easily.",False], 40:['O',"Likes to reflect, play with ideas.",False],
    41:['O',"Has few artistic interests.",True], 42:['A',"Likes to cooperate.",False],
    43:['C',"Is easily distracted.",True], 44:['O',"Is sophisticated in art, music, literature.",False],
}

# PersonalityAssessmentApp class moved to personality_gui.py
