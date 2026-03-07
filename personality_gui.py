import tkinter as tk
from tkinter import ttk, messagebox
import time
from collections import defaultdict
from config_data import users_collection, TRAITS, FACET_MAP, QUESTIONNAIRE

class PersonalityAssessmentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Career Assessment System")
        self.root.geometry("1250x950")
        self.root.configure(bg="#F8F9FA") # COLOR_BG_MAIN
        self.setup_styles()
        self.reset_app()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", thickness=12, background="#3498DB")

    def reset_app(self):
        for widget in self.root.winfo_children(): widget.destroy()
        self.q_ids = list(QUESTIONNAIRE.keys())
        self.index = 0
        self.answers = {}
        self.answer_var = tk.IntVar(value=0)
        self.build_layout()
        self.show_question()

    def build_layout(self):
        COLOR_BG_SIDEBAR = "#2C3E50"
        COLOR_BG_MAIN = "#F8F9FA"
        COLOR_PRIMARY = "#3498DB"
        COLOR_SUCCESS = "#2ECC71"
        COLOR_TEXT_MAIN = "#2C3E50"
        COLOR_WHITE = "#FFFFFF"

        self.side_pane = tk.Frame(self.root, bg=COLOR_BG_SIDEBAR, width=280)
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

        self.main_pane = tk.Frame(self.root, bg=COLOR_BG_MAIN)
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
        COLOR_PRIMARY = "#3498DB"
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
            self.root.after(150, self.show_question)
        else: self.update_sidebar()

    def update_sidebar(self):
        COLOR_PRIMARY = "#3498DB"
        COLOR_SUCCESS = "#2ECC71"
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
        COLOR_BG_MAIN = "#F8F9FA"
        COLOR_WHITE = "#FFFFFF"
        COLOR_PRIMARY = "#3498DB"

        for w in self.main_pane.winfo_children(): w.destroy()
        self.side_pane.pack_forget()

        # 1. SCORING ENGINE
        trait_raw = defaultdict(list)
        facet_raw = defaultdict(list)

        for q_id, val in self.answers.items():
            trait_code, _, is_reverse = QUESTIONNAIRE[q_id]
            score = (6 - val) if is_reverse else val
            trait_raw[trait_code].append(score)
            facet_raw[FACET_MAP[q_id]].append(score)

        results = {}
        for t, vals in trait_raw.items():
            avg = sum(vals) / len(vals)
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

        # 3. SAVE TO MONGODB
        if users_collection is not None:
            try:
                document = {
                    "username": "anoop",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "raw_responses": {str(k): v for k, v in self.answers.items()},
                    "broad_traits": results,
                    "sub_traits_facets": facet_results,
                    "career_recommendation": rec_career
                }
                users_collection.insert_one(document)
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
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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
        tk.Button(footer, text="Exit", command=self.root.quit, bg="#95A5A6", fg="white", relief="flat", padx=20).pack(side=tk.RIGHT)

if __name__ == "__main__":
    root = tk.Tk()
    app = PersonalityAssessmentApp(root)
    root.mainloop()
