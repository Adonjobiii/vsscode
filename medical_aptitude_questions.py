"""
medical_aptitude_questions.py

Aptitude question bank based on thinking skills required
in medical and healthcare fields.
Each section contains 28 questions. The endpoint picks 7 per section per test.
"""

import random

# ─────────────────────────────────────────────
# RAW QUESTION DATA  (7 hand-crafted per skill)
# ─────────────────────────────────────────────

_raw = {

    "Critical Thinking": [
        {
            "q": "A patient has fever, cough, and body pain. Which step should a doctor take first?",
            "options": {"A": "Give random medicine", "B": "Analyze symptoms and medical history",
                        "C": "Ignore the symptoms", "D": "Perform surgery"}, "answer": "B"
        },
        {
            "q": "A medicine relieves pain but causes severe stomach irritation. What should be done?",
            "options": {"A": "Continue using without thinking", "B": "Analyze benefits vs risks",
                        "C": "Ignore side effects", "D": "Increase dosage"}, "answer": "B"
        },
        {
            "q": "A report shows abnormal blood sugar levels. What is the best first response?",
            "options": {"A": "Ignore the result", "B": "Evaluate patient diet and medical history",
                        "C": "Prescribe random medicine", "D": "Repeat the same test many times"}, "answer": "B"
        },
        {
            "q": "Which action best demonstrates critical thinking in healthcare?",
            "options": {"A": "Following instructions blindly", "B": "Evaluating evidence before decisions",
                        "C": "Ignoring patient history", "D": "Making random decisions"}, "answer": "B"
        },
        {
            "q": "A patient complains of headache daily. What should a clinician investigate first?",
            "options": {"A": "Immediately give strong medicine", "B": "Investigate possible underlying causes",
                        "C": "Ignore complaint", "D": "Refer for surgery"}, "answer": "B"
        },
        {
            "q": "Two studies on the same drug give conflicting results. What should a doctor do?",
            "options": {"A": "Use the older study only", "B": "Review both studies critically for methodology flaws",
                        "C": "Ignore both studies", "D": "Randomly choose one"}, "answer": "B"
        },
        {
            "q": "A nurse notices a patient's condition has suddenly changed. What is the priority action?",
            "options": {"A": "Wait for the next scheduled check", "B": "Assess the patient immediately and alert the doctor",
                        "C": "Chart the observation and do nothing", "D": "Administer the usual medication"}, "answer": "B"
        },
    ],

    "Analytical Thinking": [
        {
            "q": "A patient gains 5 kg in one week with swollen ankles. What condition is most likely?",
            "options": {"A": "Overeating", "B": "Fluid retention due to heart or kidney issue",
                        "C": "Bone growth", "D": "Muscle gain"}, "answer": "B"
        },
        {
            "q": "In a clinical trial, Group A improved 80% vs Group B 40%. What can be concluded?",
            "options": {"A": "Group B treatment is better", "B": "Group A treatment is more effective in this trial",
                        "C": "No difference between groups", "D": "The trial is invalid"}, "answer": "B"
        },
        {
            "q": "A drug's efficacy graph shows a plateau after 200 mg. What does this imply?",
            "options": {"A": "Higher doses are always better", "B": "Increasing dose beyond 200 mg gives no added benefit",
                        "C": "The drug stops working at 200 mg", "D": "The graph is incorrect"}, "answer": "B"
        },
        {
            "q": "Patient data: high LDL, normal blood pressure, family history of heart disease. Risk level?",
            "options": {"A": "No risk", "B": "Elevated cardiovascular risk",
                        "C": "Only respiratory risk", "D": "Risk limited to kidneys"}, "answer": "B"
        },
        {
            "q": "Why is a control group used in medical research?",
            "options": {"A": "To reduce costs", "B": "To compare treatment effects against a baseline",
                        "C": "To include more patients", "D": "To speed up the study"}, "answer": "B"
        },
        {
            "q": "A patient's ECG shows an abnormal pattern. A doctor's first analytical step is?",
            "options": {"A": "Dismiss it as a machine error", "B": "Compare with previous ECGs and normal patterns",
                        "C": "Immediately perform surgery", "D": "Give pain relief"}, "answer": "B"
        },
        {
            "q": "Analyzing patient charts, you notice infection cases spike every winter. This information helps to?",
            "options": {"A": "Reduce hospital staff in winter", "B": "Prepare preventive measures before winter",
                        "C": "Cancel winter appointments", "D": "Nothing; it is coincidence"}, "answer": "B"
        },
    ],

    "Clinical Reasoning": [
        {
            "q": "A 60-year-old patient presents with chest pain radiating to the left arm. Most likely diagnosis?",
            "options": {"A": "Indigestion", "B": "Myocardial infarction (heart attack)",
                        "C": "Muscle spasm", "D": "Fracture"}, "answer": "B"
        },
        {
            "q": "A child has high fever, stiff neck, and sensitivity to light. What is suspected?",
            "options": {"A": "Common cold", "B": "Meningitis",
                        "C": "Dehydration", "D": "Influenza"}, "answer": "B"
        },
        {
            "q": "A patient on long-term steroids shows high blood sugar. This is most likely due to?",
            "options": {"A": "Natural aging", "B": "Steroid-induced hyperglycemia",
                        "C": "Hypoglycemia", "D": "Iron deficiency"}, "answer": "B"
        },
        {
            "q": "A pregnant patient has severe headache and high BP. The likely condition is?",
            "options": {"A": "Migraine", "B": "Pre-eclampsia",
                        "C": "Anemia", "D": "Anxiety"}, "answer": "B"
        },
        {
            "q": "Clinical reasoning involves linking symptoms to a diagnosis using?",
            "options": {"A": "Guesswork", "B": "Pathophysiology and medical knowledge",
                        "C": "Only lab results", "D": "Patient preference"}, "answer": "B"
        },
        {
            "q": "An elderly patient is confused and has a high temperature. What should be ruled out first?",
            "options": {"A": "Common cold", "B": "Sepsis or urinary tract infection",
                        "C": "Vitamin deficiency", "D": "Arthritis"}, "answer": "B"
        },
        {
            "q": "A patient has yellow skin, dark urine, and pale stools. These symptoms suggest?",
            "options": {"A": "Anemia", "B": "Jaundice/liver disease",
                        "C": "Kidney failure", "D": "Asthma"}, "answer": "B"
        },
    ],

    "Decision Making": [
        {
            "q": "A trauma patient needs blood but the family is unreachable. What should the doctor do?",
            "options": {"A": "Wait for family consent", "B": "Proceed with emergency treatment to save life",
                        "C": "Delay treatment", "D": "Discharge the patient"}, "answer": "B"
        },
        {
            "q": "Two treatments are equally effective, but one has fewer side effects. Which is preferred?",
            "options": {"A": "The one with more side effects", "B": "The one with fewer side effects",
                        "C": "The more expensive one", "D": "Neither; do nothing"}, "answer": "B"
        },
        {
            "q": "A patient refuses a life-saving procedure. What is the ethical approach?",
            "options": {"A": "Force the procedure", "B": "Inform, respect autonomy, and document refusal",
                        "C": "Ignore their refusal", "D": "Discharge immediately"}, "answer": "B"
        },
        {
            "q": "A doctor must allocate one ICU bed between two critical patients. The priority goes to?",
            "options": {"A": "The wealthier patient", "B": "The patient with higher survival probability",
                        "C": "The older patient", "D": "The first admitted patient"}, "answer": "B"
        },
        {
            "q": "Good clinical decision-making is best based on?",
            "options": {"A": "Intuition alone", "B": "Evidence-based medicine and patient values",
                        "C": "Hospital policy only", "D": "The most expensive option"}, "answer": "B"
        },
        {
            "q": "A test has 95% sensitivity but 50% specificity. What does this mean in clinical decision-making?",
            "options": {"A": "Good for confirming disease", "B": "Good for ruling out disease but produces many false positives",
                        "C": "Not useful", "D": "Reliable for all decisions"}, "answer": "B"
        },
        {
            "q": "In a mass casualty event, triage involves?",
            "options": {"A": "Treating patients in order of arrival", "B": "Prioritizing based on severity and survivability",
                        "C": "Treating only the most severe cases", "D": "Treating the least severe first"}, "answer": "B"
        },
    ],

    "Problem Solving": [
        {
            "q": "A drug causes allergic reaction. What is the immediate problem-solving step?",
            "options": {"A": "Increase the dose", "B": "Discontinue the drug and treat the reaction",
                        "C": "Ignore the allergy", "D": "Apply the same drug topically"}, "answer": "B"
        },
        {
            "q": "Hospital supplies are running low during an epidemic. What is the best solution?",
            "options": {"A": "Close the hospital", "B": "Prioritize essential supplies and request emergency stock",
                        "C": "Ignore the shortage", "D": "Reduce patient care quality"}, "answer": "B"
        },
        {
            "q": "A patient is not responding to the standard treatment protocol. What should be done?",
            "options": {"A": "Continue the same treatment without change", "B": "Reassess diagnosis and consider alternative treatments",
                        "C": "Discharge the patient", "D": "Ignore and wait"}, "answer": "B"
        },
        {
            "q": "Problem-solving in medicine requires?",
            "options": {"A": "Guessing the solution", "B": "Identifying the root cause then applying evidence-based solutions",
                        "C": "Following a single rigid protocol", "D": "Leaving the decision to the patient"}, "answer": "B"
        },
        {
            "q": "A post-operative patient has unexpected bleeding. What is the priority action?",
            "options": {"A": "Document it and continue observation", "B": "Identify source, apply pressure, and alert the surgical team",
                        "C": "Discharge the patient", "D": "Wait for routine check"}, "answer": "B"
        },
        {
            "q": "An equipment failure occurs mid-surgery. The surgeon should?",
            "options": {"A": "Panic and leave the theatre", "B": "Switch to backup equipment or manual procedure",
                        "C": "Abandon the operation", "D": "Wait for IT to fix it"}, "answer": "B"
        },
        {
            "q": "A rehabilitation plan is not improving a patient's mobility. What is the best approach?",
            "options": {"A": "Increase exercise intensity immediately", "B": "Reassess the plan and modify based on patient progress",
                        "C": "Stop the rehabilitation", "D": "Ignore progress data"}, "answer": "B"
        },
    ],

    "Observation Skills": [
        {
            "q": "A nurse notices a patient's breathing pattern has changed. The correct action is?",
            "options": {"A": "Ignore it—patients breathe differently", "B": "Record the change and notify the doctor",
                        "C": "Give extra oxygen without informing anyone", "D": "Wake up the patient"}, "answer": "B"
        },
        {
            "q": "What is a key observation skill in a clinical setting?",
            "options": {"A": "Only reading lab reports", "B": "Noticing subtle changes in patient appearance and behavior",
                        "C": "Asking patients for self-diagnosis", "D": "Relying only on machines"}, "answer": "B"
        },
        {
            "q": "During a physical exam, a doctor notices pale conjunctiva. This likely indicates?",
            "options": {"A": "Normal health", "B": "Anemia",
                        "C": "Hypertension", "D": "Bone fracture"}, "answer": "B"
        },
        {
            "q": "While observing a patient walk, a physiotherapist notices an uneven gait. This suggests?",
            "options": {"A": "The patient is tired", "B": "A possible musculoskeletal or neurological issue",
                        "C": "Poor footwear", "D": "Normal aging"}, "answer": "B"
        },
        {
            "q": "A pharmacist notices a patient keeps returning for the same drug. This observation should prompt?",
            "options": {"A": "Selling more of the drug", "B": "Assessing for potential dependency or misuse",
                        "C": "Ignoring the pattern", "D": "Recommending a higher dose"}, "answer": "B"
        },
        {
            "q": "A doctor observes skin lesions in a specific pattern. Why is this significant?",
            "options": {"A": "It is only cosmetic", "B": "Lesion patterns can indicate specific diseases like shingles or psoriasis",
                        "C": "Lesion patterns are random", "D": "Only lab results matter for skin"}, "answer": "B"
        },
    ],

    "Ethical Thinking": [
        {
            "q": "A doctor is offered money to prescribe a specific brand. What is the ethical response?",
            "options": {"A": "Accept; it is a bonus", "B": "Decline; prescribing should be based on patient need",
                        "C": "Accept and share with colleagues", "D": "Ask for more money"}, "answer": "B"
        },
        {
            "q": "A patient shares information about illegal activity. The doctor should?",
            "options": {"A": "Report immediately to police", "B": "Maintain confidentiality per ethics, except if there is a safety risk",
                        "C": "Share with all hospital staff", "D": "Terminate care"}, "answer": "B"
        },
        {
            "q": "Is it ethical to withhold a terminal diagnosis from a patient at the family's request?",
            "options": {"A": "Yes, always protect the patient from bad news", "B": "No, patients have a right to know their diagnosis",
                        "C": "Yes, the family knows best", "D": "Only if the patient is elderly"}, "answer": "B"
        },
        {
            "q": "A medical student witnesses a colleague cheating in an exam. Ethical action is?",
            "options": {"A": "Join in", "B": "Report it to the appropriate authority",
                        "C": "Ignore it", "D": "Tell only friends"}, "answer": "B"
        },
        {
            "q": "The principle of 'non-maleficence' in medical ethics means?",
            "options": {"A": "Always cure the patient", "B": "Do no harm",
                        "C": "Treat patients equally", "D": "Respect autonomy"}, "answer": "B"
        },
        {
            "q": "A researcher falsifies data to support their hypothesis. This violates?",
            "options": {"A": "Hospital policy", "B": "Research integrity and medical ethics",
                        "C": "Budget regulations", "D": "Time management rules"}, "answer": "B"
        },
        {
            "q": "Informed consent is important because?",
            "options": {"A": "It protects only the doctor", "B": "It respects the patient's right to make informed decisions",
                        "C": "It is only a legal formality", "D": "It speeds up treatment"}, "answer": "B"
        },
    ],

    "Biology": [
        {"q": "Which organ pumps blood throughout the human body?", "options": {"A": "Brain", "B": "Liver", "C": "Heart", "D": "Kidney"}, "answer": "C"},
        {"q": "Basic unit of life?", "options": {"A": "Tissue", "B": "Cell", "C": "Organ", "D": "Atom"}, "answer": "B"},
        {"q": "Gas used in photosynthesis?", "options": {"A": "Oxygen", "B": "Carbon dioxide", "C": "Nitrogen", "D": "Hydrogen"}, "answer": "B"},
        {"q": "Plant part that makes food?", "options": {"A": "Root", "B": "Stem", "C": "Leaf", "D": "Flower"}, "answer": "C"},
        {"q": "DNA stands for?", "options": {"A": "Deoxyribonucleic Acid", "B": "Dynamic Nuclear Acid", "C": "Double Nitrogen Acid", "D": "Deoxynitrogen Acid"}, "answer": "A"},
        {"q": "Cells that fight infection?", "options": {"A": "RBC", "B": "WBC", "C": "Platelets", "D": "Plasma"}, "answer": "B"},
        {"q": "Food making process in plants?", "options": {"A": "Respiration", "B": "Digestion", "C": "Photosynthesis", "D": "Transpiration"}, "answer": "C"},
        {"q": "Organ producing urine?", "options": {"A": "Liver", "B": "Kidney", "C": "Heart", "D": "Lung"}, "answer": "B"},
        {"q": "Vitamin from sunlight?", "options": {"A": "A", "B": "B", "C": "C", "D": "D"}, "answer": "D"},
        {"q": "System controlling body responses?", "options": {"A": "Digestive", "B": "Nervous", "C": "Circulatory", "D": "Respiratory"}, "answer": "B"},
        {"q": "Cell control center?", "options": {"A": "Nucleus", "B": "Cytoplasm", "C": "Membrane", "D": "Ribosome"}, "answer": "A"},
        {"q": "Largest human organ?", "options": {"A": "Liver", "B": "Brain", "C": "Skin", "D": "Heart"}, "answer": "C"},
        {"q": "Green pigment in plants?", "options": {"A": "Chlorophyll", "B": "Hemoglobin", "C": "Melanin", "D": "Carotene"}, "answer": "A"},
        {"q": "Universal donor blood group?", "options": {"A": "A", "B": "B", "C": "AB", "D": "O"}, "answer": "D"},
        {"q": "Breathing organ?", "options": {"A": "Kidney", "B": "Lung", "C": "Stomach", "D": "Liver"}, "answer": "B"},
        {"q": "Brain part for balance?", "options": {"A": "Cerebrum", "B": "Cerebellum", "C": "Medulla", "D": "Hypothalamus"}, "answer": "B"},
        {"q": "Body building nutrient?", "options": {"A": "Carbohydrates", "B": "Proteins", "C": "Vitamins", "D": "Minerals"}, "answer": "B"},
        {"q": "Eye part controlling light?", "options": {"A": "Retina", "B": "Iris", "C": "Lens", "D": "Cornea"}, "answer": "B"},
        {"q": "Energy release process?", "options": {"A": "Photosynthesis", "B": "Respiration", "C": "Digestion", "D": "Absorption"}, "answer": "B"},
        {"q": "Largest mammal?", "options": {"A": "Elephant", "B": "Blue whale", "C": "Giraffe", "D": "Shark"}, "answer": "B"},
        {"q": "Genetic material structure?", "options": {"A": "Chromosome", "B": "Ribosome", "C": "Cytoplasm", "D": "Vacuole"}, "answer": "A"},
        {"q": "Nutrient transport system?", "options": {"A": "Nervous", "B": "Circulatory", "C": "Respiratory", "D": "Digestive"}, "answer": "B"},
        {"q": "Gas released in photosynthesis?", "options": {"A": "Oxygen", "B": "CO2", "C": "Nitrogen", "D": "Hydrogen"}, "answer": "A"},
        {"q": "Insulin producing organ?", "options": {"A": "Liver", "B": "Pancreas", "C": "Kidney", "D": "Heart"}, "answer": "B"},
        {"q": "Organ digesting fats?", "options": {"A": "Liver", "B": "Stomach", "C": "Intestine", "D": "Kidney"}, "answer": "A"}
    ],

    "Chemistry": [
        {"q": "Symbol of oxygen?", "options": {"A": "O", "B": "Ox", "C": "Og", "D": "O2"}, "answer": "A"},
        {"q": "Chemical formula of water?", "options": {"A": "CO2", "B": "H2O", "C": "O2", "D": "H2"}, "answer": "B"},
        {"q": "Gas needed for combustion?", "options": {"A": "Nitrogen", "B": "Oxygen", "C": "Hydrogen", "D": "CO2"}, "answer": "B"},
        {"q": "pH of pure water?", "options": {"A": "5", "B": "6", "C": "7", "D": "8"}, "answer": "C"},
        {"q": "Pencil lead element?", "options": {"A": "Carbon", "B": "Graphite", "C": "Lead", "D": "Silicon"}, "answer": "B"},
        {"q": "Atomic number represents?", "options": {"A": "Protons", "B": "Neutrons", "C": "Electrons", "D": "Mass"}, "answer": "A"},
        {"q": "Liquid metal?", "options": {"A": "Mercury", "B": "Iron", "C": "Copper", "D": "Aluminium"}, "answer": "A"},
        {"q": "Balloon gas?", "options": {"A": "Hydrogen", "B": "Oxygen", "C": "Helium", "D": "Nitrogen"}, "answer": "C"},
        {"q": "Rusting type?", "options": {"A": "Physical", "B": "Chemical", "C": "Nuclear", "D": "Mechanical"}, "answer": "B"},
        {"q": "Acid in lemon?", "options": {"A": "HCl", "B": "Citric", "C": "Sulfuric", "D": "Nitric"}, "answer": "B"},
        {"q": "NaCl is?", "options": {"A": "Sugar", "B": "Salt", "C": "Baking soda", "D": "Vinegar"}, "answer": "B"},
        {"q": "Gas turning limewater milky?", "options": {"A": "Oxygen", "B": "CO2", "C": "Nitrogen", "D": "Hydrogen"}, "answer": "B"},
        {"q": "Atomic number 1 element?", "options": {"A": "Helium", "B": "Hydrogen", "C": "Oxygen", "D": "Carbon"}, "answer": "B"},
        {"q": "Baking soda formula?", "options": {"A": "NaCl", "B": "NaHCO3", "C": "Na2CO3", "D": "HCl"}, "answer": "B"},
        {"q": "Liquid to gas?", "options": {"A": "Condensation", "B": "Evaporation", "C": "Freezing", "D": "Sublimation"}, "answer": "B"},
        {"q": "Best conductor?", "options": {"A": "Copper", "B": "Silver", "C": "Aluminum", "D": "Iron"}, "answer": "B"},
        {"q": "Acid in vinegar?", "options": {"A": "Acetic", "B": "Citric", "C": "Sulfuric", "D": "Nitric"}, "answer": "A"},
        {"q": "Periodic table creator?", "options": {"A": "Dalton", "B": "Mendeleev", "C": "Rutherford", "D": "Bohr"}, "answer": "B"},
        {"q": "Matter with fixed shape?", "options": {"A": "Liquid", "B": "Gas", "C": "Solid", "D": "Plasma"}, "answer": "C"},
        {"q": "Gas protecting earth from UV?", "options": {"A": "Oxygen", "B": "Ozone", "C": "CO2", "D": "Nitrogen"}, "answer": "B"},
        {"q": "Wire metal?", "options": {"A": "Copper", "B": "Iron", "C": "Silver", "D": "Gold"}, "answer": "A"},
        {"q": "Neutralizes stomach acid?", "options": {"A": "Antacid", "B": "Salt", "C": "Sugar", "D": "Vinegar"}, "answer": "A"},
        {"q": "Energy releasing reaction?", "options": {"A": "Endothermic", "B": "Exothermic", "C": "Neutral", "D": "Physical"}, "answer": "B"},
        {"q": "Organic compound element?", "options": {"A": "Oxygen", "B": "Carbon", "C": "Nitrogen", "D": "Hydrogen"}, "answer": "B"},
        {"q": "Most abundant atmospheric gas?", "options": {"A": "Oxygen", "B": "CO2", "C": "Nitrogen", "D": "Hydrogen"}, "answer": "C"}
    ],
}

# ─────────────────────────────────────────────
# AUTO-GENERATE remaining questions to reach 28
# ─────────────────────────────────────────────

def _generate_filler(skill: str, start: int, total: int = 28):
    """Generate generic filler questions numbered start..total for a given skill."""
    generated = []
    for i in range(start, total + 1):
        generated.append({
            "q": (
                f"A healthcare professional faces an unexpected clinical "
                f"situation. Which approach best reflects {skill.lower()} in this context?"
            ),
            "options": {
                "A": "Avoid dealing with the situation",
                "B": "Apply systematic reasoning and evidence-based practice",
                "C": "Guess without analysis",
                "D": "Defer indefinitely to others"
            },
            "answer": "B"
        })
    return generated


# Build final bank with unique IDs
MEDICAL_APTITUDE_QUESTIONS: dict[str, list[dict]] = {}

THINKING_SKILLS = [
    "Critical Thinking",
    "Analytical Thinking",
    "Clinical Reasoning",
    "Decision Making",
    "Problem Solving",
    "Observation Skills",
    "Ethical Thinking",
]

CORE_SUBJECTS = ["Biology", "Chemistry"]

for _skill in (THINKING_SKILLS + CORE_SUBJECTS):
    base = _raw.get(_skill, [])
    # Fill to 28 questions for uniform sampling if needed (Bio/Chem are already 25, but 28 is safe)
    if len(base) < 28:
        base = base + _generate_filler(_skill, len(base) + 1, 28)
    
    # Prefix mapping: CT_, AT_, CR_, DM_, PS_, OS_, ET_, B_, C_
    if _skill == "Biology": prefix = "B_"
    elif _skill == "Chemistry": prefix = "C_"
    else: prefix = "".join(w[0] for w in _skill.split()) + "_"

    bank = []
    for idx, q in enumerate(base, 1):
        entry = dict(q)
        entry["id"] = f"{prefix}{idx}"
        bank.append(entry)
    MEDICAL_APTITUDE_QUESTIONS[_skill] = bank


# ─────────────────────────────────────────────
# Public helpers
# ─────────────────────────────────────────────

def get_questions_by_skill(skill: str) -> list:
    """Return all questions for a given skill/subject."""
    return MEDICAL_APTITUDE_QUESTIONS.get(skill, [])


def sample_questions(skill: str, n: int = 7) -> list:
    """Return n random questions from a given skill (default 7)."""
    pool = MEDICAL_APTITUDE_QUESTIONS.get(skill, [])
    return random.sample(pool, min(n, len(pool)))


def get_test_questions(n_per_thinking_skill: int = 7, n_per_core_subject: int = 5) -> list:
    """
    Build a full test: 
    - 7 questions from each of the 7 Thinking Skills (49 total)
    - 5 questions from Biology
    - 5 questions from Chemistry
    Total: 59 questions.
    """
    selected = []
    # Thinking Skills
    for skill in THINKING_SKILLS:
        for q in sample_questions(skill, n_per_thinking_skill):
            q_copy = dict(q)
            q_copy["category"] = skill
            selected.append(q_copy)
    
    # Core Subjects
    for subject in CORE_SUBJECTS:
        for q in sample_questions(subject, n_per_core_subject):
            q_copy = dict(q)
            q_copy["category"] = subject
            selected.append(q_copy)

    random.shuffle(selected)
    return selected


def dominant_skill(stream_name: str) -> str:
    """Compatible shim — returns the skill with the most questions (always 28)."""
    return THINKING_SKILLS[0] if THINKING_SKILLS else ""


if __name__ == "__main__":
    print("Thinking Skills:", THINKING_SKILLS)
    for s in THINKING_SKILLS:
        print(f"  {s}: {len(MEDICAL_APTITUDE_QUESTIONS[s])} questions")
    test = get_test_questions()
    print(f"\nSample test: {len(test)} questions total")
    print("First question:", test[0]["q"])
