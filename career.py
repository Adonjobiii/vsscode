import random
import sys
import time
import threading
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import defaultdict
import re
import pymongo
import os
from dotenv import load_dotenv

# ====================================================================
# CONFIGURATION & MONGODB CONNECTION
# ====================================================================

# Load environment variables
load_dotenv()
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

if MONGO_PASSWORD:
    MONGO_URI = f"mongodb+srv://anoop:anoop123@cluster0.rd6nzal.mongodb.net/?retryWrites=true&w=majority"
else:
    MONGO_URI = "mongodb+srv://anoop:anoop123@cluster0.rd6nzal.mongodb.net/?retryWrites=true&w=majority"

try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client["CareerAssessmentDB"]
    users_collection = db["Personality"]
    client.admin.command("ping")
    print("✅ MongoDB connected")
except Exception as e:
    print("❌ MongoDB connection failed:", e)
    users_collection = None

# Set Matplotlib backend
try:
    matplotlib.use('TkAgg')
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False

# ====================================================================
# DATA & MOCK ML LOGIC
# ====================================================================

# --- Color Constants ---
COLOR_BG_DARK = "#2C3E50"
COLOR_BG_NAV = "#34495E"
COLOR_BG_CONTENT = "#ECF0F1"
COLOR_BUTTON_TEXT = "#FFFFFF"
COLOR_CURRENT_Q_NAV = "#E67E22"
COLOR_ANSWERED = "#27AE60"
COLOR_UNANSWERED = "#95A5A6"
COLOR_REVIEW = "#F1C40F"
COLOR_MODERATE = "#F39C12"
COLOR_ALERT = "#C0392B"

# --- Data Structures ---
ENGINEERING_STREAMS = [
    "Computer Science (CSE)", "Information Technology (IT)", "Electronics & Communication (ECE)",
    "Electrical & Electronics (EEE)", "Mechanical Engineering (ME)", "Civil Engineering (CE)",
    "Aerospace Engineering", "Chemical Engineering (CH)", "Biotechnology", "Industrial Engineering"
]

BROAD_INTERESTS = [
    "Technology & Coding", "Mechanics & Machines", "Structures & Construction",
    "Electronics & Gadgets", "Chemistry & Biology", "Space & Aviation",
    "Management & Business", "Design & Creativity", "Mathematics & Physics"
]

ENGINEERING_TASKS = {
    "Designing software algorithms": ["CS", "IT"],
    "Building robots or electronic circuits": ["EC", "EE"],
    "Designing car engines or machinery": ["ME", "AE"],
    "Planning buildings or bridges": ["CE"],
    "Working with chemical reactions or DNA": ["CH", "BT"],
    "Analyzing system efficiency and logistics": ["IE"]
}

# --- Mock ML Models ---
class MockModel:
    def predict_proba(self, X):
        # Return random probabilities for demonstration if ML files missing
        np.random.seed(int(X.sum())) 
        probs = np.random.dirichlet(np.ones(10), size=1)[0]
        return [probs]

class MLModelTrainer:
    def __init__(self):
        self.career_model = MockModel()
        self.aptitude_model = MockModel()

ML_MODELS = MLModelTrainer()

# --- Mappings ---
career_course_map = {i: stream for i, stream in enumerate(ENGINEERING_STREAMS)}
aptitude_course_map = career_course_map 
APTITUDE_MODEL_CATEGORIES = [
    "Algorithmic", "Computational", "Logical", "System", 
    "Critical", "Abstract", "Creative"
]

# --- Question Generator ---
def generate_mock_questions():
    qs = defaultdict(list)
    for cat in APTITUDE_MODEL_CATEGORIES:
        for i in range(10):
            qs[cat].append({
                "id": i,
                "q": f"Mock Question {i+1} testing your {cat} skills. Which is correct?",
                "options": {"A": "Option A (Correct)", "B": "Option B", "C": "Option C", "D": "Option D"}
            })
    return qs

QUESTIONS = generate_mock_questions()

CORRECT_ANSWERS = defaultdict(dict)
for cat, q_list in QUESTIONS.items():
    for q in q_list:
        CORRECT_ANSWERS[cat][q['id']] = "A" # Mock answer is always A for demo

BOOM_PERCENTAGE_DATA = {"CS": 95, "IT": 92, "EC": 85, "EE": 80, "ME": 75, "AE": 70, "CE": 72, "CH": 68, "BT": 88, "IE": 65}
INTEREST_TO_NON_ENGINEERING_MAP = {
    "Technology & Coding": ["BCA", "B.Sc Computer Science"],
    "Management & Business": ["BBA", "B.Com"],
    "Design & Creativity": ["B.Des", "Architecture (B.Arch)"],
    "Chemistry & Biology": ["B.Pharma", "MBBS", "B.Sc Microbiology"]
}

# --- Personality Data ---
PERSONALITY_TRAITS = {
    'O': {"name": "Openness", "color": "#3498db"},
    'C': {"name": "Conscientiousness", "color": "#2ecc71"},
    'E': {"name": "Extraversion", "color": "#f1c40f"},
    'A': {"name": "Agreeableness", "color": "#9b59b6"},
    'N': {"name": "Neuroticism", "color": "#e74c3c"},
}

PERSONALITY_QUESTIONNAIRE = {
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

# ====================================================================
# Part 0: User Profile Setup
# ====================================================================
class UserProfileSetup:
    def __init__(self, parent, container_frame):
        self.parent = parent
        self.container_frame = container_frame
        self.user_data = parent.user_data
        self.interest_vars = {}
        self.build_widgets()

    def build_widgets(self):
        for widget in self.container_frame.winfo_children():
            widget.destroy()

        self.main_frame = tk.Frame(self.container_frame, bg=COLOR_BG_CONTENT, padx=40, pady=40)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(self.main_frame, text="Step 0: User Profile & Interests", font=("Arial", 18, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack(pady=(0, 20))
        
        # --- Input Frame ---
        input_frame = tk.Frame(self.main_frame, bg="white", padx=30, pady=20, relief=tk.RAISED, borderwidth=1)
        input_frame.pack(pady=10, fill=tk.X)
        
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=2)
        
        # 1. Name
        tk.Label(input_frame, text="Full Name:", bg="white", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=10)
        self.name_entry.insert(0, self.user_data.get('name', ''))

        # 2. Age
        tk.Label(input_frame, text="Age:", bg="white", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
        self.age_entry = tk.Spinbox(input_frame, from_=15, to_=50, font=("Arial", 12), width=5)
        self.age_entry.grid(row=1, column=1, sticky="w", pady=5, padx=10)
        self.age_entry.delete(0, "end")
        self.age_entry.insert(0, self.user_data.get('age', 17))

        # 3. Class/Grade
        tk.Label(input_frame, text="Current Class/Grade:", bg="white", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
        self.class_var = tk.StringVar(value=self.user_data.get('class', "12th Grade"))
        ttk.Combobox(input_frame, textvariable=self.class_var, values=["10th Grade", "11th Grade", "12th Grade", "Completed 12th"], state="readonly", font=("Arial", 12)).grid(row=2, column=1, sticky="ew", pady=5, padx=10)

        # 4. Preferred Course (Engineering Only)
        tk.Label(input_frame, text="Preferred Engineering Course:", bg="white", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky="w", pady=10)
        self.preferred_course_var = tk.StringVar(value=self.user_data.get('preferred_course', ENGINEERING_STREAMS[0]))
        ttk.Combobox(input_frame, textvariable=self.preferred_course_var, values=ENGINEERING_STREAMS, state="readonly", font=("Arial", 12)).grid(row=3, column=1, sticky="ew", pady=10, padx=10)
        
        # --- Interests Checkbox Frame ---
        tk.Label(self.main_frame, text="Select Broad Fields of Interest:", font=("Arial", 14, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack(pady=(20, 10), anchor="w")
        
        interest_frame = tk.Frame(self.main_frame, bg="white", padx=30, pady=20, relief=tk.RAISED, borderwidth=1)
        interest_frame.pack(pady=10, fill=tk.X, expand=True)
        interest_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        existing_interests = self.user_data.get('interests', [])
        for i, interest in enumerate(BROAD_INTERESTS):
            initial_value = interest in existing_interests
            var = tk.BooleanVar(value=initial_value)
            self.interest_vars[interest] = var
            chk = tk.Checkbutton(interest_frame, text=interest, variable=var, bg="white", font=("Arial", 11), anchor="w")
            chk.grid(row=i//3, column=i%3, sticky="w", padx=15, pady=5)

        # --- Submit Button ---
        submit_button = tk.Button(self.main_frame, text="Start Career Profiler (Part 1) →", font=("Arial", 12, "bold"), command=self.submit_profile, bg=COLOR_ANSWERED, fg=COLOR_BUTTON_TEXT)
        submit_button.pack(side=tk.BOTTOM, pady=20)
        
    def submit_profile(self):
        name = self.name_entry.get().strip()
        age = self.age_entry.get()
        preferred_course = self.preferred_course_var.get()
        
        if not name or not age.isdigit():
            messagebox.showwarning("Incomplete Data", "Please enter a valid name and age (must be a number).")
            return

        selected_interests = [interest for interest, var in self.interest_vars.items() if var.get()]
        
        if not selected_interests:
            if not messagebox.askyesno("Confirm", "You haven't selected any broad interests. This information is key for suggesting alternatives. Continue anyway?"):
                return

        self.user_data.update({
            "name": name,
            "age": int(age),
            "class": self.class_var.get(),
            "preferred_course": preferred_course,
            "interests": selected_interests
        })
        
        self.parent.show_career_profiler()

# ====================================================================
# Part 1: Career Assessment (Interests)
# ====================================================================
class CareerProfilerPart1:
    def __init__(self, parent, container_frame):
        self.parent = parent
        self.container_frame = container_frame
        self.page = 1
        self.user_profile = {"career_priority": self.parent.user_data.get('career_priority_list', [])}
        self.all_streams = ENGINEERING_STREAMS[:]
        self.stream_buttons = {}
        self.task_ratings = {}
        self.recommended_stream = None
        self.build_widgets()
        self.show_page_1()

    def build_widgets(self):
        for widget in self.container_frame.winfo_children():
            widget.destroy()
        self.main_frame = tk.Frame(self.container_frame, bg=COLOR_BG_DARK)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.grid_columnconfigure(0, weight=0, minsize=250)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.create_navigation_panel()
        self.create_content_panel()
        
    def create_navigation_panel(self):
        self.nav_frame = tk.Frame(self.main_frame, bg=COLOR_BG_NAV, padx=10, pady=10)
        self.nav_frame.grid(row=0, column=0, sticky="nsew") 
        tk.Label(self.nav_frame, text="Career Profiler", font=("Arial", 16, "bold"), fg=COLOR_BUTTON_TEXT, bg=COLOR_BG_NAV).pack(pady=(0, 20))
        tk.Label(self.nav_frame, text="Step 0: Profile Setup (Done)", font=("Arial", 12), bg=COLOR_BG_NAV, fg=COLOR_ANSWERED).pack(pady=5, anchor="w")
        self.nav_label_1 = tk.Label(self.nav_frame, text="Step 1: Career Streams", font=("Arial", 12, "bold"), bg=COLOR_BG_NAV, fg=COLOR_CURRENT_Q_NAV)
        self.nav_label_1.pack(pady=5, anchor="w")
        self.nav_label_2 = tk.Label(self.nav_frame, text="Step 2: Task Ratings", font=("Arial", 12), bg=COLOR_BG_NAV, fg=COLOR_BUTTON_TEXT)
        self.nav_label_2.pack(pady=5, anchor="w")
        self.nav_label_3 = tk.Label(self.nav_frame, text="Step 3: Recommendation", font=("Arial", 12), bg=COLOR_BG_NAV, fg=COLOR_BUTTON_TEXT)
        self.nav_label_3.pack(pady=5, anchor="w")

    def create_content_panel(self):
        self.content_frame = tk.Frame(self.main_frame, bg=COLOR_BG_CONTENT)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def update_nav_panel(self):
        self.nav_label_1.config(font=("Arial", 12), fg=COLOR_BUTTON_TEXT)
        self.nav_label_2.config(font=("Arial", 12), fg=COLOR_BUTTON_TEXT)
        self.nav_label_3.config(font=("Arial", 12), fg=COLOR_BUTTON_TEXT)
        if self.page == 1:
            self.nav_label_1.config(font=("Arial", 12, "bold"), fg=COLOR_CURRENT_Q_NAV)
        elif self.page == 2:
            self.nav_label_2.config(font=("Arial", 12, "bold"), fg=COLOR_CURRENT_Q_NAV)
        elif self.page == 3:
            self.nav_label_3.config(font=("Arial", 12, "bold"), fg=COLOR_CURRENT_Q_NAV)

    def show_page_1(self):
        self.page = 1
        self.clear_content_frame()
        self.update_nav_panel()
        page_frame = tk.Frame(self.content_frame, bg="white", padx=20, pady=20)
        page_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(page_frame, text="Step 1: Prioritize Your Engineering Options", font=("Arial", 16, "bold"), bg="white").pack(pady=(0, 20))
        tk.Label(page_frame, text="Click on the engineering streams you find most appealing to create a priority list.", font=("Arial", 12), wraplength=700, justify="left", bg="white").pack(anchor="w", pady=5)
        pane_window = ttk.PanedWindow(page_frame, orient=tk.HORIZONTAL)
        pane_window.pack(fill=tk.BOTH, expand=True, pady=10)
        streams_pane = tk.Frame(pane_window, bg="white")
        streams_canvas = tk.Canvas(streams_pane, bg="white", highlightthickness=0)
        streams_scrollbar = ttk.Scrollbar(streams_pane, orient="vertical", command=streams_canvas.yview)
        streams_frame = tk.Frame(streams_canvas, bg="white")
        streams_frame.bind("<Configure>", lambda e: streams_canvas.configure(scrollregion=streams_canvas.bbox("all")))
        streams_canvas.create_window((0, 0), window=streams_frame, anchor="nw")
        streams_canvas.configure(yscrollcommand=streams_scrollbar.set)
        streams_canvas.pack(side="left", fill="both", expand=True)
        streams_scrollbar.pack(side="right", fill="y")
        self.stream_buttons = {}
        for stream in self.all_streams:
            btn = tk.Button(streams_frame, text=stream, command=lambda s=stream: self.add_to_priority(s), font=("Arial", 11), bg="#bdc3c7", fg=COLOR_BG_DARK, relief=tk.RAISED)
            btn.pack(fill=tk.X, padx=5, pady=5)
            self.stream_buttons[stream] = btn
            if stream in self.user_profile["career_priority"]:
                btn.config(state=tk.DISABLED, relief=tk.SUNKEN, bg="#e0e0e0")
        priority_pane = tk.Frame(pane_window, bg="white")
        priority_title = tk.Label(priority_pane, text="Your Priorities:", font=("Arial", 12, "bold"), bg="white", wraplength=700, justify="left")
        priority_title.pack(anchor="w", padx=5)
        self.priority_list_frame = tk.Frame(priority_pane, bg="white")
        self.priority_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        pane_window.add(streams_pane, weight=1)
        pane_window.add(priority_pane, weight=1)
        self.next_button = tk.Button(self.content_frame, text="Next Page →", font=("Arial", 12, "bold"), command=self.show_page_2, bg=COLOR_CURRENT_Q_NAV, fg=COLOR_BUTTON_TEXT, state=tk.DISABLED)
        self.next_button.pack(side=tk.RIGHT, padx=10, pady=10)
        self.update_priority_display()
        self.update_next_button_state()

    def update_next_button_state(self):
        if self.user_profile["career_priority"]:
            self.next_button.config(state=tk.NORMAL)
        else:
            self.next_button.config(state=tk.DISABLED)

    def add_to_priority(self, stream):
        if stream not in self.user_profile["career_priority"]:
            self.user_profile["career_priority"].append(stream)
            self.stream_buttons[stream].config(state=tk.DISABLED, relief=tk.SUNKEN, bg="#e0e0e0")
        self.update_priority_display()
        self.update_next_button_state()

    def remove_from_priority(self, stream):
        if stream in self.user_profile["career_priority"]:
            self.user_profile["career_priority"].remove(stream)
            if stream in self.stream_buttons:
                self.stream_buttons[stream].config(state=tk.NORMAL, relief=tk.RAISED, bg="#bdc3c7")
        self.update_priority_display()
        self.update_next_button_state()

    def update_priority_display(self):
        for widget in self.priority_list_frame.winfo_children():
            widget.destroy()
        if self.user_profile["career_priority"]:
            for i, stream in enumerate(self.user_profile["career_priority"], 1):
                item_frame = tk.Frame(self.priority_list_frame, bg="white")
                item_frame.pack(fill=tk.X, anchor="w", pady=2)
                tk.Label(item_frame, text=f"{i}. {stream}", font=("Arial", 12), bg="white", fg=COLOR_BG_NAV).pack(side=tk.LEFT, padx=5)
                remove_btn = tk.Button(item_frame, text="Remove", font=("Arial", 8), command=lambda s=stream: self.remove_from_priority(s), bg="#e74c3c", fg="white", relief=tk.FLAT)
                remove_btn.pack(side=tk.RIGHT, padx=5)
        else:
            tk.Label(self.priority_list_frame, text="No priorities set.", font=("Arial", 12), bg="white", fg=COLOR_BG_NAV).pack(anchor="w", padx=5)

    def show_page_2(self):
        if not self.user_profile["career_priority"]:
            messagebox.showwarning("No Streams Selected", "Please select at least one career stream to proceed.")
            return

        self.page = 2
        self.clear_content_frame()
        self.update_nav_panel()
        page_frame = tk.Frame(self.content_frame, bg="white", padx=20, pady=20)
        page_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(page_frame, text="Step 2: Rate Your Engineering Interests", font=("Arial", 16, "bold"), bg="white").pack(pady=(0, 20))
        tk.Label(page_frame, text="Rate how much you would enjoy the following engineering tasks. Scale: 1-Not at All to 5-Extremely.", font=("Arial", 10), bg="white").pack(anchor="w", pady=5)
        
        tasks_canvas = tk.Canvas(page_frame, bg="white", highlightthickness=0)
        tasks_scrollbar = ttk.Scrollbar(page_frame, orient="vertical", command=tasks_canvas.yview)
        tasks_frame = tk.Frame(tasks_canvas, bg="white")
        tasks_frame.bind("<Configure>", lambda e: tasks_canvas.configure(scrollregion=tasks_canvas.bbox("all")))
        tasks_canvas.create_window((0, 0), window=tasks_frame, anchor="nw")
        tasks_canvas.configure(yscrollcommand=tasks_scrollbar.set)
        tasks_canvas.pack(side="left", fill="both", expand=True)
        tasks_scrollbar.pack(side="right", fill="y")
        
        self.task_ratings = {}
        for i, (task_name, related_streams) in enumerate(self.parent.ENGINEERING_TASKS.items()):
            frame = tk.Frame(tasks_frame, bg="white")
            frame.pack(fill=tk.X, pady=5)
            tk.Label(frame, text=f"{i+1}. {task_name}", font=("Arial", 12), bg="white", anchor="w", justify="left", wraplength=750).pack(side=tk.LEFT, padx=5)
            
            rating_var = tk.IntVar(value=0)
            self.task_ratings[task_name] = rating_var
            options_frame = tk.Frame(frame, bg="white")
            options_frame.pack(side=tk.RIGHT)
            for i in range(1, 6):
                tk.Radiobutton(options_frame, text=str(i), variable=rating_var, value=i, bg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=2)

        submit_button = tk.Button(self.content_frame, text="Generate Recommendation", font=("Arial", 12, "bold"), command=self.generate_recommendation, bg=COLOR_ANSWERED, fg=COLOR_BUTTON_TEXT)
        submit_button.pack(side=tk.BOTTOM, padx=10, pady=10, anchor="e")

    def generate_recommendation(self):
        user_input_raw = [var.get() for var in self.task_ratings.values()]
        if 0 in user_input_raw:
            messagebox.showwarning("Incomplete Ratings", "Please rate all engineering tasks before generating a recommendation.")
            return

        user_input = np.array(user_input_raw).reshape(1, -1)
        
        probabilities = ML_MODELS.career_model.predict_proba(user_input)[0]
        sorted_indices = np.argsort(probabilities)[::-1]
        
        top_recommendations = []
        for i in sorted_indices: 
            course = career_course_map[i]
            confidence = probabilities[i] * 100
            top_recommendations.append((course, confidence))
        
        predicted_course_id = sorted_indices[0]
        self.recommended_stream = career_course_map[predicted_course_id]
        confidence = probabilities[predicted_course_id] * 100

        self.parent.user_data['career_profiler_recommendation'] = self.recommended_stream
        self.parent.user_data['career_profiler_confidence'] = confidence
        self.parent.user_data['career_priority_list'] = self.user_profile["career_priority"]

        messagebox.showinfo(
            "Your Recommendation",
            f"Based on your task ratings, the best-fit engineering stream is:\n\n"
            f"✅ {self.recommended_stream}\n\n"
            f"(Confidence: {confidence:.2f}%)"
        )
        self.show_page_3(self.recommended_stream, confidence, top_recommendations)

    def show_page_3(self, recommended_stream, confidence, top_recommendations):
        self.page = 3
        self.clear_content_frame()
        self.update_nav_panel()
        result_frame = tk.Frame(self.content_frame, bg=COLOR_BG_CONTENT)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(result_frame, text="--- Your Interests Report ---", font=("Arial", 18, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack(pady=10)
        
        tk.Label(result_frame, text="\n--- Model-Based Recommendation (Interests) ---", font=("Arial", 14, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack()
        
        tk.Label(result_frame, 
                 text=f"Primary Recommendation: {recommended_stream} ({confidence:.2f}%)", 
                 font=("Arial", 13, "bold"), wraplength=700, justify="left", 
                 bg=COLOR_BG_CONTENT, fg=COLOR_ANSWERED).pack(pady=(10, 5))
                 
        for i, (course, conf) in enumerate(top_recommendations[:3]): # Show top 3 here
            tk.Label(result_frame, 
                     text=f"Rank {i+1}: {course} (Confidence: {conf:.2f}%)", 
                     font=("Arial", 12), wraplength=700, justify="left", 
                     bg=COLOR_BG_CONTENT, fg=COLOR_BG_NAV).pack(anchor="w", padx=20)
        
        continue_button = tk.Button(result_frame, text="Continue to Personality Assessment →", font=("Arial", 12, "bold"), 
                                     command=lambda: self.parent.show_personality_test(recommended_stream, self.user_profile["career_priority"]), 
                                     bg=COLOR_CURRENT_Q_NAV, fg=COLOR_BUTTON_TEXT)
        continue_button.pack(pady=20)


# ====================================================================
# PART 1.5: PERSONALITY ASSESSMENT (Detailed Report Version)
# ====================================================================
class PersonalityAssessmentPart:
    def __init__(self, parent, container_frame, recommended_stream, priority_list):
        self.parent = parent
        self.container_frame = container_frame
        self.recommended_stream = recommended_stream
        self.priority_list = priority_list
        self.reset_app()

    def reset_app(self):
        # Clear existing widgets
        for widget in self.container_frame.winfo_children():
            widget.destroy()

        self.q_ids = list(PERSONALITY_QUESTIONNAIRE.keys())
        self.index = 0
        self.answers = {}
        self.answer_var = tk.IntVar(value=0)
        
        self.build_layout()
        self.show_question()

    def build_layout(self):
        # Main Layout Frame
        self.main_split = tk.Frame(self.container_frame, bg=COLOR_BG_DARK)
        self.main_split.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self.side_pane = tk.Frame(self.main_split, bg=COLOR_BG_NAV, width=280)
        self.side_pane.pack(side=tk.LEFT, fill=tk.Y)
        self.side_pane.pack_propagate(False)

        tk.Label(
            self.side_pane, text="PERSONALITY", fg="white", bg=COLOR_BG_NAV,
            font=("Helvetica", 12, "bold")
        ).pack(pady=(20, 10))

        self.grid_frame = tk.Frame(self.side_pane, bg=COLOR_BG_NAV)
        self.grid_frame.pack(padx=10)

        self.q_btns = {}
        for i in self.q_ids:
            btn = tk.Button(
                self.grid_frame, text=str(i), width=3, font=("Helvetica", 9),
                relief="flat", bg="#34495E", fg="white",
                command=lambda x=i: self.jump(x)
            )
            row, col = (i - 1) // 5, (i - 1) % 5
            btn.grid(row=row, column=col, padx=3, pady=3)
            self.q_btns[i] = btn

        # Main Content Area
        self.content_pane = tk.Frame(self.main_split, bg=COLOR_BG_CONTENT)
        self.content_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Header with Progress Bar
        header = tk.Frame(self.content_pane, bg="white", height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="Psychometric Analysis", font=("Arial", 14, "bold"), bg="white", fg=COLOR_BG_DARK).pack(side=tk.LEFT, padx=20)

        self.progress = ttk.Progressbar(
            header, orient="horizontal", length=400, mode="determinate"
        )
        self.progress.pack(pady=25)

        # Question Card
        self.card = tk.Frame(
            self.content_pane, bg="white", padx=50, pady=50,
            highlightbackground="#DCDCDC", highlightthickness=1
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        self.lbl_trait = tk.Label(
            self.card, text="TRAIT", fg="#3498DB", bg="white",
            font=("Helvetica", 10, "bold")
        )
        self.lbl_trait.pack(anchor="w")

        self.lbl_q_text = tk.Label(
            self.card, text="", bg="white", fg="#2C3E50",
            font=("Helvetica", 22), wraplength=600, justify="left"
        )
        self.lbl_q_text.pack(pady=(10, 40), anchor="w")

        self.opt_frame = tk.Frame(self.card, bg="white")
        self.opt_frame.pack(fill=tk.X)

        options = [
            ("Strongly Disagree", 1), ("Disagree", 2), ("Neutral", 3),
            ("Agree", 4), ("Strongly Agree", 5)
        ]

        for text, val in options:
            tk.Radiobutton(
                self.opt_frame, text=text, value=val, variable=self.answer_var,
                indicatoron=0, font=("Helvetica", 11), bg="#F1F3F4",
                selectcolor="#3498DB", fg="#2C3E50", padx=20, pady=15,
                width=20, borderwidth=0, command=self.save_and_next
            ).pack(pady=5, fill=tk.X)

        # Navigation Buttons
        nav_frame = tk.Frame(self.content_pane, bg=COLOR_BG_CONTENT)
        nav_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=50, pady=30)

        tk.Button(
            nav_frame, text="← Previous", font=("Helvetica", 11), bg="white",
            relief="flat", padx=20, command=self.prev_q
        ).pack(side=tk.LEFT)

        tk.Button(
            nav_frame, text="Finish Personality Test", font=("Helvetica", 11, "bold"),
            bg="#2ECC71", fg="white", relief="flat", padx=20, pady=10,
            command=self.finish
        ).pack(side=tk.RIGHT)

    def show_question(self):
        q_id = self.q_ids[self.index]
        trait_code, text, _ = PERSONALITY_QUESTIONNAIRE[q_id]
        self.lbl_trait.config(
            text=f"QUESTION {q_id} / {len(self.q_ids)} — {PERSONALITY_TRAITS[trait_code]['name'].upper()}"
        )
        self.lbl_q_text.config(text=text)
        self.progress['value'] = (len(self.answers) / len(self.q_ids)) * 100
        self.answer_var.set(self.answers.get(q_id, 0))
        self.update_sidebar()

    def save_and_next(self):
        self.answers[self.q_ids[self.index]] = self.answer_var.get()
        if self.index < len(self.q_ids) - 1:
            self.index += 1
            self.container_frame.after(200, self.show_question)
        else:
            self.update_sidebar()

    def update_sidebar(self):
        curr = self.q_ids[self.index]
        for q, btn in self.q_btns.items():
            if q == curr:
                btn.config(bg="#3498DB", fg="white", font=("Helvetica", 10, "bold"))
            elif q in self.answers:
                btn.config(bg="#2ECC71", fg="white")
            else:
                btn.config(bg="#34495E", fg="white")

    def prev_q(self):
        if self.index > 0:
            self.index -= 1
            self.show_question()

    def jump(self, q_id):
        self.index = self.q_ids.index(q_id)
        self.show_question()

    def finish(self):
        if len(self.answers) < len(self.q_ids):
            if not messagebox.askyesno(
                "Incomplete",
                f"Missing {len(self.q_ids) - len(self.answers)} answers. Proceed?"
            ):
                return
        self.show_personality_report()

    def show_personality_report(self):
        # 1. Scoring Logic
        raw = defaultdict(list)
        for q, val in self.answers.items():
            trait, _, rev = PERSONALITY_QUESTIONNAIRE[q]
            if val == 0: val = 3
            score = (6 - val) if rev else val
            raw[trait].append(score)

        results = {}
        for t, vals in raw.items():
            avg = sum(vals) / len(vals) if vals else 3
            results[t] = {
                "name": PERSONALITY_TRAITS[t]["name"],
                "score": ((avg - 1) / 4) * 100,
                "color": PERSONALITY_TRAITS[t]["color"]
            }

        # 2. Save Data
        self.parent.user_data['personality_results'] = results
        
        top_trait = sorted(results.items(), key=lambda x: x[1]['score'], reverse=True)[0][0]
        archetypes = {
            'O': ("The Visionary", "Driven by curiosity, abstract ideas, and innovation."),
            'C': ("The Architect", "Characterized by high discipline, order, and reliability."),
            'E': ("The Catalyst", "Thrives on social energy, leadership, and excitement."),
            'A': ("The Harmonizer", "Defined by profound empathy and cooperation."),
            'N': ("The Sentinel", "Possesses high sensitivity and environmental awareness.")
        }
        arch_title, arch_desc = archetypes.get(top_trait, ("Balanced", "A well-rounded profile."))
        self.parent.user_data['personality_archetype'] = f"{arch_title} - {arch_desc}"

        # 3. Build Detailed Report UI
        for widget in self.container_frame.winfo_children():
            widget.destroy()

        container = tk.Frame(self.container_frame, bg=COLOR_BG_CONTENT, padx=40, pady=30)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(container, text="PERSONALITY ANALYSIS REPORT", font=("Helvetica", 10, "bold"), fg="#3498DB", bg=COLOR_BG_CONTENT).pack()
        tk.Label(container, text=f"Archetype: {arch_title}", font=("Helvetica", 26, "bold"), fg="#2C3E50", bg=COLOR_BG_CONTENT).pack(pady=5)
        tk.Label(container, text=arch_desc, font=("Helvetica", 12, "italic"), fg="#7F8C8D", bg=COLOR_BG_CONTENT).pack(pady=(0, 20))

        content_split = tk.Frame(container, bg=COLOR_BG_CONTENT)
        content_split.pack(fill=tk.BOTH, expand=True)

        # --- LEFT: Chart ---
        chart_wrap = tk.Frame(content_split, bg="white", padx=15, pady=15, relief="flat", highlightbackground="#DCDCDC", highlightthickness=1)
        chart_wrap.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        if MATPLOTLIB_AVAILABLE:
            fig = Figure(figsize=(5, 5), dpi=95)
            ax = fig.add_subplot(111)
            
            names = [results[k]["name"] for k in results]
            scores = [results[k]["score"] for k in results]
            colors = [results[k]["color"] for k in results]
            
            y_pos = range(len(names))
            ax.barh(y_pos, scores, color=colors)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(names)
            ax.set_xlim(0, 100)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, chart_wrap)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            tk.Label(chart_wrap, text="Chart unavailable", bg="white").pack()

        # --- RIGHT: Text Report ---
        text_wrap = tk.Frame(content_split, bg="white", padx=20, pady=20, highlightbackground="#DCDCDC", highlightthickness=1)
        text_wrap.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))

        tk.Label(text_wrap, text="Character Breakdown", font=("Helvetica", 14, "bold"), bg="white", fg="#3498DB").pack(anchor="w", pady=(0, 10))
        
        report_text = tk.Text(text_wrap, wrap=tk.WORD, font=("Helvetica", 10), bg="white", bd=0, height=15)
        report_text.pack(fill=tk.BOTH, expand=True)

        features = {
            'O': "OPENNESS: Measures 'Intellect' (abstract ideas) and 'Aesthetics' (creativity).",
            'C': "CONSCIENTIOUSNESS: Measures 'Industriousness' (grit) and 'Orderliness' (organization).",
            'E': "EXTRAVERSION: Measures 'Enthusiasm' (sociability) and 'Assertiveness' (leadership).",
            'A': "AGREEABLENESS: Measures 'Compassion' (empathy) and 'Politeness' (social harmony).",
            'N': "NEUROTICISM: Measures 'Withdrawal' (anxiety) and 'Volatility' (reactivity)."
        }

        report_text.tag_configure("bold", font=("Helvetica", 10, "bold"))
        for code, f_text in features.items():
            t_part, d_part = f_text.split(":", 1)
            report_text.insert(tk.END, f"• {t_part}:", "bold")
            report_text.insert(tk.END, f"{d_part}\nScore: {results[code]['score']:.1f}%\n\n")
        
        report_text.config(state=tk.DISABLED)

        # --- BOTTOM: Suggested Careers ---
        career_box = tk.Frame(container, bg="#EBF5FB", padx=20, pady=15)
        career_box.pack(fill=tk.X, pady=(20, 0))
        
        careers = {
            'O': "Design, Research, AI Development, Architecture, Creative Arts", 
            'C': "Finance, Engineering, Law, Project Management, Data Science",
            'E': "Sales, Public Relations, Management, Politics, Hospitality", 
            'A': "Healthcare, HR, Teaching, Social Work, Counseling",
            'N': "Quality Assurance, Risk Analysis, Writing, Cybersecurity, Research"
        }
        tk.Label(career_box, text=f"Suggested Career Paths based on Dominant Trait ({PERSONALITY_TRAITS[top_trait]['name']}):", font=("Helvetica", 10), bg="#EBF5FB").pack()
        tk.Label(career_box, text=careers.get(top_trait, 'General Management'), font=("Helvetica", 12, "bold"), bg="#EBF5FB", fg="#2E86C1").pack()

        # --- Footer ---
        footer = tk.Frame(container, bg=COLOR_BG_CONTENT)
        footer.pack(fill=tk.X, pady=20)
        
        tk.Button(footer, text="Continue to Aptitude Test →", 
                  command=lambda: self.parent.show_aptitude_test(self.recommended_stream, self.priority_list), 
                  bg=COLOR_ANSWERED, fg="white", relief="flat", padx=20, pady=10, font=("Arial", 12, "bold")).pack()


# ====================================================================
# Part 2: Aptitude Test (Skills)
# ====================================================================
class AptitudeTestPart2:
    def __init__(self, parent, container_frame, recommended_stream, priority_list):
        self.parent = parent
        self.container_frame = container_frame
        self.recommended_stream = recommended_stream
        self.priority_list = priority_list
        self.question_index = 0
        self.answers = {}
        self.review_questions = set()
        self.questions = self.prepare_questions()
        self.selected_option = tk.StringVar()
        self.current_question = None
        self.start_time = time.time()
        self.timer_label = None
        self.timer_id = None 

        self.build_widgets()
        self.update_timer()
        self.show_question()

    def update_timer(self):
        elapsed_time = int(time.time() - self.start_time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_str = f"Time: {minutes:02d}:{seconds:02d}"
        if self.timer_label:
            self.timer_label.config(text=time_str)
        
        self.timer_id = self.container_frame.after(1000, self.update_timer)

    def cancel_timer(self):
        if self.timer_id is not None:
            self.container_frame.after_cancel(self.timer_id)
            self.timer_id = None
            
    def prepare_questions(self):
        all_selected_questions = []
        self.section_question_map = defaultdict(list)
        self.section_question_indices = {}
        
        available_categories = [cat for cat in sorted(QUESTIONS.keys()) if QUESTIONS[cat]]
        QUESTIONS_PER_CATEGORY = 7
        
        for section in available_categories:
            qs = QUESTIONS[section]
            
            if section in APTITUDE_MODEL_CATEGORIES:
                k = min(QUESTIONS_PER_CATEGORY, len(qs)) 
                if k == 0: continue
            
                qs_selected = random.sample(qs, k)
                for q in qs_selected:
                    all_selected_questions.append({**q, "category": section})

        random.shuffle(all_selected_questions)

        for idx, q in enumerate(all_selected_questions):
            section = q['category']
            self.section_question_map[section].append(q)
            i = len(self.section_question_map[section]) - 1
            self.section_question_indices[(section, i)] = idx
            
        return all_selected_questions

    def build_widgets(self):
        for widget in self.container_frame.winfo_children():
            widget.destroy()

        self.main_frame = tk.Frame(self.container_frame, bg=COLOR_BG_DARK)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.grid_columnconfigure(0, weight=0, minsize=250)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        self.create_navigation_panel()
        self.create_content_panel()
    
    def create_navigation_panel(self):
        self.nav_frame = tk.Frame(self.main_frame, bg=COLOR_BG_NAV, padx=10, pady=10)
        self.nav_frame.grid(row=0, column=0, sticky="nsew") 

        nav_canvas = tk.Canvas(self.nav_frame, bg=COLOR_BG_NAV, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.nav_frame, orient="vertical", command=nav_canvas.yview)
        scrollable_frame = tk.Frame(nav_canvas, bg=COLOR_BG_NAV)
        
        scrollable_frame.bind("<Configure>", lambda e: nav_canvas.configure(scrollregion=nav_canvas.bbox("all")))
        nav_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        nav_canvas.configure(yscrollcommand=scrollbar.set)
        
        nav_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.question_buttons = {}
        self.dropdown_labels = {}
        self.section_content_frames = {}
        
        for section in sorted(self.section_question_map.keys()):
            header_frame = tk.Frame(scrollable_frame, bg=COLOR_BG_NAV)
            header_frame.pack(fill=tk.X, pady=(10, 0), padx=5)

            dropdown_label = tk.Label(header_frame, text=f"▶ {section}", font=("Arial", 12, "bold"), bg=COLOR_BG_NAV, fg=COLOR_BUTTON_TEXT, anchor="w")
            dropdown_label.pack(side=tk.LEFT, padx=5)
            dropdown_label.bind("<Button-1>", lambda event, s=section: self.toggle_dropdown(s))
            self.dropdown_labels[section] = dropdown_label
            
            q_info_label = tk.Label(header_frame, text=f"({len(self.section_question_map[section])} Qs)", font=("Arial", 9), fg="lightgray", bg=COLOR_BG_NAV, anchor="w")
            q_info_label.pack(side=tk.LEFT, padx=5)
            
            q_frame = tk.Frame(scrollable_frame, bg=COLOR_BG_NAV)
            q_frame.pack(fill=tk.X, padx=5)
            self.section_content_frames[section] = q_frame
            q_frame.pack_forget() 

            for i in range(len(self.section_question_map[section])):
                global_idx = self.section_question_indices.get((section, i))
                if global_idx is not None:
                    btn = tk.Button(q_frame, text=f"{i+1}", width=3, relief=tk.RAISED, fg=COLOR_BUTTON_TEXT, bg=COLOR_UNANSWERED)
                    btn.config(command=lambda idx=global_idx: self.goto_question(idx))
                    btn.grid(row=i//5, column=i%5, padx=2, pady=2)
                    self.question_buttons[global_idx] = btn
        
        self.add_legend_item(self.nav_frame, COLOR_CURRENT_Q_NAV, "Current Question")
        self.add_legend_item(self.nav_frame, COLOR_ANSWERED, "Answered")
        self.add_legend_item(self.nav_frame, COLOR_REVIEW, "Marked for Review")
        self.add_legend_item(self.nav_frame, COLOR_UNANSWERED, "Unanswered")

    def add_legend_item(self, parent, color, text):
        frame = tk.Frame(parent, bg=COLOR_BG_NAV)
        frame.pack(fill=tk.X, padx=5, pady=2, anchor="w")
        tk.Label(frame, bg=color, width=2, height=1, relief=tk.SUNKEN).pack(side=tk.LEFT)
        tk.Label(frame, text=text, fg=COLOR_BUTTON_TEXT, bg=COLOR_BG_NAV, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

    def toggle_dropdown(self, section):
        frame = self.section_content_frames.get(section)
        label = self.dropdown_labels.get(section)
        if frame and label:
            if frame.winfo_ismapped():
                frame.pack_forget()
                label.config(text=f"▶ {section}")
            else:
                frame.pack(fill=tk.X)
                label.config(text=f"▼ {section}")

    def create_content_panel(self):
        self.content_frame = tk.Frame(self.main_frame, bg=COLOR_BG_CONTENT)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.topbar = tk.Frame(self.content_frame, bg=COLOR_BG_CONTENT)
        self.topbar.pack(fill=tk.X, anchor="n")
        
        tk.Label(self.topbar, text=f"General Aptitude Test ({len(self.questions)} Questions)", font=("Arial", 14, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack(side=tk.LEFT, padx=10, pady=5)
        
        self.timer_label = tk.Label(self.topbar, text="Time: 00:00", font=("Arial", 14, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_UNANSWERED)
        self.timer_label.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.finish_button = tk.Button(self.topbar, text="Finish Test", font=("Arial", 12, "bold"), bg=COLOR_UNANSWERED, fg=COLOR_BUTTON_TEXT, command=self.finish_test, relief=tk.FLAT)
        self.finish_button.pack(side=tk.RIGHT, padx=10, pady=5)

        self.question_area = tk.Frame(self.content_frame, bg="white", padx=20, pady=20)
        self.question_area.pack(pady=(10, 0), fill=tk.BOTH, expand=True)

        self.question_title_label = tk.Label(self.question_area, text="", font=("Arial", 14, "bold"), bg="white", anchor="w")
        self.question_title_label.pack(anchor="w")

        self.question_text_label = tk.Label(self.question_area, text="", font=("Arial", 15), wraplength=750, justify="left", bg="white")
        self.question_text_label.pack(pady=(10, 20), anchor="w")

        self.options_frame = tk.Frame(self.question_area, bg="white")
        self.options_frame.pack(anchor="w", pady=(0, 10), padx=20)
        self.selected_option.trace_add("write", lambda *args: self.save_answer())
        self.option_radiobuttons = []

        self.control_buttons_frame = tk.Frame(self.content_frame, bg=COLOR_BG_CONTENT)
        self.control_buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        self.prev_button = tk.Button(self.control_buttons_frame, text="← Previous", font=("Arial", 12), command=self.prev_question, relief=tk.FLAT, bg=COLOR_BG_NAV, fg=COLOR_BUTTON_TEXT)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.next_button = tk.Button(self.control_buttons_frame, text="Next →", font=("Arial", 12), command=self.next_question_manual, relief=tk.FLAT, bg=COLOR_CURRENT_Q_NAV, fg=COLOR_BUTTON_TEXT)
        self.next_button.pack(side=tk.RIGHT, padx=5)
        self.review_button = tk.Button(self.control_buttons_frame, text="Mark for Review", font=("Arial", 12), command=self.mark_review, relief=tk.FLAT, bg=COLOR_REVIEW, fg="black")
        self.review_button.pack(side=tk.RIGHT, padx=5)
    
    def update_nav_panel(self):
        for global_idx, btn in self.question_buttons.items():
            if global_idx >= len(self.questions):
                continue
            q = self.questions[global_idx]
            key = (q['category'], q['id'])

            if key in self.answers:
                btn.config(bg=COLOR_ANSWERED, fg=COLOR_BUTTON_TEXT)
            elif global_idx in self.review_questions:
                btn.config(bg=COLOR_REVIEW, fg="black")
            else:
                btn.config(bg=COLOR_UNANSWERED, fg=COLOR_BUTTON_TEXT)

            if global_idx == self.question_index:
                btn.config(relief=tk.SUNKEN, bg=COLOR_CURRENT_Q_NAV)
            else:
                btn.config(relief=tk.RAISED)

        if self.question_index < len(self.questions):
            if self.question_index in self.review_questions:
                self.review_button.config(text="Unmark Review", bg=COLOR_REVIEW, fg="black")
            else:
                self.review_button.config(text="Mark for Review", bg=COLOR_BG_NAV, fg="white")

        self.prev_button.config(state=tk.NORMAL if self.question_index > 0 else tk.DISABLED)
        self.next_button.config(text="Next →" if self.question_index < len(self.questions) - 1 else "End Test", 
                                command=self.next_question_manual if self.question_index < len(self.questions) - 1 else self.finish_test_prompt)

    def goto_question(self, global_idx):
        self.save_answer()
        self.question_index = global_idx
        self.show_question()

    def show_question(self):
        if self.question_index >= len(self.questions):
            self.finish_test()
            return
        
        self.current_question = self.questions[self.question_index]
        q = self.current_question
        
        self.question_title_label.config(text=f"[{q['category']}]")
        self.question_text_label.config(text=f"Question {self.question_index + 1} of {len(self.questions)}: {q['q']}")

        for rb in self.option_radiobuttons:
            rb.destroy()
        self.option_radiobuttons.clear()

        global CORRECT_ANSWERS
        saved_answer = self.answers.get((q['category'], q['id']), "")
        self.selected_option.set(saved_answer)
        
        for opt_key, opt_val in q['options'].items():
            rb = tk.Radiobutton(
                self.options_frame, text=f"{opt_key}) {opt_val}", variable=self.selected_option,
                value=opt_key, font=("Arial", 12), anchor="w", bg="white", activebackground="#bdc3c7",
                selectcolor=COLOR_CURRENT_Q_NAV, indicatoron=0, width=70, relief=tk.FLAT
            )
            rb.pack(anchor="w", pady=2)
            self.option_radiobuttons.append(rb)

        self.update_nav_panel()

    def save_answer(self, *args):
        if self.current_question is None:
            return
        
        q = self.current_question
        key = (q['category'], q['id'])
        selected = self.selected_option.get()
        
        if selected:
            self.answers[key] = selected
        
        self.update_nav_panel()
        
    def next_question_manual(self):
        self.save_answer()
        self.question_index += 1
        self.show_question()

    def prev_question(self):
        self.save_answer()
        self.question_index -= 1
        self.show_question()
        
    def mark_review(self):
        global_idx = self.question_index
        if global_idx in self.review_questions:
            self.review_questions.remove(global_idx)
        else:
            self.review_questions.add(global_idx)
        self.update_nav_panel()

    def finish_test_prompt(self):
        self.save_answer()
        unanswered_count = len(self.questions) - len(self.answers)
        if unanswered_count > 0:
            if messagebox.askyesno("Confirm Finish", f"You have {unanswered_count} unanswered questions. Are you sure you want to finish?"):
                self.show_result()
        else:
            self.show_result()

    def finish_test(self):
        if messagebox.askyesno("Finish Test", "Are you sure you want to finish the test and see your results? You cannot return."):
            self.show_result()

    def show_result(self):
        self.cancel_timer() 

        if self.main_frame:
            self.main_frame.destroy()

        result_frame = tk.Frame(self.container_frame, bg=COLOR_BG_CONTENT)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(result_frame, text="--- Aptitude Test Results ---", font=("Arial", 18, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack(pady=10)

        scores = defaultdict(int)
        section_answered = defaultdict(int)
        for q in self.questions:
            section = q['category']
            question_id = q['id']
            key = (section, question_id)
            if key in self.answers:
                section_answered[section] += 1
                if self.answers[key] == CORRECT_ANSWERS[section].get(question_id):
                    scores[section] += 1
        
        user_scores_array = np.array([
            scores[cat] / len(self.section_question_map.get(cat, [1])) if len(self.section_question_map.get(cat, [])) > 0 else 0
            for cat in APTITUDE_MODEL_CATEGORIES
        ]).reshape(1, -1)
        
        all_probabilities = ML_MODELS.aptitude_model.predict_proba(user_scores_array)[0]
        
        stream_confidence_map = {
            aptitude_course_map[i]: all_probabilities[i] * 100
            for i in range(len(all_probabilities))
        }

        predicted_aptitude_id = np.argmax(all_probabilities)
        aptitude_confidence = all_probabilities[predicted_aptitude_id]

        # Save Part 2 results to user_data
        self.parent.user_data['aptitude_recommendation'] = aptitude_course_map[predicted_aptitude_id]
        self.parent.user_data['aptitude_confidence_max'] = aptitude_confidence * 100
        self.parent.user_data['aptitude_confidence_map'] = stream_confidence_map
        self.parent.user_data['aptitude_scores'] = dict(scores)
        
        score_frame = tk.Frame(result_frame, bg=COLOR_BG_CONTENT)
        score_frame.pack(pady=10)
        tk.Label(score_frame, text="\n--- Your Skills Score ---", font=("Arial", 14, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack()
        
        for section in sorted(self.section_question_map.keys()):
            section_q_count = len(self.section_question_map.get(section, []))
            tk.Label(score_frame, text=f"   {section}: {scores[section]}/{section_q_count}", font=("Arial", 12), bg=COLOR_BG_CONTENT, fg=COLOR_BG_NAV).pack(anchor="w")

        global MATPLOTLIB_AVAILABLE
        if MATPLOTLIB_AVAILABLE:
            try:
                fig = Figure(figsize=(8, 4), dpi=100)
                ax = fig.add_subplot(111)
                sections_present = sorted(self.section_question_map.keys())
                correct = [scores[s] for s in sections_present]
                total_answered = [section_answered[s] for s in sections_present]
                incorrect = [total_answered[i] - correct[i] for i in range(len(sections_present))]
                
                ax.bar(sections_present, correct, label='Correct', color=COLOR_ANSWERED)
                ax.bar(sections_present, incorrect, bottom=correct, label='Incorrect', color=COLOR_UNANSWERED)
                
                ax.set_ylabel('Number of Questions')
                ax.set_title('Answer Breakdown per Skill')
                ax.set_yticks(range(1, 8))
                ax.tick_params(axis='x', rotation=45)
                ax.legend()
                fig.tight_layout()

                canvas = FigureCanvasTkAgg(fig, master=result_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(pady=20)
                
            except Exception as ex:
                tk.Label(result_frame, text=f"(Matplotlib Error: {ex})", fg="red", bg=COLOR_BG_CONTENT).pack()
        else:
            tk.Label(result_frame, text="(Matplotlib not available for chart)", fg="red", bg=COLOR_BG_CONTENT).pack()
        
        final_button = tk.Button(result_frame, text="View Final Combined Recommendation →", font=("Arial", 12, "bold"), 
                                     command=self.parent.show_final_recommendation, 
                                     bg=COLOR_CURRENT_Q_NAV, fg=COLOR_BUTTON_TEXT)
        final_button.pack(pady=20)

# ====================================================================
# --- Specialized Aptitude Test Class ---
# ====================================================================
class SpecializedAptitudeTest(tk.Frame): 
    def __init__(self, parent, container_frame, selected_course, full_report_data):
        self.parent = parent
        self.container_frame = container_frame
        self.selected_course = selected_course
        self.full_report_data = full_report_data
        
        self.question_index = 0
        self.answers = {}
        self.review_questions = set()
        self.questions = self.prepare_questions()
        self.selected_option = tk.StringVar()
        self.current_question = None
        self.start_time = time.time()
        self.timer_label = None
        self.timer_id = None 

        self.build_widgets()
        self.update_timer()
        self.show_question()
    
    def update_timer(self):
        elapsed_time = int(time.time() - self.start_time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_str = f"Time: {minutes:02d}:{seconds:02d}"
        if self.timer_label:
            self.timer_label.config(text=time_str)
        self.timer_id = self.container_frame.after(1000, self.update_timer)

    def cancel_timer(self):
        if self.timer_id is not None:
            self.container_frame.after_cancel(self.timer_id)
            self.timer_id = None
            
    def prepare_questions(self):
        LOCAL_COURSE_TO_SKILLS_MAP = {
            "Computer Science (CSE)": ["Algorithmic", "Computational", "Logical", "System", "Critical", "Abstract", "Creative"],
            "Information Technology (IT)": ["Algorithmic", "System", "Logical", "Computational", "Critical", "Abstract", "Creative"],
            "Electronics & Communication (ECE)": ["System", "Critical", "Logical", "Algorithmic", "Computational", "Abstract", "Creative"],
            "Electrical & Electronics (EEE)": ["System", "Critical", "Computational", "Algorithmic", "Logical", "Abstract", "Creative"],
            "Mechanical Engineering (ME)": ["System", "Abstract", "Critical", "Algorithmic", "Computational", "Logical", "Creative"],
            "Aerospace Engineering": ["System", "Abstract", "Computational", "Algorithmic", "Critical", "Logical", "Creative"],
            "Civil Engineering (CE)": ["Abstract", "System", "Critical", "Algorithmic", "Computational", "Logical", "Creative"],
            "Chemical Engineering (CH)": ["System", "Logical", "Critical", "Algorithmic", "Computational", "Abstract", "Creative"],
            "Biotechnology": ["Logical", "Critical", "Creative", "Algorithmic", "Computational", "System", "Abstract"],
            "Industrial Engineering": ["System", "Logical", "Algorithmic", "Computational", "Critical", "Abstract", "Creative"]
        }
        
        relevant_skills = LOCAL_COURSE_TO_SKILLS_MAP.get(self.selected_course, ["Logical", "Critical", "System"])
        QUESTIONS_PER_SKILL = 7
        all_selected_questions = []
        self.section_question_map = defaultdict(list)
        self.section_question_indices = {}
        
        for section in relevant_skills:
            if section in QUESTIONS:
                qs = QUESTIONS[section]
                k = min(QUESTIONS_PER_SKILL, len(qs))
                if k == 0: continue
                
                qs_selected = random.sample(qs, k)
                for q in qs_selected:
                    all_selected_questions.append({**q, "category": section})

        random.shuffle(all_selected_questions)

        for idx, q in enumerate(all_selected_questions):
            section = q['category']
            self.section_question_map[section].append(q)
            i = len(self.section_question_map[section]) - 1
            self.section_question_indices[(section, i)] = idx
            
        return all_selected_questions

    def build_widgets(self):
        for widget in self.container_frame.winfo_children():
            widget.destroy()

        self.main_frame = tk.Frame(self.container_frame, bg=COLOR_BG_DARK)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.grid_columnconfigure(0, weight=0, minsize=250)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        self.nav_frame = tk.Frame(self.main_frame, bg=COLOR_BG_NAV, padx=10, pady=10)
        self.nav_frame.grid(row=0, column=0, sticky="nsew") 

        self.content_frame = tk.Frame(self.main_frame, bg=COLOR_BG_CONTENT)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.topbar = tk.Frame(self.content_frame, bg=COLOR_BG_CONTENT)
        self.topbar.pack(fill=tk.X, anchor="n")
        
        title_text = f"Specialized Test: {self.selected_course} ({len(self.questions)} Qs)"
        tk.Label(self.topbar, text=title_text, font=("Arial", 14, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack(side=tk.LEFT, padx=10, pady=5)
        
        self.timer_label = tk.Label(self.topbar, text="Time: 00:00", font=("Arial", 14, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_UNANSWERED)
        self.timer_label.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.finish_button = tk.Button(self.topbar, text="Finish Test", font=("Arial", 12, "bold"), bg=COLOR_UNANSWERED, fg=COLOR_BUTTON_TEXT, command=self.finish_test_prompt, relief=tk.FLAT)
        self.finish_button.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.question_area = tk.Frame(self.content_frame, bg="white", padx=20, pady=20)
        self.question_area.pack(pady=(10, 0), fill=tk.BOTH, expand=True)

        self.question_text_label = tk.Label(self.question_area, text="Question text here", font=("Arial", 15), wraplength=750, justify="left", bg="white")
        self.question_text_label.pack(pady=(10, 20), anchor="w")

        self.options_frame = tk.Frame(self.question_area, bg="white")
        self.options_frame.pack(anchor="w", pady=(0, 10), padx=20)
        self.selected_option.trace_add("write", lambda *args: self.save_answer())
        
        self.control_buttons_frame = tk.Frame(self.content_frame, bg=COLOR_BG_CONTENT)
        self.control_buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Simplified navigation buttons
        tk.Button(self.control_buttons_frame, text="← Previous", font=("Arial", 12), command=lambda: self.goto_question(max(0, self.question_index - 1)), relief=tk.FLAT, bg=COLOR_BG_NAV, fg=COLOR_BUTTON_TEXT).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_buttons_frame, text="Next →", font=("Arial", 12), command=lambda: self.goto_question(min(len(self.questions) - 1, self.question_index + 1)), relief=tk.FLAT, bg=COLOR_CURRENT_Q_NAV, fg=COLOR_BUTTON_TEXT).pack(side=tk.RIGHT, padx=5)

    def goto_question(self, idx):
        self.save_answer()
        self.question_index = idx
        self.show_question()
        
    def save_answer(self, *args):
        if self.current_question is None: return
        key = (self.current_question['category'], self.current_question['id'])
        selected = self.selected_option.get()
        if selected: self.answers[key] = selected

    def show_question(self):
        if self.question_index >= len(self.questions): return
        q = self.questions[self.question_index]
        self.current_question = q
        
        # Clear old options
        for widget in self.options_frame.winfo_children(): widget.destroy()

        self.question_text_label.config(text=f"Question {self.question_index + 1} of {len(self.questions)}: {q['q']}")
        saved_answer = self.answers.get((q['category'], q['id']), "")
        self.selected_option.set(saved_answer)
        
        for opt_key, opt_val in q['options'].items():
            tk.Radiobutton(self.options_frame, text=f"{opt_key}) {opt_val}", variable=self.selected_option,
                           value=opt_key, font=("Arial", 12), anchor="w", bg="white").pack(anchor="w", pady=2)

    def finish_test_prompt(self):
        self.save_answer()
        unanswered_count = len(self.questions) - len(self.answers)
        if unanswered_count > 0:
            if messagebox.askyesno("Confirm Finish", f"You have {unanswered_count} unanswered questions. Are you sure you want to finish this specialized test?"):
                self.show_specialized_result()
        else:
            self.show_specialized_result()

    def show_specialized_result(self):
        self.cancel_timer() 

        scores = defaultdict(int)
        for q in self.questions:
            section, q_id = q['category'], q['id']
            key = (section, q_id)
            if key in self.answers:
                 if self.answers[key] == CORRECT_ANSWERS[section].get(q_id):
                    scores[section] += 1
        
        self.parent.show_specialized_test_results(
            self.selected_course,
            scores,
            self.section_question_map,
            self.full_report_data
        )


# ====================================================================
# --- MAIN APPLICATION MANAGER ---
# ====================================================================
class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Engineering Career Assessment")
        self.root.geometry("1200x850") 
        self.root.configure(bg=COLOR_BG_DARK)
        self.container = tk.Frame(root, bg=COLOR_BG_DARK)
        self.container.pack(fill=tk.BOTH, expand=True)
        self.user_data = {} 
        
        self.ENGINEERING_TASKS = ENGINEERING_TASKS
        
        self.start_assessment()

    def start_assessment(self):
        self.current_part = UserProfileSetup(self, self.container) 

    def show_career_profiler(self):
        self.current_part = CareerProfilerPart1(self, self.container) 
        
    def show_personality_test(self, recommended_stream, priority_list):
        self.current_part = PersonalityAssessmentPart(self, self.container, recommended_stream, priority_list)

    def show_aptitude_test(self, recommended_stream, priority_list):
        self.current_part = AptitudeTestPart2(self, self.container, recommended_stream, priority_list) 

    # --- FINAL REPORT GENERATION ---
    def show_final_recommendation(self):
        # 1. Update Data with Time
        self.user_data['submission_timestamp'] = time.time()
        self.user_data['submission_date'] = time.ctime()

        # 2. AUTO-SAVE TO MONGODB (Background Thread)
        if users_collection is not None:
            threading.Thread(target=self.save_to_mongo, args=(self.user_data,), daemon=True).start()

        # Gather UI Data
        user_name = self.user_data.get('name', 'User')
        user_class = self.user_data.get('class', 'N/A')
        preferred_course = self.user_data.get('preferred_course', 'N/A')
        career_rec = self.user_data.get('career_profiler_recommendation', 'N/A')
        personality_archetype = self.user_data.get('personality_archetype', 'N/A')
        personality_results = self.user_data.get('personality_results', {})
        aptitude_confidence_map = self.user_data.get('aptitude_confidence_map', {})
        
        # UI Construction
        for widget in self.container.winfo_children():
            widget.destroy()
        
        canvas = tk.Canvas(self.container, bg=COLOR_BG_CONTENT)
        scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLOR_BG_CONTENT)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- REPORT HEADER ---
        header_frame = tk.Frame(scrollable_frame, bg=COLOR_BG_DARK, pady=20)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="COMPREHENSIVE CAREER REPORT", font=("Arial", 22, "bold"), fg="white", bg=COLOR_BG_DARK).pack()
        tk.Label(header_frame, text=f"Prepared for: {user_name} | Class: {user_class}", font=("Arial", 12), fg="lightgray", bg=COLOR_BG_DARK).pack()

        # --- SECTION 1: PERSONALITY PROFILE ---
        p_frame = tk.LabelFrame(scrollable_frame, text="1. Psychometric Profile", font=("Arial", 14, "bold"), bg="white", padx=15, pady=15)
        p_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(p_frame, text=f"Archetype: {personality_archetype}", font=("Arial", 16, "bold"), fg=COLOR_CURRENT_Q_NAV, bg="white").pack(anchor="w")
        
        traits_text = ""
        for code, data in personality_results.items():
            traits_text += f"• {data['name']}: {data['score']:.1f}%\n"
        
        tk.Label(p_frame, text=traits_text, font=("Arial", 11), bg="white", justify="left").pack(anchor="w", pady=5)
        
        # --- SECTION 2: CAREER INTERESTS ---
        i_frame = tk.LabelFrame(scrollable_frame, text="2. Career Interest Analysis", font=("Arial", 14, "bold"), bg="white", padx=15, pady=15)
        i_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(i_frame, text=f"Interest-Based Recommendation: {career_rec}", font=("Arial", 13, "bold"), bg="white").pack(anchor="w")
        tk.Label(i_frame, text=f"Stated Preference: {preferred_course}", font=("Arial", 11), bg="white").pack(anchor="w")

        # --- SECTION 3: APTITUDE & SKILLS ---
        a_frame = tk.LabelFrame(scrollable_frame, text="3. Aptitude & Market Fit", font=("Arial", 14, "bold"), bg="white", padx=15, pady=15)
        a_frame.pack(fill=tk.X, padx=20, pady=10)
        
        pref_conf = 0
        if preferred_course in aptitude_confidence_map:
            pref_conf = aptitude_confidence_map[preferred_course]
        else:
            for k, v in aptitude_confidence_map.items():
                if k in preferred_course or preferred_course in k:
                    pref_conf = max(pref_conf, v)

        match_color = COLOR_ANSWERED if pref_conf > 60 else (COLOR_MODERATE if pref_conf > 40 else COLOR_ALERT)
        match_text = "Excellent Match" if pref_conf > 60 else ("Moderate Match" if pref_conf > 40 else "Low Match (Consider Alternatives)")
        
        tk.Label(a_frame, text=f"Fit for {preferred_course}: {match_text} ({pref_conf:.1f}%)", font=("Arial", 14, "bold"), fg=match_color, bg="white").pack(anchor="w")

        tk.Label(a_frame, text="\nTop 3 Aptitude Recommendations & Market Trend:", font=("Arial", 11, "bold"), bg="white").pack(anchor="w")
        
        sorted_confidences = sorted(aptitude_confidence_map.items(), key=lambda item: item[1], reverse=True)
        
        for i, (stream, conf) in enumerate(sorted_confidences[:3]):
            boom = self.get_boom_display_text(stream)
            tk.Label(a_frame, text=f"{i+1}. {stream} (Aptitude: {conf:.1f}%) {boom}", font=("Arial", 11), bg="white").pack(anchor="w", padx=10)

        # --- EXPORT / SAVE BUTTONS ---
        btn_frame = tk.Frame(scrollable_frame, bg=COLOR_BG_CONTENT, pady=20)
        btn_frame.pack(fill=tk.X)
        
        # Save to Text File
        tk.Button(btn_frame, text="Save Report to File", font=("Arial", 12, "bold"), bg=COLOR_BG_NAV, fg="white", 
                  command=self.save_report_to_file).pack(side=tk.LEFT, padx=20)

        # Explicit Cloud Save Button (Even though it auto-saves)
        tk.Button(btn_frame, text="Sync to Cloud DB", font=("Arial", 12, "bold"), bg=COLOR_ANSWERED, fg="white", 
                  command=lambda: self.save_to_mongo(self.user_data)).pack(side=tk.LEFT, padx=20)
                  
        LOCAL_COURSE_KEYS = [
            "Computer Science (CSE)", "Information Technology (IT)", "Electronics & Communication (ECE)", "Electrical & Electronics (EEE)", "Mechanical Engineering (ME)", 
            "Aerospace Engineering", "Civil Engineering (CE)", "Chemical Engineering (CH)", "Biotechnology", "Industrial Engineering"
        ]
        
        rec_courses = set([s for s, c in sorted_confidences[:5]])
        valid_courses = sorted([c for c in rec_courses if c in LOCAL_COURSE_KEYS])
        
        if valid_courses:
            spec_frame = tk.Frame(btn_frame, bg=COLOR_BG_CONTENT)
            spec_frame.pack(side=tk.RIGHT, padx=20)
            
            selected_course_var = tk.StringVar(value=valid_courses[0])
            ttk.Combobox(spec_frame, textvariable=selected_course_var, values=valid_courses, state="readonly", width=30).pack(side=tk.LEFT, padx=5)
            tk.Button(spec_frame, text="Take Specialized Test", bg=COLOR_CURRENT_Q_NAV, fg="white",
                      command=lambda: self.start_specialized_test(selected_course_var.get())).pack(side=tk.LEFT)

    def get_boom_display_text(self, course_cluster):
        mapping = {
            "Computer": "CS", "Information": "IT", "Electronics": "EC", "Electrical": "EE",
            "Mechanical": "ME", "Civil": "CE", "Chemical": "CH", "Bio": "BT", "Aero": "AE", "Industrial": "IE"
        }
        code = "CS" # Default
        for k, v in mapping.items():
            if k in course_cluster:
                code = v
                break
        
        val = BOOM_PERCENTAGE_DATA.get(code, 0)
        return f"[🔥 Market Boom: {val}%]"

    def save_report_to_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if not file_path: return
        
        data = self.user_data
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"CAREER ASSESSMENT REPORT FOR {data.get('name', 'User').upper()}\n")
            f.write("="*50 + "\n\n")
            f.write(f"1. PERSONALITY: {data.get('personality_archetype', 'N/A')}\n")
            if 'personality_results' in data:
                for k, v in data['personality_results'].items():
                    f.write(f"   - {v['name']}: {v['score']:.1f}%\n")
            f.write("\n")
            f.write(f"2. INTERESTS: Recommended {data.get('career_profiler_recommendation')}\n")
            f.write("\n")
            f.write(f"3. APTITUDE: Top Match -> {data.get('aptitude_recommendation')} ({data.get('aptitude_confidence_max', 0):.1f}%)\n")
        
        messagebox.showinfo("Saved", "Report saved locally!")

    def clean_for_mongo(self, data):
        """Recursively converts numpy types to native Python types for MongoDB."""
        if isinstance(data, dict):
            return {k: self.clean_for_mongo(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.clean_for_mongo(v) for v in data]
        elif isinstance(data, (np.integer, np.int64, np.int32)):
            return int(data)
        elif isinstance(data, (np.floating, np.float64, np.float32)):
            return float(data)
        elif isinstance(data, np.ndarray):
            return self.clean_for_mongo(data.tolist())
        else:
            return data

    def save_to_mongo(self, data):
        if users_collection is None:
            print("⚠️ MongoDB not connected. Skipping save.")
            return

        try:
            # Clean numpy data types before insertion
            clean_data = self.clean_for_mongo(data)
            
            # Remove any non-serializable Tkinter vars if they slipped in
            final_data = {k: v for k, v in clean_data.items() if isinstance(v, (str, int, float, list, dict, bool))}
            
            users_collection.insert_one(final_data)
            print("✅ Data saved to MongoDB (CareerAssessmentDB.Personality)")
        except Exception as e:
            print(f"❌ MongoDB Save Error: {e}")

    def start_specialized_test(self, course):
        self.current_part = SpecializedAptitudeTest(self, self.container, course, self.user_data)

    def show_specialized_test_results(self, course, scores, section_map, report_data):
        self.user_data.update(report_data)

        for widget in self.container.winfo_children():
            widget.destroy()

        result_frame = tk.Frame(self.container, bg=COLOR_BG_CONTENT)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)

        tk.Label(result_frame, text=f"🔬 Specialized Test Results for {course} 🔬", font=("Arial", 18, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack(pady=(0, 20))
        
        total_score = sum(scores.values())
        total_questions = sum(len(qs) for qs in section_map.values())
        overall_percentage = (total_score / total_questions) * 100 if total_questions > 0 else 0

        tk.Label(result_frame, text="--- Your Performance on Key Skills ---", font=("Arial", 14, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_CURRENT_Q_NAV).pack(pady=10)

        for section, score in scores.items():
            count = len(section_map.get(section, []))
            tk.Label(result_frame, text=f"{section}: {score}/{count}", font=("Arial", 12), bg=COLOR_BG_CONTENT, fg=COLOR_BG_NAV).pack(anchor="center")

        tk.Label(result_frame, text=f"\nOverall Score: {total_score}/{total_questions} ({overall_percentage:.2f}%)", font=("Arial", 14), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack(pady=10)
        
        verdict = ""
        if overall_percentage >= 75:
            verdict = f"Excellent! Your scores show a strong natural aptitude for the key skills required in {course}. 👍"
        elif overall_percentage >= 50:
            verdict = f"Good performance! You have a solid foundation for the skills needed in {course}. With practice, you can excel."
        else:
            verdict = f"This area may be challenging. While you have potential, you may need to focus more on developing these specific skills for {course}. 💪"

        tk.Label(result_frame, text="--- Verdict ---", font=("Arial", 16, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack(pady=(20, 10))
        tk.Label(result_frame, text=verdict, font=("Arial", 12), bg=COLOR_BG_CONTENT, fg=COLOR_BG_NAV, wraplength=700).pack()

        # Update data and re-save
        self.user_data['specialized_test_score'] = overall_percentage
        if users_collection is not None:
             threading.Thread(target=self.save_to_mongo, args=(self.user_data,), daemon=True).start()

        back_button = tk.Button(result_frame, text="← Back to Main Report", font=("Arial", 12, "bold"),
                                 command=self.show_final_recommendation,
                                 bg=COLOR_BG_NAV, fg=COLOR_BUTTON_TEXT)
        back_button.pack(pady=30)


# ====================================================================
# --- EXECUTION ---
# ====================================================================
if __name__ == "__main__":
    if not MATPLOTLIB_AVAILABLE:
        print("Warning: Matplotlib is not available. Chart generation is disabled.")
        
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()