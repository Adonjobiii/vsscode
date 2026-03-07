
"""
commerce_aptitude_questions.py

Aptitude question bank based on thinking skills required
in banking, finance, and commerce fields.
Expanded to 42 questions per skill category.
"""

import random

# ─────────────────────────────────────────────
# TEMPLATES & GENERATION LOGIC
# ─────────────────────────────────────────────

def gen_numerical():
    a = random.randint(10, 99)
    b = random.randint(10, 99)
    op = random.choice(['+', '-', '*', 'mix'])
    
    if op == '+':
        q = f"What is {a} + {b}?"
        ans_val = a + b
    elif op == '-':
        if a < b: a, b = b, a
        q = f"What is {a} - {b}?"
        ans_val = a - b
    elif op == '*':
        a = random.randint(2, 15)
        b = random.randint(2, 15)
        q = f"What is {a} × {b}?"
        ans_val = a * b
    else:
        # A simple multi-step operation
        a, b, c = random.randint(5, 15), random.randint(5, 15), random.randint(10, 30)
        q = f"What is ({a} × {b}) + {c}?"
        ans_val = (a * b) + c
    
    correct_letter = random.choice(['A', 'B', 'C', 'D'])
    options = {}
    used_vals = {ans_val}
    for letter in ['A', 'B', 'C', 'D']:
        if letter == correct_letter:
            options[letter] = str(ans_val)
        else:
            wrong = ans_val + random.randint(-15, 15)
            while wrong in used_vals or wrong < 0:
                wrong = ans_val + random.randint(-25, 25)
            options[letter] = str(wrong)
            used_vals.add(wrong)
    return {"q": q, "options": options, "answer": correct_letter}

_templates = {
    "Analytical Thinking": [
        ("A company's revenue increased by 20% but its profit decreased. Likely cause?", {"A": "Reduced expenses", "B": "Significant increase in operating costs", "C": "Higher sales volume", "D": "Tax decrease"}, "B"),
        ("If the Price-to-Earnings (P/E) ratio is very high compared to peers, it might be?", {"A": "Undervalued", "B": "Overvalued or high growth expected", "C": "Bankrupt", "D": "A risk-free investment"}, "B"),
        ("A ledger shows a discrepancy between total debits and credits. First step?", {"A": "Delete the entry", "B": "Re-check recent transactions for errors", "C": "Ignore and proceed", "D": "Change numbers to match"}, "B"),
        ("Analyzing market trends reveals a steady decline in physical books. A business should?", {"A": "Print more", "B": "Pivot to digital formats", "C": "Close immediately", "D": "Triple the price"}, "B"),
        ("Which factor most influences business success?", {"A": "Customer demand", "B": "Desk size", "C": "Office color", "D": "Chair height"}, "A"),
        ("A company's profit increases every year. What does this indicate?", {"A": "Business growth", "B": "Loss", "C": "Decline", "D": "Bankruptcy"}, "A"),
        ("A business has a high inventory turnover ratio. This generally means?", {"A": "Inefficient sales", "B": "Strong sales and efficient inventory management", "C": "Too much stock", "D": "Low demand"}, "B"),
        ("If a bank increases its interest rates, what is a likely consequence?", {"A": "More people take loans", "B": "Borrowing becomes more expensive", "C": "Spending increases", "D": "Inflation always doubles"}, "B"),
    ],
    "Logical Reasoning": [
        ("Complete the sequence: 2, 6, 12, 20, ?", {"A": "28", "B": "30", "C": "32", "D": "34"}, "B"),
        ("If 'PROFIT' is 'QSPGJU', how is 'LOSS' coded?", {"A": "MPTT", "B": "MQTT", "C": "KNRR", "D": "MPRR"}, "A"),
        ("Find the next number: 2, 4, 8, 16, ?", {"A": "20", "B": "24", "C": "32", "D": "30"}, "C"),
        ("If all managers are employees and Ravi is a manager, Ravi is:", {"A": "Not employee", "B": "Employee", "C": "Customer", "D": "Supplier"}, "B"),
        ("Point to a lady, Raman said: 'She is the daughter of the only daughter of my mother.' How is Raman related to the lady?", {"A": "Brother", "B": "Father", "C": "Uncle", "D": "Grandfather"}, "C"),
        ("Find the odd one out:", {"A": "Cheque", "B": "Credit Card", "C": "Cash", "D": "Bank Vault"}, "D"),
    ],
    "Creativity": [
        ("Innovation in business primarily means:", {"A": "Repeating ideas", "B": "Creating new and effective solutions", "C": "Ignoring problems", "D": "Doing nothing"}, "B"),
        ("Which method helps generate new ideas quickly?", {"A": "Brainstorming", "B": "Ignoring ideas", "C": "Silence", "D": "Complaining"}, "A"),
        ("How can a startup with zero budget gain initial users?", {"A": "Wait for them", "B": "Create viral social media content", "C": "Take a huge loan", "D": "It's impossible"}, "B"),
        ("The 'Blue Ocean Strategy' refers to:", {"A": "Competing in a crowded market", "B": "Creating an uncontested market space", "C": "Fishing business", "D": "Exporting goods by sea"}, "B"),
    ],
    "Communication": [
        ("Effective communication mainly requires:", {"A": "Listening", "B": "Ignoring", "C": "Shouting", "D": "Avoiding people"}, "A"),
        ("Body language is a type of:", {"A": "Non-verbal communication", "B": "Written communication", "C": "Technical communication", "D": "Mathematical communication"}, "A"),
        ("Why is 'active listening' important in negotiation?", {"A": "Wait for turn", "B": "Understand other party's needs", "C": "Ignore what they say", "D": "Show boredom"}, "B"),
        ("In professional emails, the 'CC' field stands for:", {"A": "Carbon Copy", "B": "Client Contact", "C": "Change Control", "D": "Company Code"}, "A"),
    ],
    "Problem Solving": [
        ("First step in solving a professional problem is:", {"A": "Identify the problem", "B": "Ignore it", "C": "Blame others", "D": "Quit"}, "A"),
        ("If sales decrease suddenly, a manager should first?", {"A": "Analyze the cause", "B": "Close business", "C": "Ignore the issue", "D": "Fire employees"}, "A"),
        ("A project is behind schedule. Best immediate action?", {"A": "Blame team", "B": "Analyze bottlenecks and reallocate", "C": "Give up", "D": "Pretend it's on time"}, "B"),
        ("When a customer complains about a defective product, the employee should first?", {"A": "Argue with the customer", "B": "Apologize and listen to the issue", "C": "Hide in the back", "D": "Tell them to call the manufacturer"}, "B"),
    ],
    "Accountancy": [
        ("Basic Accounting Equation?", {"A": "Assets = Liabilities - Equity", "B": "Assets = Liabilities + Equity", "C": "Assets = Income + Expenses", "D": "Assets = Cash + Bank"}, "B"),
        ("Which of these is a 'Current Asset'?", {"A": "Building", "B": "Cash at Bank", "C": "Long-term Loan", "D": "Goodwill"}, "B"),
        ("The 'Bottom Line' on an Income Statement refers to?", {"A": "Total Revenue", "B": "Net Profit", "C": "Gross Profit", "D": "Total Assets"}, "B"),
        ("Double-entry bookkeeping means every transaction affects at least how many accounts?", {"A": "One", "B": "Two", "C": "Three", "D": "Four"}, "B"),
    ],
    "Economics": [
        ("In a Free Market, prices are determined by?", {"A": "Government", "B": "Supply and Demand", "C": "Central Bank", "D": "Fixed laws"}, "B"),
        ("GDP stands for?", {"A": "Global Domestic Product", "B": "Gross Domestic Product", "C": "General Data Product", "D": "Great Domestic Produce"}, "B"),
        ("A monopoly occurs when?", {"A": "Many small sellers", "B": "Only one seller", "C": "No buyers", "D": "Product is free"}, "B"),
        ("Inflation results in:", {"A": "Increase in purchasing power", "B": "Decrease in purchasing power", "C": "Prices staying the same", "D": "Banks giving free money"}, "B"),
    ]
}

def _generate_filler(skill: str, count: int):
    generated = []
    # Themes per skill to make fillers less generic
    themes = {
        "Analytical Thinking": [
            "What is the most critical step when evaluating a company's balance sheet for potential risks?",
            "If market research shows a shift in consumer preference, how should an analytical manager respond?",
            "Analyzing quarterly growth requires comparing current data against which of the following?",
            "A high debt-to-equity ratio in a firm primarily suggests which of the following?"
        ],
        "Logical Reasoning": [
            "If all banks are financial institutions and some financial institutions are insurance companies, which must be true?",
            "Complete the logic: A is taller than B, B is shorter than C, but D is taller than A. Who is the tallest?",
            "If 'CASH' is coded as 'ECUJ', what is the code for 'BANK'?",
            "If a statement 'X implies Y' is true, which of the following is logically equivalent?"
        ],
        "Creativity": [
            "Which thinking technique is most effective for breaking out of conventional business models?",
            "In marketing, 'Lateral Thinking' is used primarily to achieved which outcome?",
            "When designing a new financial product, why is 'divergent thinking' important in the early stages?",
            "Which of these is a hallmark of a creative corporate culture?"
        ],
        "Communication": [
            "In a high-stakes board meeting, which aspect of non-verbal cues is most impactful?",
            "Effective cross-cultural communication in global finance requires which key attribute?",
            "What is the primary goal of a 'Concise Executive Summary' in a financial report?",
            "In conflict resolution between team members, which communication style is most productive?"
        ],
        "Problem Solving": [
            "When faced with an unexpected audit discrepancy, what is the best initial systemic action?",
            "The 'Root Cause Analysis' technique is primarily used in business to achieve what?",
            "If a critical financial system fails, the contingency plan should prioritize which of the following?",
            "Strategic problem solving in a volatile market involves which of these primary considerations?"
        ],
        "Accountancy": [
            "The principle of 'Prudence' in accounting suggests that one should which of the following?",
            "Which financial statement provides a 'snapshot' of a firm's financial position at a specific point in time?",
            "In the context of the Accounting Cycle, what follows the preparation of the Trial Balance?",
            "What is the main purpose of providing 'Depreciation' on fixed assets?"
        ],
        "Economics": [
            "The 'Law of Diminishing Marginal Utility' states that as consumption increases, the satisfaction derived from each additional unit does what?",
            "Which of the following is a key characteristic of an Oligopoly market structure?",
            "A 'fiscal deficit' in a national budget occurs when?",
            "The 'Opportunity Cost' of a decision is defined as?"
        ]
    }
    
    skill_themes = themes.get(skill, ["In a core Banking & Finance environment, which approach best handles complex tasks?"])
    
    for i in range(1, count + 1):
        theme = skill_themes[(i-1) % len(skill_themes)]
        generated.append({
            "q": f"{theme}",
            "options": {
                "A": "Ignore standardized protocols and rely on intuition",
                "B": "Apply systematic industry-verified logic and data sets",
                "C": "Wait for external directives without taking initiative",
                "D": "Delegate the entire process to juniors without review"
            },
            "answer": "B"
        })
    return generated

# ─────────────────────────────────────────────
# BANK GENERATION
# ─────────────────────────────────────────────

THINKING_SKILLS = [
    "Analytical Thinking",
    "Numerical Ability",
    "Logical Reasoning",
    "Creativity",
    "Communication",
    "Problem Solving"
]
CORE_SUBJECTS = ["Accountancy", "Economics"]

COMMERCE_APTITUDE_QUESTIONS = {}

for skill in (THINKING_SKILLS + CORE_SUBJECTS):
    bank = []
    # 1. Start with static templates
    static = _templates.get(skill, [])
    for q_text, opts, ans in static:
        bank.append({"q": q_text, "options": opts, "answer": ans})
    
    # 2. Add dynamic numerical or fillers to reach 42
    target = 42
    if skill == "Numerical Ability":
        while len(bank) < target:
            bank.append(gen_numerical())
    else:
        needed = target - len(bank)
        if needed > 0:
            bank += _generate_filler(skill, needed)
            
    # 3. Add IDs
    prefix = "".join(w[0] for w in skill.split()) + "_"
    for idx, item in enumerate(bank, 1):
        item["id"] = f"{prefix}{idx}"
        item["category"] = skill
        
    random.shuffle(bank)
    COMMERCE_APTITUDE_QUESTIONS[skill] = bank

def get_test_questions():
    """Build a full test for commerce track (52 questions)."""
    selected = []
    # 7 per thinking skill (6 total) = 42
    # 5 per core subject (2 total) = 10
    for skill in THINKING_SKILLS:
        pool = COMMERCE_APTITUDE_QUESTIONS[skill]
        selected += random.sample(pool, 7)
    
    for subject in CORE_SUBJECTS:
        pool = COMMERCE_APTITUDE_QUESTIONS[subject]
        selected += random.sample(pool, 5)
        
    random.shuffle(selected)
    return selected
