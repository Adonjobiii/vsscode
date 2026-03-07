from flask import Blueprint, request, jsonify, session, render_template
from bson.objectid import ObjectId
from datetime import datetime

# Import necessary commerce helpers and data
from commerce_aptitude_questions import (
    COMMERCE_APTITUDE_QUESTIONS, THINKING_SKILLS as COMMERCE_THINKING_SKILLS, get_test_questions as get_commerce_test_questions
)
from commerce_config import (
    COMMERCE_PREDEFINED_SKILLS, COMMERCE_PREDEFINED_INTERESTS, COMMERCE_OPTIONAL_COURSES,
    determine_commerce_interests, determine_commerce_course_by_aptitude
)

# Shared config/db
from config_data import users_collection, assessment_history

commerce_bp = Blueprint('commerce', __name__)

@commerce_bp.route('/commerce_step1.html')
def get_commerce_step1():
    return render_template('commerce_step1.html')

@commerce_bp.route('/api/save_commerce_step1', methods=['POST'])
def save_commerce_step1():
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
    session['assessment_track'] = 'commerce' 
    
    # Pre-calculate interest recommendation so it doesn't default to engineering
    results = determine_commerce_interests([], priority_list)
    session['career_recommendation'] = results
    
    return jsonify({"message": "Commerce priorities saved successfully"}), 200

@commerce_bp.route('/commerce_assesment.html')
def commerce_assessment():
    return render_template('commerce_assesment.html')

@commerce_bp.route('/api/get_commerce_test_questions', methods=['GET'])
def get_commerce_test():
    questions = get_commerce_test_questions()
    return jsonify(questions)

@commerce_bp.route('/api/commerce_aptitude_questions', methods=['GET'])
def get_commerce_aptitude_questions():
    questions = get_commerce_test_questions()
    session['commerce_aptitude_questions'] = [
        {"id": q['id'], "category": q['category'], "answer": q['answer']}
        for q in questions
    ]
    visible = []
    for q in questions:
        q_out = {k: v for k, v in q.items() if k != 'answer'}
        visible.append(q_out)
    return jsonify(visible)

@commerce_bp.route('/api/submit_commerce_interests', methods=['POST'])
def submit_commerce_interests():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    priorities = data.get('priorities', [])
    
    session['career_priority_list'] = priorities
    session['assessment_track'] = 'commerce'
    
    results = determine_commerce_interests([], priorities)
    session['career_recommendation'] = results
    
    user_id = session.get('user_id')
    if user_id:
        if users_collection is not None:
            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "career_priority_list": priorities,
                    "career_recommendation": results,
                    "assessment_track": "commerce"
                }}
            )
        if assessment_history is not None:
            try:
                assessment_history.insert_one({
                    "user_id": ObjectId(user_id),
                    "type": "commerce_interests",
                    "result": results,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "Saved"
                })
            except Exception as e:
                print(f"Error saving commerce interests: {e}")

    return jsonify({"success": True, "recommendation": results})

@commerce_bp.route('/api/submit_commerce_aptitude', methods=['POST'])
def submit_commerce_aptitude():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    answers = request.json.get('answers', {})
    
    scores = {cat: 0 for cat in (COMMERCE_THINKING_SKILLS + ["Accountancy", "Economics"])}
    counts_target = {cat: 0 for cat in (COMMERCE_THINKING_SKILLS + ["Accountancy", "Economics"])}
    counts_answered = {cat: 0 for cat in (COMMERCE_THINKING_SKILLS + ["Accountancy", "Economics"])}

    session_qs = session.get('commerce_aptitude_questions', [])
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

    skill_percentages = {s: (scores[s]/max(counts_answered[s], 1)*100) if counts_answered[s]>0 else 0 for s in COMMERCE_THINKING_SKILLS}
    rec = determine_commerce_course_by_aptitude(skill_percentages)
    completion_rate = sum(counts_answered.values()) / max(sum(counts_target.values()), 1)
    
    result = {
        "recommended_stream": rec["recommended_stream"],
        "confidence": round(rec["confidence"], 1),
        "scores": scores,
        "probabilities": rec["probabilities"],
        "completion_rate": round(completion_rate * 100, 1)
    }
    
    session['aptitude_recommendation'] = result
    session['assessment_track'] = 'commerce'
    
    user_id = session.get('user_id')
    if user_id:
        if users_collection is not None:
            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "aptitude_recommendation": result,
                    "assessment_track": "commerce"
                }}
            )
        if assessment_history is not None:
            try:
                assessment_history.insert_one({
                    "user_id": ObjectId(user_id),
                    "type": "commerce_aptitude",
                    "recommended_stream": result["recommended_stream"],
                    "confidence": result["confidence"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "Completed"
                })
            except Exception as e:
                print(f"Error saving commerce assessment: {e}")
    
    return jsonify(result)
