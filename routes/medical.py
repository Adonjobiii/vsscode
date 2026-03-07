from flask import Blueprint, request, jsonify, session, render_template
from bson.objectid import ObjectId
from datetime import datetime
import os

# Import necessary helpers and data
from medical_config import MEDICAL_PREDEFINED_SKILLS, MEDICAL_PREDEFINED_INTERESTS, MEDICAL_OPTIONAL_COURSES
from medical_thinking_skills import get_skills_for_stream, dominant_skill as get_dominant_thinking_skill
from medical_aptitude_questions import (
    MEDICAL_APTITUDE_QUESTIONS, THINKING_SKILLS as MEDICAL_THINKING_SKILLS, get_test_questions as get_medical_test_questions
)

# We need to access these from the main app or a shared config
# For now, we'll assume they are imported from config_data or passed via current_app
from config_data import users_collection, assessment_history

medical_bp = Blueprint('medical', __name__)

@medical_bp.route('/medical_step1.html')
def get_medical_step1():
    return render_template('medical_step1.html')

@medical_bp.route('/api/save_medical_step1', methods=['POST'])
def save_medical_step1():
    if 'user_id' not in session:
        return jsonify({"error": "No user session"}), 401
    
    data = request.json
    priority_list = data.get('career_priority_list', [])
    
    # Clear previous assessment data to prevent mix-ups
    session.pop('career_recommendation', None)
    session.pop('aptitude_recommendation', None)
    session.pop('personality_result', None)
    session.pop('medical_aptitude_questions', None)
    session.pop('commerce_aptitude_questions', None)
    session.pop('aptitude_questions', None)
    
    session['career_priority_list'] = priority_list
    session['assessment_track'] = 'medical' 
    return jsonify({"message": "Medical priorities saved successfully"}), 200

@medical_bp.route('/medical_assesment.html')
def medical_assessment():
    return render_template('medical_assesment.html')

@medical_bp.route('/api/get_medical_test_questions', methods=['GET'])
def get_medical_test():
    questions = get_medical_test_questions()
    return jsonify(questions)

@medical_bp.route('/api/medical_aptitude_questions', methods=['GET'])
def get_medical_aptitude_questions():
    questions = get_medical_test_questions(n_per_thinking_skill=7, n_per_core_subject=5)
    session['medical_aptitude_questions'] = [
        {"id": q['id'], "category": q['category'], "answer": q['answer']}
        for q in questions
    ]
    visible = []
    for q in questions:
        q_out = {k: v for k, v in q.items() if k != 'answer'}
        visible.append(q_out)
    return jsonify(visible)

@medical_bp.route('/api/submit_medical_aptitude', methods=['POST'])
def submit_medical_aptitude():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    answers = request.json.get('answers', {})

    # Weighted distributions per field provided by user
    MEDICAL_FIELDS_WEIGHTS = {
        "General Medicine (MBBS)": {"biology": 0.70, "chemistry": 0.30},
        "Pharmacy":                {"biology": 0.45, "chemistry": 0.55},
        "Surgery":                 {"biology": 0.75, "chemistry": 0.25},
        "Nursing & Patient Care":  {"biology": 0.70, "chemistry": 0.30},
        "Dentistry (BDS)":         {"biology": 0.65, "chemistry": 0.35},
        "Physiotherapy":           {"biology": 0.70, "chemistry": 0.30},
        "Veterinary Science":      {"biology": 0.70, "chemistry": 0.30},
        "Ayurveda (BAMS)":         {"biology": 0.65, "chemistry": 0.35}
    }

    # Score categories
    THINKING_SKILLS = ["Critical Thinking", "Analytical Thinking", "Clinical Reasoning", "Decision Making", "Problem Solving", "Observation Skills", "Ethical Thinking"]
    CORE_SUBJECTS = ["Biology", "Chemistry"]
    
    scores = {cat: 0 for cat in (THINKING_SKILLS + CORE_SUBJECTS)}
    counts_target = {cat: 0 for cat in (THINKING_SKILLS + CORE_SUBJECTS)}
    counts_answered = {cat: 0 for cat in (THINKING_SKILLS + CORE_SUBJECTS)}

    session_qs = session.get('medical_aptitude_questions', [])
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

    # Logic 1: Weighted Field Recommendation (based on Bio/Chem)
    bio_pct = (scores["Biology"] / max(counts_answered["Biology"], 1)) if counts_answered["Biology"] > 0 else 0
    chem_pct = (scores["Chemistry"] / max(counts_answered["Chemistry"], 1)) if counts_answered["Chemistry"] > 0 else 0
    
    field_scores = {}
    for field, weights in MEDICAL_FIELDS_WEIGHTS.items():
        val = (bio_pct * weights["biology"]) + (chem_pct * weights["chemistry"])
        field_scores[field] = round(val * 100, 2)

    rec_stream = max(field_scores, key=field_scores.get)
    probabilities = {field: round(min(98.0, 45 + val * 0.5), 1) for field, val in field_scores.items()}

    total_correct_thinking = sum(scores.get(c, 0) for c in THINKING_SKILLS)
    total_ans_thinking = sum(counts_answered.get(c, 0) for c in THINKING_SKILLS)
    thinking_acc = total_correct_thinking / max(total_ans_thinking, 1) if total_ans_thinking > 0 else 0
    
    completion_rate = sum(counts_answered.values()) / max(sum(counts_target.values()), 1)
    confidence = round(50 + (thinking_acc * 20) + (bio_pct * 10) + (chem_pct * 10), 1)
    if completion_rate < 0.5: confidence *= 0.8

    thinking_skills = get_skills_for_stream(rec_stream)
    dom_skill = get_dominant_thinking_skill(rec_stream)

    result = {
        "recommended_stream": rec_stream,
        "confidence": round(confidence, 1),
        "scores": scores, 
        "probabilities": probabilities,
        "thinking_skills": thinking_skills,
        "dominant_thinking_skill": dom_skill,
        "field_scores": field_scores,
        "completion_rate": round(completion_rate * 100, 1)
    }
    
    session['aptitude_recommendation'] = result
    session['assessment_track'] = 'medical'

    user_id = session.get('user_id')
    if user_id and assessment_history is not None:
        try:
            assessment_history.insert_one({
                "user_id": ObjectId(user_id),
                "type": "medical_aptitude",
                "recommended_stream": rec_stream,
                "confidence": result["confidence"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Completed"
            })
        except Exception as e:
            print(f"Error saving medical assessment: {e}")

    return jsonify(result)
