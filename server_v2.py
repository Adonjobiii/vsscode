import os
import pymongo
import numpy as np
from flask import Flask, request, jsonify, render_template, session, send_file, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from authlib.integrations.flask_client import OAuth

from config_data import *
from medical_config import *
from medical_thinking_skills import get_skills_for_stream, dominant_skill as get_dominant_thinking_skill
from medical_aptitude_questions import (
    MEDICAL_APTITUDE_QUESTIONS, THINKING_SKILLS as MEDICAL_THINKING_SKILLS, get_test_questions as get_medical_test_questions
)
from commerce_aptitude_questions import (
    COMMERCE_APTITUDE_QUESTIONS, THINKING_SKILLS as COMMERCE_THINKING_SKILLS, get_test_questions as get_commerce_test_questions
)
from commerce_config import (
    COMMERCE_PREDEFINED_SKILLS, COMMERCE_PREDEFINED_INTERESTS, COMMERCE_OPTIONAL_COURSES,
    determine_commerce_interests, determine_commerce_course_by_aptitude
)
from course_data import COURSE_DATA, KERALA_COLLEGES
from ml_logic import DataProcessor, MLModelTrainer
from pdf_generator import generate_assessment_report

app = Flask(__name__)
app.secret_key = "career_assessment_secret_key" # Needed for session management

# OAuth Configuration
oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID', 'placeholder-google-client-id'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET', 'placeholder-google-client-secret'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)

apple = oauth.register(
    name='apple',
    client_id=os.environ.get('APPLE_CLIENT_ID', 'placeholder-apple-client-id'),
    client_secret=os.environ.get('APPLE_CLIENT_SECRET', 'placeholder-apple-client-secret'),
    access_token_url='https://appleid.apple.com/auth/token',
    access_token_params=None,
    authorize_url='https://appleid.apple.com/auth/authorize',
    authorize_params=None,
    api_base_url='https://appleid.apple.com/',
    client_kwargs={'scope': 'name email'},
)

# Initialize Data & Models
DATA_PROCESSOR = DataProcessor()
ML_MODELS = MLModelTrainer()

# MongoDB Setup is now handled in config_data.py
# users_collection is imported via 'from config_data import *'

# Big Five Configuration (from career1supp.py)
TRAITS = {
    'O': {"name": "Openness", "color": "#3498db"},
    'C': {"name": "Conscientiousness", "color": "#2ecc71"},
    'E': {"name": "Extraversion", "color": "#f1c40f"},
    'A': {"name": "Agreeableness", "color": "#9b59b6"},
    'N': {"name": "Neuroticism", "color": "#e74c3c"}
}

QUESTIONNAIRE = {
    1:['E',"Is talkative.",False], 2:['A',"Tends to find fault with others.",True],
    3:['C',"Does a thorough job.",False], 4:['N',"Is depressed, blue.",False],
    5:['O',"Is original, comes up with new ideas.",False], 6:['E',"Is reserved.",True],
    7:['A',"Is helpful and unselfish with others.",False], 8:['C',"Can be somewhat careless.",True],
    9:['N',"Is relaxed, handles stress well.",True], 10:['O',"Is curious about many different things.",False],
    11:['E',"Is full of energy.",False], 12:['A',"Starts quarrels with others.",True],
    13:['C',"Is a reliable worker.",False], 14:['N',"Can be tense.",False],
    15:['O',"Is ingenious, a deep thinker.",False], 16:['E',"Generates a lot of enthusiasm.",False],
    17:['A',"Has a forgiving nature.",False], 18:['C',"Tends to be disorganized.",True],
    19:['N',"Worries a lot.",False], 20:['O',"Has an active imagination.",False],
    21:['E',"Tends to be quiet.",True], 22:['A',"Is generally trusting.",False],
    23:['C',"Tends to be lazy.",True], 24:['N',"Is emotionally stable, not easily upset.",True],
    25:['O',"Is inventive.",False], 26:['E',"Has an assertive personality.",False],
    27:['A',"Can be cold and aloof.",True], 28:['C',"Perseveres until the task is finished.",False],
    29:['N',"Can be moody.",False], 30:['O',"Values artistic experiences.",False],
    31:['E',"Is sometimes shy, inhibited.",True], 32:['A',"Is considerate and kind.",False],
    33:['C',"Does things efficiently.",False], 34:['N',"Remains calm in tense situations.",True],
    35:['O',"Prefers routine work.",True], 36:['E',"Is outgoing, sociable.",False],
    37:['A',"Is sometimes rude to others.",True], 38:['C',"Makes plans and follows through with them.",False],
    39:['N',"Gets nervous easily.",False], 40:['O',"Likes to reflect, play with ideas.",False],
    41:['O',"Has few artistic interests.",True], 42:['A',"Likes to cooperate.",False],
    43:['C',"Is easily distracted.",True], 44:['O',"Is sophisticated in art, music, literature.",False],
}


# ==========================================
# HTML ROUTES
# ==========================================

@app.route('/')
def index():
    return render_template('mainpage1.html')

@app.route('/signin.html')
def signin():
    return render_template('signin.html')

@app.route('/step1.html')
def get_step1():
    return render_template('step1.html')

@app.route('/api/save_step1', methods=['POST'])
def save_step1():
    if 'user_id' not in session:
        return jsonify({"error": "No user session"}), 401
    
    data = request.json
    priority_list = data.get('career_priority_list', [])
    
    # Store it in the session so ML models can access it later for the final report
    session['career_priority_list'] = priority_list
    return jsonify({"message": "Priorities saved successfully"}), 200

@app.route('/hobbies.html')
def profile():
    return render_template('hobbies.html')

@app.route('/homepage.html')
def dashboard():
    return render_template('homepage.html')

@app.route('/assesment.html')
def assessment():
    return render_template('assesment.html')

@app.route('/personality.html')
def personality():
    return render_template('personality.html')

@app.route('/medical_step1.html')
def get_medical_step1():
    return render_template('medical_step1.html')

@app.route('/api/save_medical_step1', methods=['POST'])
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

@app.route('/commerce_step1.html')
def get_commerce_step1():
    return render_template('commerce_step1.html')

@app.route('/api/save_commerce_step1', methods=['POST'])
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

@app.route('/medical_assesment.html')
def medical_assessment():
    return render_template('medical_assesment.html')

@app.route('/commerce_assesment.html')
def commerce_assessment():
    return render_template('commerce_assesment.html')

@app.route('/api/get_medical_test_questions', methods=['GET'])
def get_medical_test():
    questions = get_medical_test_questions()
    return jsonify(questions)

@app.route('/api/get_commerce_test_questions', methods=['GET'])
def get_commerce_test():
    questions = get_commerce_test_questions()
    return jsonify(questions)

@app.route('/api/medical_aptitude_questions', methods=['GET'])
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

@app.route('/api/commerce_aptitude_questions', methods=['GET'])
def get_commerce_aptitude_questions():
    questions = get_commerce_test_questions()
    session['commerce_aptitude_questions'] = [
        {"id": q['id'], "category": q['category'], "answer": q['answer']}
        for q in questions
    ]
    visible = []
    for q in questions:
        # Shallow copy to avoid mutating session storage
        q_out = {k: v for k, v in q.items() if k != 'answer'}
        visible.append(q_out)
    return jsonify(visible)

@app.route('/api/submit_medical_aptitude', methods=['POST'])
def submit_medical_aptitude():
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
    # Use answered questions as denominator for performance percentage
    bio_pct = (scores["Biology"] / max(counts_answered["Biology"], 1)) if counts_answered["Biology"] > 0 else 0
    chem_pct = (scores["Chemistry"] / max(counts_answered["Chemistry"], 1)) if counts_answered["Chemistry"] > 0 else 0
    
    field_scores = {}
    for field, weights in MEDICAL_FIELDS_WEIGHTS.items():
        # Formula: (bio% * bioWt) + (chem% * chemWt)
        val = (bio_pct * weights["biology"]) + (chem_pct * weights["chemistry"])
        field_scores[field] = round(val * 100, 2)

    rec_stream = max(field_scores, key=field_scores.get)
    
    # Probabilities for UI Bar Chart
    probabilities = {field: round(min(98.0, 45 + val * 0.5), 1) for field, val in field_scores.items()}

    # Overall Confidence (mix of accuracy and volume of questions answered)
    total_correct_thinking = sum(scores.get(c, 0) for c in THINKING_SKILLS)
    total_ans_thinking = sum(counts_answered.get(c, 0) for c in THINKING_SKILLS)
    thinking_acc = total_correct_thinking / max(total_ans_thinking, 1) if total_ans_thinking > 0 else 0
    
    # Scale confidence slightly by how much of the test was actually completed
    completion_rate = sum(counts_answered.values()) / max(sum(counts_target.values()), 1)
    confidence = round(50 + (thinking_acc * 20) + (bio_pct * 10) + (chem_pct * 10), 1)
    if completion_rate < 0.5: confidence *= 0.8 # Penalty for very low completion

    # Thinking skills data for diagnostic profile
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
    return jsonify(result)

@app.route('/api/submit_commerce_interests', methods=['POST'])
def submit_commerce_interests():
    # Similar to medical but for commerce
    data = request.json
    priorities = data.get('priorities', [])
    
    # Store in session and DB
    session['career_priority_list'] = priorities
    session['assessment_track'] = 'commerce'
    
    results = determine_commerce_interests([], priorities)
    session['career_recommendation'] = results
    
    user_id = session.get('user_id')
    if user_id:
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "career_priority_list": priorities,
                "career_recommendation": results,
                "assessment_track": "commerce"
            }}
        )
    return jsonify({"success": True, "recommendation": results})

@app.route('/api/submit_commerce_aptitude', methods=['POST'])
def submit_commerce_aptitude():
    answers = request.json.get('answers', {})
    
    # COMMERCE_THINKING_SKILLS = ["Analytical Thinking", "Numerical Ability", "Logical Reasoning", "Creativity", "Communication", "Problem Solving"]
    # CORE_SUBJECTS = ["Accountancy", "Economics"]
    
    scores = {cat: 0 for cat in (COMMERCE_THINKING_SKILLS + ["Accountancy", "Economics"])}
    counts_target = {cat: 0 for cat in (COMMERCE_THINKING_SKILLS + ["Accountancy", "Economics"])}
    counts_answered = {cat: 0 for cat in (COMMERCE_THINKING_SKILLS + ["Accountancy", "Economics"])}

    # Assuming we sample questions and store in session like medical
    # But for now let's just use the answers keys if they are prefixed
    # or follow the medical logic of session storage
    
    session_qs = session.get('commerce_aptitude_questions', [])
    if not session_qs:
        # Fallback if session expired or lost
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

    # Calculation
    skill_percentages = {s: (scores[s]/max(counts_answered[s], 1)*100) if counts_answered[s]>0 else 0 for s in COMMERCE_THINKING_SKILLS}
    
    # Use recommendation engine from commerce_config
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
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "aptitude_recommendation": result,
                "assessment_track": "commerce"
            }}
        )
    
    return jsonify(result)

# ==========================================
# ==========================================

@app.route('/api/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')

@app.route('/api/signup', methods=['POST'])
def signup():
    if users_collection is None:
         return jsonify({"error": "Database error."}), 503

    data = request.json
    try:
        # Check if basic fields exist
        if not data.get('first_name') or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Fields missing. Profile requires Name, Email, and Password."}), 400
            
        # Check if email is unique
        if users_collection.find_one({"email": data.get('email')}):
            return jsonify({"error": "An account with this email already exists."}), 400
            
        # Hash password
        hashed_pw = generate_password_hash(data.get('password'))
        data['password'] = hashed_pw

        result = users_collection.insert_one(data)
        session['user_id'] = str(result.inserted_id)
        
        return jsonify({"message": "User registered", "id": str(result.inserted_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    if users_collection is None:
        return jsonify({"error": "Database error."}), 503

    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = users_collection.find_one({"email": email})
    
    if not user or 'password' not in user or not check_password_hash(user['password'], password):
        return jsonify({"error": "Invalid email or password."}), 401

    session['user_id'] = str(user['_id'])
    return jsonify({"message": "Logged in successfully", "id": str(user['_id'])}), 200

# ==========================================
# OAUTH ROUTES
# ==========================================

@app.route('/login/<provider>')
def oauth_login(provider):
    if provider == 'google':
        # Bypass real OAuth redirect if no real Client ID is supplied to prevent Google 401 Error
        if not os.environ.get('GOOGLE_CLIENT_ID'):
            return redirect(url_for('oauth_authorize', provider=provider))
        redirect_uri = url_for('oauth_authorize', provider=provider, _external=True)
        return google.authorize_redirect(redirect_uri)
    elif provider == 'apple':
        if not os.environ.get('APPLE_CLIENT_ID'):
            return redirect(url_for('oauth_authorize', provider=provider))
        redirect_uri = url_for('oauth_authorize', provider=provider, _external=True)
        return apple.authorize_redirect(redirect_uri)
    return jsonify({"error": "Unsupported provider"}), 400

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    try:
        if provider == 'google':
            token = google.authorize_access_token()
            resp = google.get('userinfo')
            user_info = resp.json()
            email = user_info.get('email')
            name = user_info.get('name', 'Google User')
            
        elif provider == 'apple':
            token = apple.authorize_access_token()
            user_info = {'email': 'placeholder-apple@apple.com', 'name': 'Apple User'} # Needs Apple ID decoding in production
            email = user_info.get('email')
            name = user_info.get('name')
            
        if not email:
            return jsonify({"error": "Failed to retrieve email from provider"}), 400
            
        if users_collection is not None:
            user = users_collection.find_one({"email": email})
            if not user:
                # Auto-register OAuth user
                result = users_collection.insert_one({"email": email, "first_name": name, "auth_provider": provider})
                session['user_id'] = str(result.inserted_id)
            else:
                session['user_id'] = str(user['_id'])
                
        return redirect('/homepage.html')
    except Exception as e:
        # Fallback Mock Logic for testing without real Client IDs
        print(f"OAuth Flow Failed (Likely Missing Credentials): {e}")
        # Insert a mock user to allow the user to see the dashboard anyway during testing
        if users_collection is not None:
            mock_email = f"mockuser_{provider}@example.com"
            user = users_collection.find_one({"email": mock_email})
            if not user:
                result = users_collection.insert_one({"email": mock_email, "first_name": f"Mock {provider.title()} User", "auth_provider": provider})
                session['user_id'] = str(result.inserted_id)
            else:
                session['user_id'] = str(user['_id'])
        return redirect('/homepage.html')

@app.route('/api/engineering_tasks', methods=['GET'])
def get_engineering_tasks():
    # Return tasks for part 1
    return jsonify({
        "tasks": list(ENGINEERING_TASKS.keys())
    })

@app.route('/api/profile_options', methods=['GET'])
def get_profile_options():
    # Merge engineering, medical and commerce options
    all_optional = list(set(OPTIONAL_COURSES + MEDICAL_OPTIONAL_COURSES + COMMERCE_OPTIONAL_COURSES))
    return jsonify({
        "skills": list(set(PREDEFINED_SKILLS + MEDICAL_PREDEFINED_SKILLS + COMMERCE_PREDEFINED_SKILLS)),
        "interests": list(set(PREDEFINED_INTERESTS + MEDICAL_PREDEFINED_INTERESTS + COMMERCE_PREDEFINED_INTERESTS)),
        "courses": all_optional
    })

@app.route('/api/v2/course_catalogue', methods=['GET'])
def get_course_catalogue_v2():
    return jsonify({
        "courses": COURSE_DATA,
        "colleges": KERALA_COLLEGES
    })

@app.route('/api/user_profile', methods=['GET', 'POST'])
def user_profile():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session['user_id']
    if users_collection is None:
        return jsonify({"error": "Database error"}), 503

    if request.method == 'GET':
        user = users_collection.find_one({"_id": ObjectId(user_id)}, {"_id": 0})
        if user:
            # Attach session-based recommendations for current test runs if available
            user['career_recommendation'] = session.get('career_recommendation')
            user['aptitude_recommendation'] = session.get('aptitude_recommendation')
            user['personality_result'] = session.get('personality_result')
            user['assessment_track'] = session.get('assessment_track', 'engineering')
            user['career_priority_list'] = session.get('career_priority_list', [])
            
            # Calculate Recommended Optional Courses
            skills_str = " ".join(user.get('skills', [])).lower()
            interests_str = " ".join(user.get('interests', [])).lower()
            recs = set()
            track = user.get('assessment_track', 'engineering')

            if track == 'commerce':
                if "accounting" in skills_str or "tax" in interests_str:
                    recs.add("Advanced Accounting Standards")
                if "stock" in interests_str or "investing" in interests_str:
                    recs.add("Stock Market Trading Basics")
                if "finance" in skills_str or "banking" in interests_str:
                    recs.add("Personal Finance 101")
                if "law" in skills_str or "corporate" in interests_str:
                    recs.add("Introduction to Business Law")
                if "management" in skills_str or "business" in interests_str:
                    recs.add("Principles of Marketing")
            else:
                if "python" in skills_str or "machine learning" in skills_str or "artificial intelligence" in interests_str:
                    recs.add("AI & Data Science Fundamentals")
                if "web" in skills_str or "java" in skills_str:
                    recs.add("Advanced Web Architecture")
                if "robotics" in skills_str or "cad" in skills_str or "automotive" in interests_str:
                    recs.add("Robotics & Automation")
                if "renewable" in interests_str:
                    recs.add("Sustainable Energy Systems")
                if "cybersecurity" in interests_str:
                    recs.add("Cybersecurity & Ethical Hacking")
                if "data" in skills_str or "financial" in interests_str:
                    recs.add("Financial Engineering")
                if "entrepreneurship" in interests_str or "public speaking" in skills_str:
                    recs.add("Digital Marketing & SEO")
                if "design" in skills_str or "art" in interests_str:
                    recs.add("UX/UI Design Principles")
                if "healthcare" in interests_str:
                    recs.add("Bioinformatics Fundamentals")
                
            user['recommended_optional_courses'] = list(recs)
            
            return jsonify(user), 200
        return jsonify({"error": "User not found"}), 404

    if request.method == 'POST':
        update_data = request.json
        # Only allow specific fields to be updated
        allowed_fields = ['first_name', 'last_name', 'phone', 'country_code', 'student_class', 'skills', 'interests', 'saved_courses']
        filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
        
        if not filtered_data:
            return jsonify({"error": "No valid fields to update"}), 400

        result = users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": filtered_data}
        )
        if result.modified_count > 0 or result.matched_count > 0:
            return jsonify({"message": "Profile updated successfully"}), 200
        return jsonify({"error": "Update failed"}), 500

@app.route('/api/recommend_stream', methods=['POST'])
def recommend_stream():
    data = request.json
    ratings = data.get('ratings', []) # List of integers 1-5
    
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
        
    return jsonify({
        "recommended_stream": top_recommendations[0]["course"],
        "confidence": top_recommendations[0]["confidence"],
        "top_recommendations": top_recommendations
    })

@app.route('/api/aptitude_questions', methods=['GET'])
def get_aptitude_questions():
    import random
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
                # Remove answer key
                q_copy = q.copy()
                q_copy['category'] = section
                all_selected_questions.append(q_copy)

    random.shuffle(all_selected_questions)
    # Storing answers map in session to grade later
    session['aptitude_questions'] = [{"id": q['id'], "category": q['category']} for q in all_selected_questions]
    return jsonify(all_selected_questions)

@app.route('/api/submit_aptitude', methods=['POST'])
def submit_aptitude():
    answers = request.json.get('answers', {}) # format: "category_id": "option"
    
    scores = {cat: 0 for cat in APTITUDE_MODEL_CATEGORIES}
    section_answered = {cat: 0 for cat in APTITUDE_MODEL_CATEGORIES}
    section_counts = {cat: 0 for cat in APTITUDE_MODEL_CATEGORIES}
    
    # Calculate scores based on session questions
    session_qs = session.get('aptitude_questions', [])
    for q in session_qs:
        cat = q['category']
        q_id = q['id']
        section_counts[cat] += 1
        
        ans_key = f"{cat}_{q_id}"
        if ans_key in answers:
            user_ans = str(answers[ans_key]).upper().strip()
            if user_ans: # Only count if not empty
                section_answered[cat] += 1
                correct_ans = str(DATA_PROCESSOR.CORRECT_ANSWERS[cat].get(q_id, "")).upper().strip()
                if user_ans == correct_ans:
                    scores[cat] += 1
                
    # Calculate performance ratio based on ANSWERED questions, not total questions
    # This prevents users from being penalized for unreached questions when finishing early.
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
    
    return jsonify(result)

@app.route('/api/personality_questions', methods=['GET'])
def get_personality_questions():
    formatted = []
    for q_id, data in QUESTIONNAIRE.items():
        formatted.append({
            "id": q_id,
            "text": data[1],
            "options": {"1":"Disagree Strongly", "2":"Disagree a little", "3":"Neither agree nor disagree", "4":"Agree a little", "5":"Agree Strongly"}
        })
    return jsonify(formatted)
    
@app.route('/api/submit_personality', methods=['POST'])
def submit_personality():
    answers = request.json.get('answers', {}) # id: 1-5
    
    trait_scores = {'O': 0, 'C': 0, 'E': 0, 'A': 0, 'N': 0}
    
    for q_id_str, val_str in answers.items():
        q_id = int(q_id_str)
        val = int(val_str)
        if q_id in QUESTIONNAIRE:
            trait, _, reverse = QUESTIONNAIRE[q_id]
            if reverse:
                score = 6 - val
            else:
                score = val
            trait_scores[trait] += score
            
    # Calculate percentages (max score per trait varies, but generally we can normalize)
    # O: 10 Qs (max 50), C: 9 Qs (max 45), E: 8 Qs (max 40), A: 9 Qs (max 45), N: 8 Qs (max 40)
    max_scores = {'O': 50, 'C': 45, 'E': 40, 'A': 45, 'N': 40}
    
    percentages = {t: (trait_scores[t] / max_scores[t]) * 100 for t in trait_scores}
    
    result = {
        "raw_scores": trait_scores,
        "percentages": percentages
    }
    session['personality_result'] = result
    
    return jsonify(result)

@app.route('/api/download_report', methods=['GET'])
def download_report():
    if 'user_id' not in session:
        return jsonify({"error": "No user session"}), 401
    
    if users_collection is None:
        return jsonify({"error": "Database error"}), 503
        
    user = users_collection.find_one({"_id": ObjectId(session['user_id'])}, {"_id": 0})
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    # Attach session-based recommendations for current test runs if available
    user['career_recommendation'] = session.get('career_recommendation')
    user['aptitude_recommendation'] = session.get('aptitude_recommendation')
    user['personality_result'] = session.get('personality_result')
    user['assessment_track'] = session.get('assessment_track', 'engineering')
    user['career_priority_list'] = session.get('career_priority_list', [])

    
    # Calculate Recommended Optional Courses
    skills_str = " ".join(user.get('skills', [])).lower()
    interests_str = " ".join(user.get('interests', [])).lower()
    recs = set()
    track = user.get('assessment_track', 'engineering')

    if track == 'commerce':
        if "accounting" in skills_str or "tax" in interests_str:
            recs.add("Advanced Accounting Standards")
        if "stock" in interests_str or "investing" in interests_str:
            recs.add("Stock Market Trading Basics")
        if "finance" in skills_str or "banking" in interests_str:
            recs.add("Personal Finance 101")
        if "law" in skills_str or "corporate" in interests_str:
            recs.add("Introduction to Business Law")
        if "management" in skills_str or "business" in interests_str:
            recs.add("Principles of Marketing")
    else:
        if "python" in skills_str or "machine learning" in skills_str or "artificial intelligence" in interests_str:
            recs.add("AI & Data Science Fundamentals")
        if "web" in skills_str or "java" in skills_str:
            recs.add("Advanced Web Architecture")
        if "robotics" in skills_str or "cad" in skills_str or "automotive" in interests_str:
            recs.add("Robotics & Automation")
        if "renewable" in interests_str:
            recs.add("Sustainable Energy Systems")
        if "cybersecurity" in interests_str:
            recs.add("Cybersecurity & Ethical Hacking")
        if "data" in skills_str or "financial" in interests_str:
            recs.add("Financial Engineering")
        if "entrepreneurship" in interests_str or "public speaking" in skills_str:
            recs.add("Digital Marketing & SEO")
        if "design" in skills_str or "art" in interests_str:
            recs.add("UX/UI Design Principles")
        if "healthcare" in interests_str:
            recs.add("Bioinformatics Fundamentals")
        
    user['recommended_optional_courses'] = list(recs)
    
    pdf_buffer = generate_assessment_report(user)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name='PathWise_Career_Report.pdf',
        mimetype='application/pdf'
    )

@app.route('/api/user_profile_data', methods=['GET'])
def get_user_profile_data():
    if 'user_id' not in session:
        return jsonify({"error": "No user session"}), 401
    
    interests = []
    skills = []
    
    if users_collection is not None:
        user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
        if user:
            interests = user.get('interests', [])
            skills = user.get('skills', [])
            
    return jsonify({
        "career_recommendation": session.get('career_recommendation'),
        "aptitude_recommendation": session.get('aptitude_recommendation'),
        "personality_result": session.get('personality_result'),
        "interests": interests,
        "skills": skills
    })

@app.route('/api/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({"error": "No user session"}), 401
        
    data = request.json
    interests = data.get('interests', [])
    skills = data.get('skills', [])
    
    if users_collection is not None:
        users_collection.update_one(
            {"_id": ObjectId(session['user_id'])},
            {"$set": {"interests": interests, "skills": skills}}
        )
        
    return jsonify({"message": "Profile updated successfully"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
