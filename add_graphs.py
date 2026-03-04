import re

with open(r"d:\vsscode\career1.py", "r", encoding="utf-8") as f:
    main_content = f.read()

# We need to render the charts in `show_final_recommendation(self):` of `QuizApp`.

# Locate where to insert the charts
# Let's add them at the end of the `show_final_recommendation` function just before the "Specialized Test" option.

target_insertion = "        # --- Option to Test Other Branches ---"

graph_logic = """
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

"""

# Also fix the numbering later
new_option_test = target_insertion.replace("4. Specialized Test", "5. Specialized Test")

main_content = main_content.replace(target_insertion, graph_logic + new_option_test)


with open(r"d:\vsscode\career1_graphs.py", "w", encoding="utf-8") as f:
    f.write(main_content)
    
print("script done")
