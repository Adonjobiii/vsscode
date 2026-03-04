import sys

with open(r"d:\vsscode\career1supp.py", "r", encoding="utf-8") as f:
    supp_lines = f.readlines()

# find where imports end, roughly line 9
start_idx = 0
for i, line in enumerate(supp_lines):
    if line.startswith("# ==============================="):
        start_idx = i
        break

supp_content = "".join(supp_lines[start_idx:])
# Handle users_collection conflict
supp_content = supp_content.replace('users_collection = db["Personality"]', 'personality_collection = db["Personality"]')
supp_content = supp_content.replace('users_collection = None', 'personality_collection = None')
supp_content = supp_content.replace('if users_collection is not None:', 'if personality_collection is not None:')
supp_content = supp_content.replace('users_collection.insert_one(document)', 'personality_collection.insert_one(document)')

with open(r"d:\vsscode\career1.py", "r", encoding="utf-8") as f:
    main_content = f.read()

# Replace the execution block
execution_block = """# ====================================================================
# --- EXECUTION ---
# ===================================================================="""

new_block = """# ====================================================================
# --- PERSONALITY ASSESSMENT (from career1supp.py) ---
# ====================================================================
""" + supp_content

# Remove the original main block from career1supp code inside the new block
new_block = new_block.replace('''if __name__ == "__main__":\n    root = tk.Tk()\n    app = PersonalityAssessmentApp(root)\n    root.mainloop()''', '')

# Remove original main layout of career1.py
original_main = """if __name__ == "__main__":
    if not MATPLOTLIB_AVAILABLE:
        print("Warning: Matplotlib is not available. Chart generation is disabled.")
        
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()"""


# Add a combined launch menu
launch_menu = """
# ====================================================================
# --- EXECUTION ---
# ====================================================================
if __name__ == "__main__":
    if not MATPLOTLIB_AVAILABLE:
        print("Warning: Matplotlib is not available. Chart generation is disabled.")

    def run_engineering_quiz():
        launcher.destroy()
        root = tk.Tk()
        app = QuizApp(root)
        root.mainloop()

    def run_personality_assessment():
        launcher.destroy()
        root = tk.Tk()
        app = PersonalityAssessmentApp(root)
        root.mainloop()

    launcher = tk.Tk()
    launcher.title("Select Assessment")
    launcher.geometry("400x200")
    launcher.configure(bg="#2C3E50")

    tk.Label(launcher, text="Choose an Assessment", font=("Helvetica", 16, "bold"), bg="#2C3E50", fg="white").pack(pady=20)
    
    tk.Button(launcher, text="Engineering Career Assessment", command=run_engineering_quiz, bg="#3498DB", fg="white", font=("Helvetica", 12), width=30, pady=5).pack(pady=5)
    tk.Button(launcher, text="Personality Assessment", command=run_personality_assessment, bg="#2ECC71", fg="white", font=("Helvetica", 12), width=30, pady=5).pack(pady=5)
    
    launcher.mainloop()
"""

new_content = main_content.replace(execution_block, new_block + launch_menu)
new_content = new_content.replace(original_main, '')

with open(r"d:\vsscode\career1.py", "w", encoding="utf-8") as f:
    f.write(new_content)
print("Done merging!")
