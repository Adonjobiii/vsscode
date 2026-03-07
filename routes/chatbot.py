from flask import Blueprint, request, jsonify, session
import random

chatbot_bp = Blueprint('chatbot', __name__)

# KNOWLEDGE BASE: NIRF 2024 & Career Development
KNOWLEDGE_BASE = {
    "colleges": {
        "engineering": [
            {"name": "IIT Madras", "url": "https://www.iitm.ac.in", "rank": 1},
            {"name": "IIT Delhi", "url": "https://home.iitd.ac.in", "rank": 2},
            {"name": "IIT Bombay", "url": "https://www.iitb.ac.in", "rank": 3},
            {"name": "IIT Kanpur", "url": "https://www.iitk.ac.in", "rank": 4},
            {"name": "IIT Kharagpur", "url": "https://www.iitkgp.ac.in", "rank": 5},
            {"name": "IIT Roorkee", "url": "https://www.iitr.ac.in", "rank": 6},
            {"name": "IIT Guwahati", "url": "https://www.iitg.ac.in", "rank": 7},
            {"name": "IIT Hyderabad", "url": "https://www.iith.ac.in", "rank": 8},
            {"name": "NIT Tiruchirappalli", "url": "https://www.nitt.edu", "rank": 9},
            {"name": "IIT (BHU) Varanasi", "url": "https://www.iitbhu.ac.in", "rank": 10}
        ],
        "medical": [
            {"name": "AIIMS New Delhi", "url": "https://www.aiims.edu", "rank": 1},
            {"name": "PGIMER Chandigarh", "url": "https://pgimer.edu.in", "rank": 2},
            {"name": "CMC Vellore", "url": "https://www.cmcvellore.ac.in", "rank": 3},
            {"name": "NIMHANS Bengaluru", "url": "https://nimhans.ac.in", "rank": 4},
            {"name": "BHU Varanasi", "url": "https://www.bhu.ac.in", "rank": 5},
            {"name": "JIPMER Puducherry", "url": "https://jipmer.edu.in", "rank": 6},
            {"name": "SGPGI Lucknow", "url": "https://www.sgpgi.ac.in", "rank": 7},
            {"name": "Amrita Vishwa Vidyapeetham", "url": "https://www.amrita.edu", "rank": 8},
            {"name": "SCTIMST Thiruvananthapuram", "url": "https://www.sctimst.ac.in", "rank": 9},
            {"name": "Madras Medical College", "url": "http://www.mmc.ac.in", "rank": 10}
        ],
        "commerce": [
            {"name": "SRCC New Delhi", "url": "https://www.srcc.edu", "rank": 1},
            {"name": "Hindu College New Delhi", "url": "https://hinducollege.ac.in", "rank": 2},
            {"name": "Hansraj College New Delhi", "url": "https://www.hansrajcollege.ac.in", "rank": 3},
            {"name": "St. Xavier's College Mumbai", "url": "https://www.xaviers.edu", "rank": 4},
            {"name": "Christ University Bangalore", "url": "https://www.christuniversity.in", "rank": 5}
        ],
        "law": [
            {"name": "NLSIU Bengaluru", "url": "https://www.nls.ac.in", "rank": 1},
            {"name": "NLU Delhi", "url": "https://nludelhi.ac.in", "rank": 2},
            {"name": "NALSAR Hyderabad", "url": "https://www.nalsar.ac.in", "rank": 3},
            {"name": "WBNUJS Kolkata", "url": "https://www.nujs.edu", "rank": 4},
            {"name": "SLS Pune", "url": "https://www.symbiosislawpune.org", "rank": 5}
        ],
        "defence": [
            {"name": "National Defence Academy (NDA)", "url": "https://nda.nic.in", "rank": 1},
            {"name": "Indian Military Academy (IMA)", "url": "https://indianarmy.nic.in", "rank": 2},
            {"name": "Indian Naval Academy (INA)", "url": "https://www.joinindiannavy.gov.in", "rank": 3},
            {"name": "Air Force Academy (AFA)", "url": "https://afacat.cdac.in", "rank": 4},
            {"name": "Officers Training Academy (OTA)", "url": "https://indianarmy.nic.in", "rank": 5}
        ]
    },
    "faqs": [
        {
            "q": "What are the trending careers in India?",
            "a": "Currently, Data Science, AI/ML Engineering, Cybersecurity, Digital Marketing, and Healthcare Management are seeing massive growth in India."
        },
        {
            "q": "How do I choose between Engineering and Medical?",
            "a": "It depends on your interests! If you love solving logical problems and building things, Engineering might be better. If you are passionate about helping people and have a strong interest in biology, Medical is a great path. Take our assessment to find out!"
        },
        {
            "q": "Which are the best colleges in Kerala?",
            "a": "Our system includes detailed Kerala rankings! For Engineering, NIT Calicut is top; for Medical, Govt Medical College Trivandrum leads; and for Commerce, St. Joseph's Devagiri is highly ranked. For Law, Govt Law College Ernakulam is a premier choice."
        },
        {
            "q": "How to join the Indian Army?",
            "a": "You can join the Indian Army through exams like NDA (after Class 12), CDS (after Graduation), or specialized entries like TGC and SSC Tech. Preparation for the SSB Interview is crucial!"
        }
    ],
    "tips": [
        "Focus on building projects alongside your degree.",
        "Networking on LinkedIn can open many career doors.",
        "Consider doing internships in your second and third years.",
        "Always keep learning new skills outside your curriculum."
    ]
}

@chatbot_bp.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').lower()
    
    # Store message in session history
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    session['chat_history'].append({"user": user_message})
    
    response = ""
    
    # Simple logic-based response engine
    if "college" in user_message or "ranking" in user_message:
        if "engineering" in user_message:
            colleges = KNOWLEDGE_BASE["colleges"]["engineering"]
            response = "Here are the top 5 Engineering colleges in India (NIRF 2024):<br>" + "<br>".join([f"{c['rank']}. {c['name']} - <a href='{c['url']}' target='_blank'>Website</a>" for c in colleges[:5]])
        elif "medical" in user_message:
            colleges = KNOWLEDGE_BASE["colleges"]["medical"]
            response = "Here are the top 5 Medical colleges in India (NIRF 2024):<br>" + "<br>".join([f"{c['rank']}. {c['name']} - <a href='{c['url']}' target='_blank'>Website</a>" for c in colleges[:5]])
        elif "commerce" in user_message:
            colleges = KNOWLEDGE_BASE["colleges"]["commerce"]
            response = "Here are the top 5 Commerce colleges in India (2024):<br>" + "<br>".join([f"{c['rank']}. {c['name']} - <a href='{c['url']}' target='_blank'>Website</a>" for c in colleges[:5]])
        elif "law" in user_message:
            colleges = KNOWLEDGE_BASE["colleges"]["law"]
            response = "Here are the top 5 Law colleges in India (NIRF 2024):<br>" + "<br>".join([f"{c['rank']}. {c['name']} - <a href='{c['url']}' target='_blank'>Website</a>" for c in colleges[:5]])
        elif "defence" in user_message or "army" in user_message:
            colleges = KNOWLEDGE_BASE["colleges"]["defence"]
            response = "Here are the premier Defence Training Academies in India:<br>" + "<br>".join([f"{c['rank']}. {c['name']} - <a href='{c['url']}' target='_blank'>Website</a>" for c in colleges[:5]])
        else:
            response = "I can tell you about the best Engineering, Medical, Commerce, Law, or Defence colleges. Which path are you interested in?"
            
    elif "career" in user_message or "prediction" in user_message or "suggest" in user_message:
        # Check if user has an assessment result in session
        rec = session.get('career_recommendation') or session.get('aptitude_recommendation')
        if rec and isinstance(rec, dict):
            stream = rec.get('recommended_stream') or rec.get('course')
            response = f"Based on your profile, your recommended path is {stream}. You should focus on building skills in this area!"
        else:
            response = "To give you an accurate prediction, please take our Engineering, Medical, or Commerce assessment first! I can then guide you further."
            
    elif "tip" in user_message or "development" in user_message:
        tip = random.choice(KNOWLEDGE_BASE["tips"])
        response = f"Career Development Tip: {tip}"
        
    elif "hi" in user_message or "hello" in user_message:
        response = "Hello! I am PathWise Assistance, your career navigator. How can I help you today? You can ask about top colleges, career tips, or your prediction results."
        
    else:
        # Check FAQs
        for faq in KNOWLEDGE_BASE["faqs"]:
            if any(word in user_message for word in faq['q'].lower().split()):
                response = faq['a']
                break
        
        if not response:
            response = "I'm not sure I understand. Try asking about 'top engineering colleges', 'career tips', or 'my assessment results'."

    try:
        session['chat_history'].append({"ai": response})
        session.modified = True
    except Exception:
        # Prevent crash if session is full/locked
        pass
    
    return jsonify({"response": response})

@chatbot_bp.route('/api/chat/faq', methods=['GET'])
def get_faq():
    return jsonify(KNOWLEDGE_BASE["faqs"])
