from flask import Blueprint, request, jsonify, session, render_template
from bson.objectid import ObjectId
from datetime import datetime
import random

# Import Law specific modules
from law_config import LAW_PREDEFINED_SKILLS, LAW_PREDEFINED_INTERESTS, LAW_OPTIONAL_COURSES, determine_law_interests
from law_thinking_skills import get_skills_for_stream, dominant_skill as get_dominant_thinking_skill
from law_questions import LAW_APTITUDE_QUESTIONS, get_test_questions as get_law_test_questions

from config_data import users_collection, assessment_history

law_bp = Blueprint('law', __name__)

@law_bp.route('/law_step1.html')
def get_law_step1():
    return render_template('law_step1.html')

@law_bp.route('/api/save_law_step1', methods=['POST'])
def save_law_step1():
    if 'user_id' not in session:
        return jsonify({"error": "No user session"}), 401
    
    data = request.json
    priority_list = data.get('career_priority_list', [])
    
    # Clear previous assessment data
    session.pop('career_recommendation', None)
    session.pop('aptitude_recommendation', None)
    session.pop('personality_result', None)
    session.pop('law_aptitude_questions', None)
    
    session['career_priority_list'] = priority_list
    session['assessment_track'] = 'law'
    
    results = determine_law_interests([], priority_list)
    session['career_recommendation'] = results
    
    return jsonify({"message": "Law priorities saved successfully"}), 200

@law_bp.route('/law_assesment.html')
def law_assessment():
    return render_template('law_assesment.html')

@law_bp.route('/api/law_aptitude_questions', methods=['GET'])
def get_law_aptitude_questions():
    questions = get_law_test_questions()
    session['law_aptitude_questions'] = [
        {"id": q['id'], "category": q['category'], "answer": q['answer']}
        for q in questions
    ]
    visible = []
    for q in questions:
        q_out = {k: v for k, v in q.items() if k != 'answer'}
        visible.append(q_out)
    return jsonify(visible)

@law_bp.route('/api/submit_law_aptitude', methods=['POST'])
def submit_law_aptitude():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    answers = request.json.get('answers', {})
    
    THINKING_SKILLS = [
        "Critical Thinking", "Analytical Thinking", "Logical Reasoning", 
        "Problem Solving", "Decision Making", "Creative Thinking", 
        "Research Thinking", "Ethical Reasoning", "Strategic Thinking"
    ]
    
    scores = {cat: 0 for cat in THINKING_SKILLS}
    counts_target = {cat: 0 for cat in THINKING_SKILLS}
    counts_answered = {cat: 0 for cat in THINKING_SKILLS}

    session_qs = session.get('law_aptitude_questions', [])
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

    # Simple logic for recommendation based on top skill
    skill_acc = {s: (scores[s]/max(counts_answered[s], 1)) if counts_answered[s]>0 else 0 for s in THINKING_SKILLS}
    
    # Weight paths by skills
    PATH_WEIGHTS = {
        "Litigation & Advocacy": {"Critical Thinking": 0.4, "Logical Reasoning": 0.3, "Strategic Thinking": 0.3},
        "Corporate Law": {"Analytical Thinking": 0.4, "Problem Solving": 0.3, "Decision Making": 0.3},
        "Legal Research & Academia": {"Research Thinking": 0.5, "Analytical Thinking": 0.3, "Ethical Reasoning": 0.2}
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
    
    # LOG FOR RETRAINING: Log features and current prediction
    from app import ML_MODELS
    # Using the raw scores as features
    feature_list = list(result.get('scores', {}).values())
    if feature_list:
        ML_MODELS.log_and_retrain_aptitude(
            feature_list, 
            0, # Defaulting to 0 for law as there's only one main 'Law' stream predicted
            track="law", 
            metadata={
            "detailed_scores": result.get('scores'), 
            "answering_patterns": request.json.get('answers', {}),
            "personality": session.get('personality_result')
        }
        )

    user_id = session.get('user_id')
    if user_id and assessment_history is not None:
        try:
            assessment_history.insert_one({
                "user_id": ObjectId(user_id),
                "type": "law_aptitude",
                "recommended_stream": rec_stream,
                "confidence": confidence,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Completed"
            })
        except Exception as e:
            print(f"Error saving law assessment: {e}")

    return jsonify(result)
