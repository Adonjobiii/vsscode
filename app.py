import os
import pymongo
import numpy as np
from flask import Flask, request, jsonify, render_template, session, send_file, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from authlib.integrations.flask_client import OAuth
from datetime import datetime

from pdf_generator import generate_assessment_report

# Import blueprints
from routes.engineering import engineering_bp
from routes.medical import medical_bp
from routes.commerce import commerce_bp
from routes.chatbot import chatbot_bp
from routes.law import law_bp
from routes.gov import gov_bp

# Config and Data Imports
from config_data import *
from course_data import *
from gov_config import GOV_PREDEFINED_SKILLS, GOV_PREDEFINED_INTERESTS, GOV_OPTIONAL_COURSES
from ml_logic import DataProcessor, MLModelTrainer

app = Flask(__name__)
app.secret_key = "career_assessment_secret_key" # Needed for session management

# OAuth Configuration
oauth = OAuth(app)

# Register Blueprints
app.register_blueprint(engineering_bp)
app.register_blueprint(medical_bp)
app.register_blueprint(commerce_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(law_bp)
app.register_blueprint(gov_bp)

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



# MongoDB Setup is now handled in config_data.py
# users_collection is imported via 'from config_data import *'

# Global ML Initialization
DATA_PROCESSOR = DataProcessor()
ML_MODELS = MLModelTrainer()

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
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    return render_template('homepage.html')

@app.route('/homepage')
def homepage_redirect():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    return redirect('/homepage.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/assesment.html')
def assessment():
    return render_template('assesment.html')

@app.route('/personality.html')
def personality():
    return render_template('personality.html')





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

    data = request.json or {}
    try:
        # Check if basic fields exist
        first_name = data.get('first_name')
        email = data.get('email')
        password = data.get('password')
        
        if not first_name or not email or not password:
            return jsonify({"error": "Fields missing. Profile requires Name, Email, and Password."}), 400
            
        # Check if email is unique
        if users_collection.find_one({"email": email}):
            return jsonify({"error": "An account with this email already exists."}), 400
            
        # Hash password
        hashed_pw = generate_password_hash(password)
        data['password'] = hashed_pw

        result = users_collection.insert_one(data)
        session['user_id'] = str(result.inserted_id)
        session.permanent = True
        
        return jsonify({"message": "User registered", "id": str(result.inserted_id)})
    except Exception as e:
        print(f"Signup Error: {e}")
        return jsonify({"error": "Server error during registration. Please try again."}), 500

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
    print(f"\n[AUTH] Login requested for provider: {provider}")
    is_mock = True
    
    # Only attempt real OAuth if we have a real-looking Client ID and NOT on localhost
    if not (request.host.startswith('127.0.0.1') or request.host.startswith('localhost')):
        client_id = os.environ.get(f'{provider.upper()}_CLIENT_ID')
        if client_id and 'placeholder' not in client_id.lower():
            is_mock = False
            print(f"[AUTH] Valid Client ID found. Attempting REAL OAuth flow.")

    if is_mock:
        print(f"[AUTH] Proceeding with Mock {provider} login (BYPASS).")
        # Direct bypass: perform mock login and redirect to homepage
        email = f"{provider}-test@example.com"
        name = f"Mock {provider.capitalize()} User"
        
        if users_collection is not None:
            user = users_collection.find_one({"email": email})
            if not user:
                result = users_collection.insert_one({"email": email, "first_name": name, "auth_provider": provider})
                session['user_id'] = str(result.inserted_id)
            else:
                session['user_id'] = str(user['_id'])
        
        session.permanent = True
        return redirect('/homepage.html')

    # Real OAuth Flow
    if provider == 'google':
        redirect_uri = url_for('oauth_authorize', provider=provider, _external=True)
        return google.authorize_redirect(redirect_uri)
    elif provider == 'apple':
        redirect_uri = url_for('oauth_authorize', provider=provider, _external=True)
        return apple.authorize_redirect(redirect_uri)
    
    return jsonify({"error": "Unsupported provider"}), 400

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    try:
        # Check if we are in mock/bypass mode via query param OR missing env vars OR just as a fallback
        is_mock = request.args.get('mock') == 'true'
        if not is_mock:
            client_id = os.environ.get(f'{provider.upper()}_CLIENT_ID')
            if not client_id or 'placeholder' in client_id.lower():
                is_mock = True
        
        if is_mock:
            print(f"[AUTH] Mock Authorization triggered for {provider}.")
            email = f"{provider}-test@example.com"
            name = f"Mock {provider.capitalize()} User"
        else:
            try:
                if provider == 'google':
                    token = google.authorize_access_token()
                    resp = google.get('userinfo')
                    user_info = resp.json()
                    email = user_info.get('email')
                    name = user_info.get('name', 'Google User')
                elif provider == 'apple':
                    token = apple.authorize_access_token()
                    user_info = {'email': 'apple-user@example.com', 'name': 'Apple User'}
                    email = user_info.get('email')
                    name = user_info.get('name')
            except Exception as oauth_err:
                print(f"[AUTH] Real OAuth failed: {oauth_err}. Falling back to Mock.")
                email = f"{provider}-test@example.com"
                name = f"Mock {provider.capitalize()} User"

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
        print(f"OAuth Flow Failed: {e}")
        return jsonify({"error": f"Authentication failed: {str(e)}"}), 500

@app.route('/api/engineering_tasks', methods=['GET'])
def get_engineering_tasks():
    # Return tasks for part 1
    return jsonify({
        "tasks": list(ENGINEERING_TASKS.keys())
    })

@app.route('/api/profile_options', methods=['GET'])
def get_profile_options():
    # Merge engineering, medical, commerce, law and gov options
    all_optional = list(set(OPTIONAL_COURSES + MEDICAL_OPTIONAL_COURSES + COMMERCE_OPTIONAL_COURSES + LAW_OPTIONAL_COURSES + GOV_OPTIONAL_COURSES))
    return jsonify({
        "skills": list(set(PREDEFINED_SKILLS + MEDICAL_PREDEFINED_SKILLS + COMMERCE_PREDEFINED_SKILLS + LAW_PREDEFINED_SKILLS + GOV_PREDEFINED_SKILLS)),
        "interests": list(set(PREDEFINED_INTERESTS + MEDICAL_PREDEFINED_INTERESTS + COMMERCE_PREDEFINED_INTERESTS + LAW_PREDEFINED_INTERESTS + GOV_PREDEFINED_INTERESTS)),
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
            elif track == 'law':
                if "research" in skills_str or "documentation" in interests_str:
                    recs.add("Legal Drafting & Conveyancing")
                if "constitution" in interests_str or "rights" in skills_str:
                    recs.add("Constitutional Law Basics")
                if "criminal" in interests_str or "police" in interests_str:
                    recs.add("Introduction to Criminal Law")
                if "corporate" in skills_str or "business" in interests_str:
                    recs.add("Corporate Governance & Compliance")
                if "mediation" in skills_str or "negotiation" in interests_str:
                    recs.add("Mediation & Arbitration Skills")
            elif track == 'government & defence':
                if "governance" in interests_str or "administration" in skills_str:
                    recs.add("Ethics & Integrity in Governance")
                if "defence" in interests_str or "army" in skills_str or "security" in interests_str:
                    recs.add("Advanced SSB Preparation")
                if "disaster" in interests_str or "management" in skills_str:
                    recs.add("Disaster Management")
                if "intelligence" in interests_str or "situational" in skills_str:
                    recs.add("Intelligence & Espionage Basics")
                if "policy" in interests_str or "analysis" in skills_str:
                    recs.add("Public Policy Analysis")
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
    
    user_id = session.get('user_id')
    if user_id and assessment_history is not None:
        try:
            # Find dominant trait
            top_trait = max(percentages, key=percentages.get)
            assessment_history.insert_one({
                "user_id": ObjectId(user_id),
                "type": "personality",
                "recommended_stream": f"Dominant: {top_trait}",
                "confidence": round(percentages[top_trait], 1),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Completed"
            })
        except Exception as e:
            print(f"Error saving personality assessment: {e}")

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
    elif track == 'law':
        if "research" in skills_str or "documentation" in interests_str:
            recs.add("Legal Drafting & Conveyancing")
        if "constitution" in interests_str or "rights" in skills_str:
            recs.add("Constitutional Law Basics")
        if "criminal" in interests_str or "police" in interests_str:
            recs.add("Introduction to Criminal Law")
        if "corporate" in skills_str or "business" in interests_str:
            recs.add("Corporate Governance & Compliance")
        if "mediation" in skills_str or "negotiation" in interests_str:
            recs.add("Mediation & Arbitration Skills")
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

@app.route('/api/ping')
def ping():
    return jsonify({"status": "ok", "version": "v3-diagnostic"}), 200

@app.route('/api/assessment_history', methods=['GET'])
def get_assessment_history():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    if assessment_history is None:
        return jsonify([])

    try:
        # Validate user_id represents a valid ObjectId (24 hex chars)
        if len(user_id) != 24 or not all(c in '0123456789abcdefABCDEF' for c in user_id):
             return jsonify([]) # Return empty if it's a mock/invalid string
             
        cursor = assessment_history.find({"user_id": ObjectId(user_id)}).sort("timestamp", -1)
        history = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            doc['user_id'] = str(doc['user_id'])
            history.append(doc)
        return jsonify(history)
    except Exception as e:
        print(f"Error fetching history: {e}")
        return jsonify({"error": str(e)}), 500

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
    port = int(os.environ.get('PORT', 5001))
    try:
        # Disable reloader to prevent 'select.select' issues on Windows
        print(f" * Starting PathWise on http://0.0.0.0:{port}")
        app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
    except Exception as e:
        print(f"Error starting server: {e}")
