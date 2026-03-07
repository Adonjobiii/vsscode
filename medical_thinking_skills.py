"""
medical_thinking_skills.py

Module: Medical Thinking Skills Distribution
Description: Stores research-informed approximate thinking skill
distribution for different medical fields and provides utilities
to analyze the data.
"""

# -------------------------------
# Thinking Skill Data
# -------------------------------

medical_thinking_skills = {
    "General Medicine (MBBS)": {
        "Critical Thinking": 20,
        "Analytical Thinking": 15,
        "Clinical Reasoning": 25,
        "Decision Making": 15,
        "Problem Solving": 10,
        "Observation Skills": 8,
        "Ethical Thinking": 7
    },

    "Pharmacy": {
        "Critical Thinking": 18,
        "Analytical Thinking": 22,
        "Clinical Reasoning": 15,
        "Decision Making": 10,
        "Problem Solving": 12,
        "Observation Skills": 8,
        "Ethical Thinking": 8
    },

    "Surgery": {
        "Critical Thinking": 15,
        "Analytical Thinking": 14,
        "Clinical Reasoning": 20,
        "Decision Making": 20,
        "Problem Solving": 16,
        "Observation Skills": 7,
        "Ethical Thinking": 8
    },

    "Nursing & Patient Care": {
        "Critical Thinking": 18,
        "Analytical Thinking": 12,
        "Clinical Reasoning": 18,
        "Decision Making": 15,
        "Problem Solving": 12,
        "Observation Skills": 15,
        "Ethical Thinking": 10
    },

    "Dentistry (BDS)": {
        "Critical Thinking": 16,
        "Analytical Thinking": 14,
        "Clinical Reasoning": 22,
        "Decision Making": 14,
        "Problem Solving": 12,
        "Observation Skills": 12,
        "Ethical Thinking": 10
    },

    "Physiotherapy": {
        "Critical Thinking": 15,
        "Analytical Thinking": 18,
        "Clinical Reasoning": 20,
        "Decision Making": 12,
        "Problem Solving": 15,
        "Observation Skills": 10,
        "Ethical Thinking": 10
    },

    "Veterinary Science": {
        "Critical Thinking": 18,
        "Analytical Thinking": 15,
        "Clinical Reasoning": 22,
        "Decision Making": 14,
        "Problem Solving": 14,
        "Observation Skills": 12,
        "Ethical Thinking": 5
    },

    "Ayurveda (BAMS)": {
        "Critical Thinking": 17,
        "Analytical Thinking": 14,
        "Clinical Reasoning": 20,
        "Decision Making": 12,
        "Problem Solving": 12,
        "Observation Skills": 10,
        "Ethical Thinking": 15
    }
}


# -------------------------------
# Utility Functions
# -------------------------------

def get_skills_for_stream(stream_name):
    """Returns thinking skill distribution for a given medical stream."""
    return medical_thinking_skills.get(stream_name, {})


def get_all_streams():
    """Returns list of all medical streams."""
    return list(medical_thinking_skills.keys())


def get_all_skills():
    """Returns unique thinking skills across all streams."""
    skills = set()
    for stream in medical_thinking_skills.values():
        skills.update(stream.keys())
    return list(skills)


def dominant_skill(stream_name):
    """Returns the most dominant thinking skill for a given stream."""
    skills = medical_thinking_skills.get(stream_name)
    if not skills:
        return "Stream not found"
    return max(skills, key=skills.get)


def average_skill_distribution():
    """Calculates average percentage of each thinking skill across all streams."""
    skill_totals = {}
    stream_count = len(medical_thinking_skills)
    for stream in medical_thinking_skills.values():
        for skill, value in stream.items():
            skill_totals[skill] = skill_totals.get(skill, 0) + value
    return {skill: round(total / stream_count, 2) for skill, total in skill_totals.items()}


def plot_stream_skills(stream_name):
    """Plots thinking skill distribution for a given stream (non-interactive for server use)."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    skills = medical_thinking_skills.get(stream_name)
    if not skills:
        return None

    labels = list(skills.keys())
    values = list(skills.values())

    fig, ax = plt.subplots(figsize=(7, 4))
    colors_list = plt.cm.viridis([i / len(labels) for i in range(len(labels))])
    bars = ax.bar(labels, values, color=colors_list)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)
    ax.set_ylabel('Percentage (%)')
    ax.set_ylim(0, 35)
    ax.set_title(f'Thinking Skills Distribution — {stream_name}', pad=12)
    plt.xticks(rotation=30, ha='right', fontsize=8)
    plt.tight_layout()

    import io
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


# -------------------------------
# Example Usage
# -------------------------------

if __name__ == "__main__":
    print("Available Medical Streams:")
    print(get_all_streams())

    print("\nSkills required for MBBS:")
    print(get_skills_for_stream("General Medicine (MBBS)"))

    print("\nDominant skill in Surgery:")
    print(dominant_skill("Surgery"))

    print("\nAverage skill distribution across all streams:")
    print(average_skill_distribution())
