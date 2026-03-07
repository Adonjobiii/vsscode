import math

MEDICAL_PREDEFINED_SKILLS = [
    "Biology", "Chemistry", "Anatomy", "Patient Care", "First Aid",
    "Clinical Research", "Surgical Assistance", "Diagnostics",
    "Medical Coding", "Pharmacology", "Psychology"
]

MEDICAL_PREDEFINED_INTERESTS = [
    "Helping People", "Human Body", "Public Health", "Genetics",
    "Mental Health", "Nutrition", "Sports Medicine", "Pediatrics"
]

MEDICAL_OPTIONAL_COURSES = [
    "Introduction to Human Anatomy",
    "Basic Clinical Skills",
    "Genetics and Genomics",
    "Public Health 101",
    "Medical Ethics",
    "Healthcare Administration",
    "Emergency Medicine Fundamentals",
    "Advanced Pharmacology"
]

MEDICAL_APTITUDE_CATEGORIES = [
    "Biology & Life Sciences",
    "Chemistry & Pharmaceuticals",
    "Anatomy & Physiology",
    "Clinical Reasoning"
]

medical_aptitude_course_map = {
    0: "General Medicine (MBBS)",
    1: "Pharmacy",
    2: "Surgery",
    3: "Nursing & Patient Care"
}

# Simple heuristic logic matching rules for Interests
def determine_medical_course(skills, interests):
    skills_lower = [s.lower() for s in skills]
    interests_lower = [i.lower() for i in interests]
    
    score_pharmacy = sum(1 for s in skills_lower if "chemistry" in s or "pharmacology" in s) + \
                     sum(1 for i in interests_lower if "genetics" in i or "nutrition" in i)
                     
    score_surgery = sum(1 for s in skills_lower if "anatomy" in s or "surgical" in s) + \
                    sum(1 for i in interests_lower if "human body" in i or "sports medicine" in i)
                    
    score_nursing = sum(1 for s in skills_lower if "patient care" in s or "first aid" in s) + \
                    sum(1 for i in interests_lower if "helping people" in i or "mental health" in i)
                    
    scores = {
        "Pharmacy": score_pharmacy,
        "Surgery": score_surgery,
        "Nursing & Patient Care": score_nursing,
        "General Medicine (MBBS)": 1 # baseline fallback
    }
    
    best_match = max(scores, key=scores.get)
    max_score = scores[best_match]
    
    # Calculate a pseudo-confidence percentage (just for UI)
    base_confidence = 65.0
    bonus = min(25.0, max_score * 8.5)
    confidence = base_confidence + bonus
    
    return {"course": best_match, "confidence": confidence}

# 12 Sample questions (3 per category)
MEDICAL_QUESTIONS = {
    "Biology & Life Sciences": [
        {
            "id": 101,
            "q": "Which cellular organelle is primarily responsible for energy production?",
            "options": {"a": "Nucleus", "b": "Mitochondria", "c": "Ribosome", "d": "Golgi apparatus"}
        },
        {
            "id": 102,
            "q": "What is the basic unit of heredity?",
            "options": {"a": "Gene", "b": "Protein", "c": "Cell", "d": "Tissue"}
        },
        {
            "id": 103,
            "q": "Which blood cells are responsible for transporting oxygen?",
            "options": {"a": "Leukocytes", "b": "Thrombocytes", "c": "Erythrocytes", "d": "Lymphocytes"}
        }
    ],
    "Chemistry & Pharmaceuticals": [
        {
            "id": 201,
            "q": "Which element is central to all organic compounds?",
            "options": {"a": "Oxygen", "b": "Nitrogen", "c": "Carbon", "d": "Hydrogen"}
        },
        {
            "id": 202,
            "q": "What is the normal pH of human blood?",
            "options": {"a": "7.0", "b": "7.2", "c": "7.4", "d": "7.6"}
        },
        {
            "id": 203,
            "q": "Which of these is considered an analgesic?",
            "options": {"a": "Penicillin", "b": "Ibuprofen", "c": "Insulin", "d": "Lisinopril"}
        }
    ],
    "Anatomy & Physiology": [
        {
            "id": 301,
            "q": "What is the longest bone in the human body?",
            "options": {"a": "Tibia", "b": "Humerus", "c": "Femur", "d": "Fibula"}
        },
        {
            "id": 302,
            "q": "Which organ produces bile?",
            "options": {"a": "Gallbladder", "b": "Pancreas", "c": "Liver", "d": "Stomach"}
        },
        {
            "id": 303,
            "q": "How many chambers does the human heart have?",
            "options": {"a": "2", "b": "3", "c": "4", "d": "5"}
        }
    ],
    "Clinical Reasoning": [
        {
            "id": 401,
            "q": "A patient presents with sudden weakness on one side of their face and arm. What is the most likely diagnosis?",
            "options": {"a": "Heart Attack", "b": "Stroke", "c": "Migraine", "d": "Seizure"}
        },
        {
            "id": 402,
            "q": "Which of the following describes 'tachycardia'?",
            "options": {"a": "Slow breathing", "b": "Fast heart rate", "c": "High blood pressure", "d": "Low body temperature"}
        },
        {
            "id": 403,
            "q": "If a patient is dehydrated, which intravenous fluid is most commonly administered?",
            "options": {"a": "0.9% Normal Saline", "b": "50% Dextrose", "c": "Packed Red Blood Cells", "d": "Epinephrine"}
        }
    ]
}

MEDICAL_CORRECT_ANSWERS = {
    "Biology & Life Sciences": {101: "b", 102: "a", 103: "c"},
    "Chemistry & Pharmaceuticals": {201: "c", 202: "c", 203: "b"},
    "Anatomy & Physiology": {301: "c", 302: "c", 303: "c"},
    "Clinical Reasoning": {401: "b", 402: "b", 403: "a"}
}
