
import random
import sys
import time
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

import re

import pymongo
import os

# 1. Set the URI using the address we found. 
# REPLACE '<password>' with your actual MongoDB password.
MONGO_URI = "mongodb+srv://anoop:anoop123@cluster0.rd6nzal.mongodb.net/CareerAssessmentDB?retryWrites=true&w=majority"

# 2. Your connection logic
if MONGO_URI != "YOUR_MONGODB_CONNECTION_STRING":
    try:
        client = pymongo.MongoClient(MONGO_URI)
        
        # This will now default to 'CareerAssessmentDB' because we added it to the URI above
        db = client.get_database() 
        
        users_collection = db.users
        print("Successfully connected to MongoDB.")
        
        # Optional: specific check to verify the connection is actually live
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")

    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        users_collection = None
else:
    print("Warning: MONGO_URI not set. Data will not be saved to MongoDB.")
    users_collection = None
# Set Matplotlib backend
try:
    matplotlib.use('TkAgg')
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False

# Import all dependencies, configuration, and ML logic
from config_data import *
from ml_logic import DataProcessor, MLModelTrainer
from commerce_aptitude_questions import get_test_questions as get_commerce_test_questions
from commerce_config import determine_commerce_interests, determine_commerce_course_by_aptitude

# Global Initialization (Load data and train/load models once)
DATA_PROCESSOR = DataProcessor()
ML_MODELS = MLModelTrainer()
QUESTIONS = DATA_PROCESSOR.QUESTIONS
CORRECT_ANSWERS = DATA_PROCESSOR.CORRECT_ANSWERS
BOOM_PERCENTAGE_DATA = DATA_PROCESSOR.BOOM_PERCENTAGE_DATA
# MONGODB_AVAILABLE state is checked implicitly via DataProcessor

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
        
        continue_button = tk.Button(result_frame, text="Continue to Aptitude Test (Part 2) →", font=("Arial", 12, "bold"), 
                                     command=lambda: self.parent.show_aptitude_test(recommended_stream, self.priority_list), 
                                     bg=COLOR_ANSWERED, fg=COLOR_BUTTON_TEXT)
        continue_button.pack(pady=30)

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
        
        # Check track
        track = self.parent.user_data.get('assessment_track', 'engineering')
        
        if track == 'commerce':
            # Use specialized commerce questions
            questions = get_commerce_test_questions()
            for q in questions:
                all_selected_questions.append(q)
        else:
            # Check for global availability of QUESTIONS (from DataProcessor)
            global QUESTIONS
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
                fig, ax = plt.subplots(figsize=(8, 4))
                sections_present = sorted(self.section_question_map.keys())
                correct = [scores[s] for s in sections_present]
                total_answered = [section_answered[s] for s in sections_present]
                incorrect = [total_answered[i] - correct[i] for i in range(len(sections_present))]
                
                ax.bar(sections_present, correct, label='Correct', color=COLOR_ANSWERED)
                ax.bar(sections_present, incorrect, bottom=correct, label='Incorrect', color=COLOR_UNANSWERED)
                
                ax.set_ylabel('Number of Questions')
                ax.set_title('Answer Breakdown per Skill')
                ax.set_yticks(range(1, 8))
                plt.xticks(rotation=45, ha="right")
                plt.legend()
                plt.tight_layout()

                canvas = FigureCanvasTkAgg(fig, master=result_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(pady=20)
                
            except Exception as ex:
                tk.Label(result_frame, text=f"(Matplotlib Error: {ex})", fg="red", bg=COLOR_BG_CONTENT).pack()
        else:
            tk.Label(result_frame, text="(Matplotlib not available for chart)", fg="red", bg=COLOR_BG_CONTENT).pack()
        
        final_button = tk.Button(result_frame, text="Proceed to Personality Assessment →", font=("Arial", 12, "bold"), 
                                     command=self.parent.show_personality_test, 
                                     bg=COLOR_CURRENT_Q_NAV, fg=COLOR_BUTTON_TEXT)
        final_button.pack(pady=20)

# ====================================================================
# --- Specialized Aptitude Test Class ---
# ====================================================================
class SpecializedAptitudeTest(tk.Frame): # Inherits from tk.Frame instead of AptitudeTestPart2 due to separation
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
    
    # Re-implementing necessary methods from AptitudeTestPart2
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
        # Localized map for safety
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
        
        # NOTE: Navigation panel creation methods etc. are assumed to be in scope or defined inline 
        # in the context of the larger file structure for brevity and focusing on core logic.
        
        # Simplified widget creation for Specialized Test focusing on core needs
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
        self.root.geometry("1100x750") 
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

    def show_aptitude_test(self, recommended_stream, priority_list):
        self.current_part = AptitudeTestPart2(self, self.container, recommended_stream, priority_list) 

    def show_personality_test(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        self.current_part = PersonalityAssessmentApp(self.container, self)
        
    def show_final_recommendation(self):
        track = self.user_data.get('assessment_track', 'engineering')
        is_commerce = (track == 'commerce')
        
        interest_recommendation = self.user_data.get('career_profiler_recommendation', 'N/A')
        priority_list = self.user_data.get('career_priority_list', [])
        aptitude_recommendation = self.user_data.get('aptitude_recommendation', 'N/A')
        aptitude_confidence = self.user_data.get('aptitude_confidence_max', 0)
        aptitude_confidence_map = self.user_data.get('aptitude_confidence_map', {})
        preferred_course = self.user_data.get('preferred_course', 'N/A')
        user_interests = self.user_data.get('interests', [])
        personality_results = self.user_data.get('personality_results', {})
        
        for widget in self.container.winfo_children():
            widget.destroy()

        # Create a scrollable container for the final results
        result_canvas = tk.Canvas(self.container, bg=COLOR_BG_CONTENT, highlightthickness=0)
        result_scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=result_canvas.yview)
        result_frame = tk.Frame(result_canvas, bg=COLOR_BG_CONTENT)
        
        result_frame.bind("<Configure>", lambda e: result_canvas.configure(scrollregion=result_canvas.bbox("all")))
        result_canvas.create_window((0, 0), window=result_frame, anchor="nw")
        result_canvas.configure(yscrollcommand=result_scrollbar.set)
        
        result_canvas.pack(side="left", fill="both", expand=True, padx=(40, 0), pady=40)
        result_scrollbar.pack(side="right", fill="y", pady=40)

        header_text = "✨ FINAL COMMERCE & FINANCE REPORT ✨" if is_commerce else "✨ FINAL CAREER RECOMMENDATION ✨"
        tk.Label(result_frame, text=header_text, font=("Arial", 20, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack(pady=(0, 20))
        
        # --- Profile Info ---
        tk.Label(result_frame, text=f"Profile: {self.user_data.get('name', 'User')} | Track: {track.title()}", font=("Arial", 12), bg=COLOR_BG_CONTENT, fg=COLOR_BG_NAV).pack(anchor="w", pady=(5, 15))

        # --- Section 1: Interest Match ---
        tk.Label(result_frame, text="1. Primary Interest Match", font=("Arial", 16, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack(anchor="w", pady=(10, 5))
        if is_commerce:
            # Commerce interest match
            interest_rec = self.user_data.get('career_recommendation', {})
            course = interest_rec.get('course', 'N/A')
            tk.Label(result_frame, text=f"Top Match: {course}", font=("Arial", 13, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_ANSWERED).pack(anchor="w", padx=20)
            tk.Label(result_frame, text="Your expressed interests and priorities suggest a strong alignment with this commerce field.", font=("Arial", 11), bg=COLOR_BG_CONTENT, fg=COLOR_BG_NAV, wraplength=700).pack(anchor="w", padx=20, pady=5)
        else:
            # Engineering interest match
            tk.Label(result_frame, text=f"Top Match: {interest_recommendation}", font=("Arial", 13, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_ANSWERED).pack(anchor="w", padx=20)
            tk.Label(result_frame, text="Based on your task preferences and vocational interests.", font=("Arial", 11), bg=COLOR_BG_CONTENT, fg=COLOR_BG_NAV).pack(anchor="w", padx=20, pady=5)
        tk.Label(result_frame, text=f"Stated Preference: {preferred_course}", font=("Arial", 12, 'bold'), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack(anchor="w", padx=20)
        tk.Label(result_frame, text=f"Aptitude Confidence for Preference: {preferred_course_confidence:.2f}%", font=("Arial", 12), bg=COLOR_BG_CONTENT, fg=COLOR_BG_NAV).pack(anchor="w", padx=20)


        # --- Section 2: Cognitive Aptitude Match ---
        tk.Label(result_frame, text="\n2. Cognitive Aptitude Match", font=("Arial", 16, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack(anchor="w", pady=(10, 5))
        if is_commerce:
            # Aptitude match based on commerce-specific logic
            apt_rec_data = determine_commerce_course_by_aptitude(self.user_data.get('aptitude_scores', {}))
            rec_stream = apt_rec_data.get('recommended_stream', 'N/A')
            conf = apt_rec_data.get('confidence', 0)
            tk.Label(result_frame, text=f"Best Fit based on Thinking Skills: {rec_stream} ({conf:.1f}%)", font=("Arial", 13, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_PRIMARY).pack(anchor="w", padx=20)
            
            # Show probabilities bar chart (Top 5)
            probs = apt_rec_data.get('probabilities', {})
            if probs and MATPLOTLIB_AVAILABLE:
                try:
                    fig, ax = plt.subplots(figsize=(6, 3))
                    courses = list(probs.keys())
                    vals = list(probs.values())
                    ax.barh(courses, vals, color="#2C3E50")
                    ax.set_title("Top Specialization Matches (%)")
                    plt.tight_layout()
                    canvas = FigureCanvasTkAgg(fig, master=result_frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack(pady=10)
                except: pass
        else:
            tk.Label(result_frame, text=f"Top Aptitude Match: {aptitude_recommendation} ({aptitude_confidence:.1f}%)", font=("Arial", 13, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_PRIMARY).pack(anchor="w", padx=20)
            sorted_confidences = sorted(aptitude_confidence_map.items(), key=lambda item: item[1], reverse=True)
            for i, (course, conf) in enumerate(sorted_confidences[:5]):
                 tk.Label(result_frame, text=f"• {course}: {conf:.2f}%", font=("Arial", 11), bg=COLOR_BG_CONTENT, fg=COLOR_BG_NAV).pack(anchor="w", padx=40)

        # --- Section 3: Personality Insights ---
        tk.Label(result_frame, text="Career Personality Profile", font=("Arial", 14, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack(anchor="w", pady=(10, 5))
        
        p_rec = self.user_data.get('personality_rec_career', "N/A")
        tk.Label(result_frame, text=f"Top Trait Career Rec: {p_rec}", font=("Arial", 12, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack(anchor="w", padx=20)
        
        p_results = self.user_data.get('personality_results', {})
        if p_results:
            p_frame = tk.Frame(result_frame, bg=COLOR_BG_CONTENT)
            p_frame.pack(fill=tk.X, padx=20, pady=5)
            for trait_k, trait_v in sorted(p_results.items(), key=lambda item: item[1]['score'], reverse=True):
                tk.Label(p_frame, text=f"• {trait_v['name']}: {trait_v['score']:.1f}%", font=("Arial", 11), bg=COLOR_BG_CONTENT, fg=COLOR_BG_NAV).pack(anchor="w")



        # --- GRAPHICAL REPRESENTATIONS ---
        ttk.Separator(result_frame, orient='horizontal').pack(fill='x', pady=15, padx=20)
        tk.Label(result_frame, text="4. Performance & Trait Graphs", font=("Arial", 14, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack(anchor="w", pady=(10, 5))
        
        graphs_frame = tk.Frame(result_frame, bg=COLOR_BG_CONTENT)
        graphs_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        if MATPLOTLIB_AVAILABLE:
            try:
                # 1. Aptitude Graph
                aptitude_scores = self.user_data.get('aptitude_scores', {})
                if aptitude_scores:
                    fig_apt, ax_apt = plt.subplots(figsize=(6, 3))
                    sections_present = sorted(aptitude_scores.keys())
                    correct = [aptitude_scores[s] for s in sections_present]
                    
                    # Estimate total answered (assuming 7 per section normally if recorded correctly, or we just show raw correct scores)
                    ax_apt.bar(sections_present, correct, color=COLOR_ANSWERED)
                    ax_apt.set_ylabel('Questions Correct')
                    ax_apt.set_title('Aptitude Skill Breakdown')
                    plt.setp(ax_apt.get_xticklabels(), rotation=15, ha="right", fontsize=8)
                    fig_apt.tight_layout()
                    
                    canvas_apt = FigureCanvasTkAgg(fig_apt, master=graphs_frame)
                    canvas_apt.draw()
                    canvas_apt.get_tk_widget().pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

                # 2. Personality Graph
                p_results = self.user_data.get('personality_results', {})
                if p_results:
                    fig_pers, ax_pers = plt.subplots(figsize=(6, 3), dpi=80)
                    names = [p_results[k]["name"] for k in p_results]
                    scores = [p_results[k]["score"] for k in p_results]
                    
                    TRAITS_LOCAL = {
                        'O': {"name": "Openness", "color": "#3498db"},
                        'C': {"name": "Conscientiousness", "color": "#2ecc71"},
                        'E': {"name": "Extraversion", "color": "#f1c40f"},
                        'A': {"name": "Agreeableness", "color": "#9b59b6"},
                        'N': {"name": "Neuroticism", "color": "#e74c3c"},
                    }
                    colors = [TRAITS_LOCAL[k]["color"] for k in p_results]
                    
                    ax_pers.barh(names, scores, color=colors)
                    ax_pers.set_xlim(0, 100)
                    ax_pers.set_xlabel('Trait Intensity (%)')
                    ax_pers.set_title('Big Five Personality Profile')
                    fig_pers.tight_layout()
                    
                    canvas_pers = FigureCanvasTkAgg(fig_pers, master=graphs_frame)
                    canvas_pers.draw()
                    canvas_pers.get_tk_widget().pack(side=tk.RIGHT, padx=10, fill=tk.BOTH, expand=True)
                    
            except Exception as ex:
                tk.Label(graphs_frame, text=f"(Chart Generation Error: {ex})", fg="red", bg=COLOR_BG_CONTENT).pack()
        else:
            tk.Label(graphs_frame, text="(Matplotlib not available for charts)", fg="red", bg=COLOR_BG_CONTENT).pack()

        # --- Option to Test Other Branches ---
        ttk.Separator(result_frame, orient='horizontal').pack(fill='x', pady=15, padx=20)
        tk.Label(result_frame, text="4. Specialized Test for Other Branches", font=("Arial", 14, "bold"), bg=COLOR_BG_CONTENT, fg=COLOR_BG_DARK).pack(pady=(5, 10))
        
        
        # Combine user priorities and top 5 recommendations
        rec_courses = set()
        
        for i, (stream, conf) in enumerate(sorted_confidences[:5]):
            rec_courses.add(stream)

        for prio in priority_list:
             prio_map = {"Computer Science and Engineering": "Computer Science (CSE)", "Information Technology": "Information Technology (IT)", "Electronics and Communication Engineering": "Electronics & Communication (ECE)", "Electrical and Electronics Engineering": "Electrical & Electronics (EEE)", "Mechanical Engineering": "Mechanical Engineering (ME)", "Civil Engineering": "Civil Engineering (CE)", "Aerospace Engineering": "Aerospace Engineering", "Chemical Engineering": "Chemical Engineering (CH)", "Biotechnology Engineering": "Biotechnology", "Industrial Engineering": "Industrial Engineering"}
             rec_courses.add(prio_map.get(prio, prio))
        
        # Filter for courses that have a defined skill map
        LOCAL_COURSE_TO_SKILLS_MAP_KEYS = {
            "Computer Science (CSE)", "Information Technology (IT)", "Electronics & Communication (ECE)", "Electrical & Electronics (EEE)", "Mechanical Engineering (ME)", 
            "Aerospace Engineering", "Civil Engineering (CE)", "Chemical Engineering (CH)", "Biotechnology", "Industrial Engineering"
        }
        
        valid_courses = sorted([c for c in rec_courses if c in LOCAL_COURSE_TO_SKILLS_MAP_KEYS])

        if valid_courses:
            test_frame = tk.Frame(result_frame, bg=COLOR_BG_CONTENT)
            test_frame.pack(pady=10)
            
            selected_course = tk.StringVar(value=valid_courses[0])
            course_menu = ttk.Combobox(test_frame, textvariable=selected_course, values=valid_courses, state="readonly", font=("Arial", 12), width=40)
            course_menu.pack(side=tk.LEFT, padx=10)

            start_spec_test_btn = tk.Button(test_frame, text="Start Specialized Test for Selected Branch", font=("Arial", 12, "bold"), 
                                             command=lambda: self.start_specialized_test(selected_course.get()),
                                             bg=COLOR_ANSWERED, fg=COLOR_BUTTON_TEXT)
            start_spec_test_btn.pack(side=tk.LEFT, padx=10)
        else:
            tk.Label(result_frame, text="No suitable engineering branches available for specialized testing.", font=("Arial", 11), bg=COLOR_BG_CONTENT, fg="gray").pack(pady=10)


    def show_specialized_test_results(self, course, scores, section_map, report_data):
        self.user_data.update(report_data)

        for widget in self.container.winfo_children():
            widget.destroy()

        # Create a scrollable container for the final results
        result_canvas = tk.Canvas(self.container, bg=COLOR_BG_CONTENT, highlightthickness=0)
        result_scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=result_canvas.yview)
        result_frame = tk.Frame(result_canvas, bg=COLOR_BG_CONTENT)
        
        result_frame.bind("<Configure>", lambda e: result_canvas.configure(scrollregion=result_canvas.bbox("all")))
        result_canvas.create_window((0, 0), window=result_frame, anchor="nw")
        result_canvas.configure(yscrollcommand=result_scrollbar.set)
        
        result_canvas.pack(side="left", fill="both", expand=True, padx=(40, 0), pady=40)
        result_scrollbar.pack(side="right", fill="y", pady=40)

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

        back_button = tk.Button(result_frame, text="← Back to Main Report", font=("Arial", 12, "bold"),
                                 command=self.show_final_recommendation,
                                 bg=COLOR_BG_NAV, fg=COLOR_BUTTON_TEXT)
        back_button.pack(pady=30)


# ====================================================================
# --- PERSONALITY ASSESSMENT (from career1supp.py) ---
# ====================================================================
# ===============================
# MongoDB Configuration
# ===============================
# Fetching password from environment or using your project default
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
if MONGO_PASSWORD:
    MONGO_URI = f"mongodb+srv://anoop:{MONGO_PASSWORD}@cluster0.rd6nzal.mongodb.net/?retryWrites=true&w=majority"
else:
    MONGO_URI = "mongodb+srv://anoop:anoop123@cluster0.rd6nzal.mongodb.net/?retryWrites=true&w=majority"

try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client["CareerAssessmentDB"]
    # Results are stored in the 'Personality' collection
    personality_collection = db["Personality"]
    client.admin.command("ping")
    print("✅ MongoDB connected successfully")
except Exception as e:
    print("❌ MongoDB connection failed:", e)
    personality_collection = None

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

class PersonalityAssessmentApp:
    def __init__(self, container_frame, parent):
        self.container_frame = container_frame
        self.parent = parent
        self.setup_styles()
        self.reset_app()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", thickness=12, background=COLOR_PRIMARY)

    def reset_app(self):
        for widget in self.container_frame.winfo_children(): widget.destroy()
        self.q_ids = list(QUESTIONNAIRE.keys())
        self.index = 0
        self.answers = {}
        self.answer_var = tk.IntVar(value=0)
        self.build_layout()
        self.show_question()

    def build_layout(self):
        self.side_pane = tk.Frame(self.container_frame, bg=COLOR_BG_SIDEBAR, width=280)
        self.side_pane.pack(side=tk.LEFT, fill=tk.Y)
        self.side_pane.pack_propagate(False)

        tk.Label(self.side_pane, text="PROGRESS", fg="white", bg=COLOR_BG_SIDEBAR, font=("Helvetica", 12, "bold")).pack(pady=20)
        self.grid_frame = tk.Frame(self.side_pane, bg=COLOR_BG_SIDEBAR)
        self.grid_frame.pack(padx=10)

        self.q_btns = {}
        for i in self.q_ids:
            btn = tk.Button(self.grid_frame, text=str(i), width=3, font=("Helvetica", 9), relief="flat", bg="#34495E", fg="white", command=lambda x=i: self.jump(x))
            row, col = (i - 1) // 5, (i - 1) % 5
            btn.grid(row=row, column=col, padx=3, pady=3)
            self.q_btns[i] = btn

        self.main_pane = tk.Frame(self.container_frame, bg=COLOR_BG_MAIN)
        self.main_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        header = tk.Frame(self.main_pane, bg=COLOR_WHITE, height=80)
        header.pack(fill=tk.X)
        self.progress = ttk.Progressbar(header, orient="horizontal", length=500, mode="determinate")
        self.progress.pack(pady=25)

        self.card = tk.Frame(self.main_pane, bg=COLOR_WHITE, padx=50, pady=50, highlightbackground="#DCDCDC", highlightthickness=1)
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        self.lbl_trait = tk.Label(self.card, text="TRAIT", fg=COLOR_PRIMARY, bg=COLOR_WHITE, font=("Helvetica", 10, "bold"))
        self.lbl_trait.pack(anchor="w")

        self.lbl_q_text = tk.Label(self.card, text="", bg=COLOR_WHITE, fg=COLOR_TEXT_MAIN, font=("Helvetica", 22), wraplength=600, justify="left")
        self.lbl_q_text.pack(pady=(10, 40), anchor="w")

        self.opt_frame = tk.Frame(self.card, bg=COLOR_WHITE)
        self.opt_frame.pack(fill=tk.X)

        options = [("Strongly Disagree", 1), ("Disagree", 2), ("Neutral", 3), ("Agree", 4), ("Strongly Agree", 5)]
        for text, val in options:
            tk.Radiobutton(self.opt_frame, text=text, value=val, variable=self.answer_var, indicatoron=0, font=("Helvetica", 11), bg="#F1F3F4", selectcolor=COLOR_PRIMARY, fg=COLOR_TEXT_MAIN, padx=20, pady=12, width=25, command=self.save_and_next).pack(pady=5, fill=tk.X)

        nav_frame = tk.Frame(self.main_pane, bg=COLOR_BG_MAIN)
        nav_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=50, pady=30)
        tk.Button(nav_frame, text="← Previous", bg=COLOR_WHITE, relief="flat", padx=20, command=self.prev_q).pack(side=tk.LEFT)
        tk.Button(nav_frame, text="Finish & Save", bg=COLOR_SUCCESS, fg="white", relief="flat", padx=20, pady=10, font=("Helvetica", 11, "bold"), command=self.finish).pack(side=tk.RIGHT)

    def show_question(self):
        q_id = self.q_ids[self.index]
        trait_code, text, _ = QUESTIONNAIRE[q_id]
        self.lbl_trait.config(text=f"QUESTION {q_id} / {len(self.q_ids)} — {TRAITS[trait_code]['name'].upper()}")
        self.lbl_q_text.config(text=text)
        self.progress['value'] = (len(self.answers) / len(self.q_ids)) * 100
        self.answer_var.set(self.answers.get(q_id, 0))
        self.update_sidebar()

    def save_and_next(self):
        self.answers[self.q_ids[self.index]] = self.answer_var.get()
        if self.index < len(self.q_ids) - 1:
            self.index += 1
            self.container_frame.after(150, self.show_question)
        else: self.update_sidebar()

    def update_sidebar(self):
        curr = self.q_ids[self.index]
        for q, btn in self.q_btns.items():
            if q == curr: btn.config(bg=COLOR_PRIMARY, fg="white", font=("Helvetica", 10, "bold"))
            elif q in self.answers: btn.config(bg=COLOR_SUCCESS, fg="white")
            else: btn.config(bg="#34495E", fg="white")

    def prev_q(self):
        if self.index > 0:
            self.index -= 1
            self.show_question()

    def jump(self, q_id):
        self.index = self.q_ids.index(q_id)
        self.show_question()

    def finish(self):
        if len(self.answers) < len(self.q_ids):
            if not messagebox.askyesno("Incomplete", f"You've missed {len(self.q_ids) - len(self.answers)} questions. Proceed to save anyway?"): return
        self.show_results()

    def show_results(self):
        for w in self.main_pane.winfo_children(): w.destroy()
        self.side_pane.pack_forget()

        # 1. SCORING ENGINE
        trait_raw = defaultdict(list)
        facet_raw = defaultdict(list)

        for q_id, val in self.answers.items():
            trait_code, _, is_reverse = QUESTIONNAIRE[q_id]
            # Convert raw input to standardized 1-5 score [cite: 272, 273]
            score = (6 - val) if is_reverse else val
            trait_raw[trait_code].append(score)
            facet_raw[FACET_MAP[q_id]].append(score)

        results = {}
        for t, vals in trait_raw.items():
            avg = sum(vals) / len(vals)
            # Normalizing to 100% scale 
            results[t] = {"name": TRAITS[t]["name"], "score": ((avg - 1) / 4) * 100}

        facet_results = {f: ((sum(vals)/len(vals)-1)/4)*100 for f, vals in facet_raw.items()}

        # 2. CAREER ANALYSIS
        top_trait = sorted(results.items(), key=lambda x: x[1]['score'], reverse=True)[0][0]
        careers = {
            'O': "Creative Arts, Design, R&D, AI Research, Architecture",
            'C': "Engineering, Law, Auditing, Project Management, Administration",
            'E': "Sales, Public Relations, Leadership, Politics, Hospitality",
            'A': "Healthcare, Education, HR, Social Work, Counseling",
            'N': "Risk Analysis, Cybersecurity, Quality Control, Strategic Planning"
        }
        rec_career = careers.get(top_trait, "General Professional")

        self.parent.user_data['personality_results'] = results
        self.parent.user_data['personality_facet_results'] = facet_results
        self.parent.user_data['personality_rec_career'] = rec_career
        
        # Proceed to Final Recommendation
        self.parent.show_final_recommendation()
        return

        # 3. SAVE TO MONGODB (THE "BACK DIRECTORY")
        if personality_collection is not None:
            try:
                document = {
                    "username": "anoop",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "raw_responses": {str(k): v for k, v in self.answers.items()},
                    "broad_traits": results,
                    "sub_traits_facets": facet_results,
                    "career_recommendation": rec_career
                }
                personality_collection.insert_one(document)
                messagebox.showinfo("Success", "Assessment report saved to MongoDB directory!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save to MongoDB: {e}")

        # 4. RESULTS DISPLAY
        container = tk.Canvas(self.main_pane, bg=COLOR_BG_MAIN)
        scrollbar = ttk.Scrollbar(self.main_pane, orient="vertical", command=container.yview)
        scrollable_frame = tk.Frame(container, bg=COLOR_BG_MAIN, padx=40, pady=30)

        scrollable_frame.bind("<Configure>", lambda e: container.configure(scrollregion=container.bbox("all")))
        container.create_window((0, 0), window=scrollable_frame, anchor="nw")
        container.configure(yscrollcommand=scrollbar.set)

        container.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(scrollable_frame, text="CAREER PROFILE & PERSONALITY REPORT", font=("Helvetica", 16, "bold"), bg=COLOR_BG_MAIN).pack(pady=(0, 20))

        # Chart
        fig, ax = plt.subplots(figsize=(6, 3), dpi=95)
        ax.barh([results[k]["name"] for k in results], [results[k]["score"] for k in results], color=[TRAITS[k]["color"] for k in results])
        ax.set_xlim(0, 100)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, scrollable_frame)
        canvas.get_tk_widget().pack()

        # Career Box
        c_box = tk.Frame(scrollable_frame, bg="#EBF5FB", padx=20, pady=20, bd=1, relief="solid")
        c_box.pack(fill=tk.X, pady=20)
        tk.Label(c_box, text="PROFESSIONAL GUIDANCE", font=("Helvetica", 10, "bold"), bg="#EBF5FB", fg="#2E86C1").pack(anchor="w")
        tk.Label(c_box, text=rec_career, font=("Helvetica", 13), bg="#EBF5FB", wraplength=700).pack(pady=10, anchor="w")

        # Sub-Trait Grid
        s_box = tk.Frame(scrollable_frame, bg=COLOR_WHITE, padx=20, pady=20, bd=1, relief="solid")
        s_box.pack(fill=tk.X)
        tk.Label(s_box, text="GRANULAR FACET SCORES", font=("Helvetica", 10, "bold"), bg=COLOR_WHITE).pack(anchor="w", pady=(0, 10))
        
        f_grid = tk.Frame(s_box, bg=COLOR_WHITE)
        f_grid.pack(fill=tk.X)
        for i, (f_name, f_score) in enumerate(sorted(facet_results.items(), key=lambda x: x[1], reverse=True)):
            row, col = i // 2, i % 2
            tk.Label(f_grid, text=f"• {f_name}: {f_score:.1f}%", bg=COLOR_WHITE).grid(row=row, column=col, sticky="w", padx=20, pady=3)

        footer = tk.Frame(scrollable_frame, bg=COLOR_BG_MAIN)
        footer.pack(fill=tk.X, pady=30)
        tk.Button(footer, text="New Assessment", command=self.reset_app, bg=COLOR_PRIMARY, fg="white", relief="flat", padx=20).pack(side=tk.LEFT)
        tk.Button(footer, text="Exit", command=self.parent.show_final_recommendation, bg="#95A5A6", fg="white", relief="flat", padx=20).pack(side=tk.RIGHT)


# ====================================================================
# ====================================================================
# --- EXECUTION ---
# ====================================================================
if __name__ == "__main__":
    if not MATPLOTLIB_AVAILABLE:
        print("Warning: Matplotlib is not available. Chart generation is disabled.")

    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
