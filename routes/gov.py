from flask import Blueprint, request, jsonify, session, render_template
from bson.objectid import ObjectId
from datetime import datetime
import random

# Import Gov specific modules
from gov_config import GOV_PREDEFINED_SKILLS, GOV_PREDEFINED_INTERESTS, GOV_OPTIONAL_COURSES, determine_gov_interests
from gov_thinking_skills import get_skills_for_stream, dominant_skill as get_dominant_thinking_skill
from gov_questions import get_gov_test_questions

from config_data import users_collection, assessment_history

gov_bp = Blueprint('gov', __name__)

@gov_bp.route('/gov_step1.html')
def get_gov_step1():
    return render_template('gov_step1.html')

@gov_bp.route('/api/save_gov_step1', methods=['POST'])
def save_gov_step1():
    if 'user_id' not in session:
        return jsonify({"error": "No user session"}), 401
    
    data = request.json
    priority_list = data.get('career_priority_list', [])
    
    # Clear previous assessment data
    session.pop('career_recommendation', None)
    session.pop('aptitude_recommendation', None)
    session.pop('personality_result', None)
    session.pop('gov_aptitude_questions', None)
    
    session['career_priority_list'] = priority_list
    session['assessment_track'] = 'government & defence'
    return jsonify({"message": "Government priorities saved successfully"}), 200

@gov_bp.route('/gov_assesment.html')
def gov_assessment():
    return render_template('gov_assesment.html')

@gov_bp.route('/api/gov_aptitude_questions', methods=['GET'])
def get_gov_aptitude_questions():
    questions = get_gov_test_questions()
    session['gov_aptitude_questions'] = [
        {"id": q['id'], "category": q['category'], "answer": q['answer']}
        for q in questions
    ]
    visible = []
    for q in questions:
        q_out = {k: v for k, v in q.items() if k != 'answer'}
        visible.append(q_out)
    return jsonify(visible)

@gov_bp.route('/api/submit_gov_aptitude', methods=['POST'])
def submit_gov_aptitude():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    answers = request.json.get('answers', {})
    
    THINKING_SKILLS = [
        "Logical Reasoning", "Analytical Thinking", "Problem Solving",
        "Critical Thinking", "Decision Making", "Memory Recall",
        "Strategic Thinking", "Observation Skills", "Time Management"
    ]
    
    scores = {cat: 0 for cat in THINKING_SKILLS}
    counts_target = {cat: 0 for cat in THINKING_SKILLS}
    counts_answered = {cat: 0 for cat in THINKING_SKILLS}

    session_qs = session.get('gov_aptitude_questions', [])
    if not session_qs:
        return jsonify({"error": "Session lost. Please restart the test."}), 400

    for q in session_qs:
        cat = q.get('category', '')
        if cat not in scores: continue
        
        q_id = q.get('id', '')
        correct = str(q.get('answer', '')).upper().strip()
        counts_target[cat] += 1

        ans_key = f"{cat}_{q_id}"
        user_ans = str(answers.get(ans_key, '')).upper().strip()
        if user_ans:
            counts_answered[cat] += 1
            if user_ans == correct:
                scores[cat] += 1

    # Analysis
    skill_acc = {s: (scores[s]/max(counts_answered[s], 1)) if counts_answered[s]>0 else 0 for s in THINKING_SKILLS}
    
    PATH_WEIGHTS = {
        "Civil Services": {"Critical Thinking": 0.4, "Analytical Thinking": 0.3, "Decision Making": 0.3},
        "Defence": {"Strategic Thinking": 0.4, "Observation Skills": 0.3, "Problem Solving": 0.3},
        "State/Central Gov": {"Memory Recall": 0.5, "Time Management": 0.3, "Logical Reasoning": 0.2}
    }
    
    path_scores = {}
    for path, weights in PATH_WEIGHTS.items():
        s = sum(skill_acc.get(skill, 0) * weight for skill, weight in weights.items())
        path_scores[path] = round(s * 100, 2)
        
    rec_stream = max(path_scores, key=path_scores.get)
    confidence = round(50 + (path_scores[rec_stream] * 0.4), 1)
    completion_rate = sum(counts_answered.values()) / max(sum(counts_target.values()), 1)

    result = {
        "recommended_stream": rec_stream,
        "confidence": confidence,
        "scores": scores,
        "probabilities": path_scores,
        "thinking_skills": get_skills_for_stream(rec_stream),
        "dominant_thinking_skill": get_dominant_thinking_skill(rec_stream),
        "completion_rate": round(completion_rate * 100, 1)
    }
    
    session['aptitude_recommendation'] = result
    session['assessment_track'] = 'government & defence'
    
    user_id = session.get('user_id')
    if user_id and assessment_history is not None:
        try:
            assessment_history.insert_one({
                "user_id": ObjectId(user_id),
                "type": "gov_aptitude",
                "recommended_stream": rec_stream,
                "confidence": confidence,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Completed"
            })
        except Exception as e:
            print(f"Error saving gov assessment: {e}")

    return jsonify(result)
