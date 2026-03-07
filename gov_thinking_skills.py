"""
gov_thinking_skills.py

Thinking skill percentages for Government Exams track.
"""

GOV_THINKING_SKILLS_DATA = {
    "Logical Reasoning": 20,
    "Analytical Thinking": 18,
    "Problem Solving": 15,
    "Critical Thinking": 12,
    "Decision Making": 10,
    "Memory Recall": 8,
    "Strategic Thinking": 7,
    "Observation Skills": 5,
    "Time Management": 5
}

GOV_PATH_WEIGHTS = {
    "Civil Services": {"Critical Thinking": 40, "Analytical Thinking": 30, "Decision Making": 30},
    "Defence": {"Strategic Thinking": 40, "Observation Skills": 30, "Problem Solving": 30},
    "State/Central Gov": {"Memory Recall": 50, "Time Management": 30, "Logical Reasoning": 20}
}

def get_skills_for_stream(stream):
    """Return relevant skills for a specific Gov/Defence stream."""
    return GOV_PATH_WEIGHTS.get(stream, {"Logical Reasoning": 40, "Analytical Thinking": 30, "Problem Solving": 30})

def dominant_skill(stream):
    """Return the most important skill for a stream."""
    skills = get_skills_for_stream(stream)
    return max(skills, key=skills.get)

def plot_stream_skills(stream_name):
    """Plots thinking skill distribution for a given stream."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import io

    skills = GOV_PATH_WEIGHTS.get(stream_name)
    if not skills:
        return None

    labels = list(skills.keys())
    values = list(skills.values())

    fig, ax = plt.subplots(figsize=(7, 4))
    colors_list = plt.cm.plasma([i / len(labels) for i in range(len(labels))])
    bars = ax.bar(labels, values, color=colors_list)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)
    ax.set_ylabel('Percentage (%)')
    ax.set_ylim(0, 60)
    ax.set_title(f'Thinking Skills Distribution — {stream_name}', pad=12)
    plt.xticks(rotation=20, ha='right', fontsize=8)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf
