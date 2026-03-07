from flask import Blueprint, request, jsonify, session, render_template
import numpy as np
from bson.objectid import ObjectId
from datetime import datetime
import random

# Import data and models from main config or specific files
from config_data import (
    ENGINEERING_TASKS, APTITUDE_MODEL_CATEGORIES, career_course_map, aptitude_course_map,
    users_collection, assessment_history
)

# These would ideally be imported from the main app or a shared model loader
# For this blueprint to work, we'll need to reference them from a shared place
# For now, let's assume they are globally available or will be linked
# from flask import current_app
# ML_MODELS = current_app.config['ML_MODELS']

engineering_bp = Blueprint('engineering', __name__)

@engineering_bp.route('/assesment.html')
def assessment():
    return render_template('assesment.html')

@engineering_bp.route('/step1.html')
def get_step1():
    return render_template('step1.html')

@engineering_bp.route('/api/save_step1', methods=['POST'])
def save_step1():
    if 'user_id' not in session:
        return jsonify({"error": "No user session"}), 401
    
    data = request.json
    priority_list = data.get('career_priority_list', [])
    session['career_priority_list'] = priority_list
    return jsonify({"message": "Priorities saved successfully"}), 200

@engineering_bp.route('/api/engineering_tasks', methods=['GET'])
def get_engineering_tasks():
    return jsonify({
        "tasks": list(ENGINEERING_TASKS.keys())
    })

@engineering_bp.route('/api/recommend_stream', methods=['POST'])
def recommend_stream():
    # Note: Accessing ML_MODELS requires them to be either in a shared module or current_app
    from app import ML_MODELS # Temporary until full refactor
    data = request.json
    ratings = data.get('ratings', []) 
    
    if len(ratings) != len(ENGINEERING_TASKS):
        return jsonify({"error": "Invalid number of ratings"}), 400

    user_input = np.array(ratings).reshape(1, -1)
    probabilities = ML_MODELS.career_model.predict_proba(user_input)[0]
    sorted_indices = np.argsort(probabilities)[::-1]
    
    top_recommendations = []
    for i in sorted_indices: 
        course = career_course_map[i]
        confidence = float(probabilities[i] * 100)
        top_recommendations.append({"course": course, "confidence": confidence})
        
    session['career_recommendation'] = top_recommendations[0]
        
    # LOG FOR RETRAINING: Use user's priority as the "ground truth"
    priority_list = session.get('career_priority_list', [])
    if priority_list:
        top_interest = priority_list[0]
        # Find index of top interest in ENG_STREAMS
        from config_data import ENG_STREAMS
        if top_interest in ENG_STREAMS:
            label = ENG_STREAMS.index(top_interest)
            ML_MODELS.log_and_retrain_career(ratings, label)
        
    return jsonify({
        "recommended_stream": top_recommendations[0]["course"],
        "confidence": top_recommendations[0]["confidence"],
        "top_recommendations": top_recommendations
    })

@engineering_bp.route('/api/aptitude_questions', methods=['GET'])
def get_aptitude_questions():
    from app import DATA_PROCESSOR # Temporary until full refactor
    all_selected_questions = []
    available_categories = [cat for cat in sorted(DATA_PROCESSOR.QUESTIONS.keys()) if DATA_PROCESSOR.QUESTIONS[cat]]
    QUESTIONS_PER_CATEGORY = 7
    
    for section in available_categories:
        if section in APTITUDE_MODEL_CATEGORIES:
            qs = DATA_PROCESSOR.QUESTIONS[section]
            k = min(QUESTIONS_PER_CATEGORY, len(qs)) 
            if k == 0: continue
        
            qs_selected = random.sample(qs, k)
            for q in qs_selected:
                q_copy = q.copy()
                q_copy['category'] = section
                all_selected_questions.append(q_copy)

    random.shuffle(all_selected_questions)
    session['aptitude_questions'] = [{"id": q['id'], "category": q['category']} for q in all_selected_questions]
    return jsonify(all_selected_questions)

@engineering_bp.route('/api/submit_aptitude', methods=['POST'])
def submit_aptitude():
    from app import DATA_PROCESSOR, ML_MODELS # Temporary
    answers = request.json.get('answers', {})
    
    scores = {cat: 0 for cat in APTITUDE_MODEL_CATEGORIES}
    section_answered = {cat: 0 for cat in APTITUDE_MODEL_CATEGORIES}
    section_counts = {cat: 0 for cat in APTITUDE_MODEL_CATEGORIES}
    
    session_qs = session.get('aptitude_questions', [])
    for q in session_qs:
        cat = q['category']
        q_id = q['id']
        section_counts[cat] += 1
        
        ans_key = f"{cat}_{q_id}"
        if ans_key in answers:
            user_ans = str(answers[ans_key]).upper().strip()
            if user_ans:
                section_answered[cat] += 1
                correct_ans = str(DATA_PROCESSOR.CORRECT_ANSWERS[cat].get(q_id, "")).upper().strip()
                if user_ans == correct_ans:
                    scores[cat] += 1
                
    user_scores_list = []
    for cat in APTITUDE_MODEL_CATEGORIES:
        if section_answered[cat] > 0:
            user_scores_list.append(scores[cat] / section_answered[cat])
        else:
            user_scores_list.append(0)
            
    user_scores_array = np.array(user_scores_list).reshape(1, -1)
    probabilities = ML_MODELS.aptitude_model.predict_proba(user_scores_array)[0]
    predicted_aptitude_id = np.argmax(probabilities)
    
    completion_rate = sum(section_answered.values()) / max(sum(section_counts.values()), 1)
    
    result = {
        "recommended_stream": aptitude_course_map[predicted_aptitude_id],
        "confidence": round(float(probabilities[predicted_aptitude_id] * 100), 1),
        "scores": scores,
        "probabilities": {aptitude_course_map[i]: float(probabilities[i] * 100) for i in range(len(probabilities))},
        "completion_rate": round(completion_rate * 100, 1)
    }
    session['aptitude_recommendation'] = result
    
    # LOG FOR RETRAINING: Log features and current prediction
    ML_MODELS.log_and_retrain_aptitude(user_scores_list, predicted_aptitude_id)
    
    user_id = session.get('user_id')
    if user_id and assessment_history is not None:
        try:
            assessment_history.insert_one({
                "user_id": ObjectId(user_id),
                "type": "engineering_aptitude",
                "recommended_stream": result["recommended_stream"],
                "confidence": result["confidence"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Completed"
            })
        except Exception as e:
            print(f"Error saving engineering assessment: {e}")

    return jsonify(result)
