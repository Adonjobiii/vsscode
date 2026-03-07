import io
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

# Config and Data Imports
from gov_thinking_skills import plot_stream_skills as plot_gov_skills
from medical_thinking_skills import plot_stream_skills as plot_medical_skills

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_bar_chart(scores_dict, title):
    # Sort by value descending
    sorted_items = sorted(scores_dict.items(), key=lambda x: x[1], reverse=True)
    labels = [k.replace(' Engineering', '') for k, v in sorted_items]
    values = [v for k, v in sorted_items]
    
    fig, ax = plt.subplots(figsize=(6, 4))
    colors_list = plt.cm.viridis(np.linspace(0.2, 0.8, len(labels)))
    bars = ax.bar(labels, values, color=colors_list)
    
    ax.set_ylabel('Match Confidence (%)')
    ax.set_title(title, pad=15)
    ax.set_ylim(0, 100)
    plt.xticks(rotation=45, ha='right')
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)
                    
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf

def create_radar_chart(percentages, title):
    # Order: O, C, E, A, N
    trait_names = {'O': 'Openness', 'C': 'Conscientiousness', 'E': 'Extraversion', 'A': 'Agreeableness', 'N': 'Neuroticism'}
    labels = [trait_names.get(k, k) for k in ['O', 'C', 'E', 'A', 'N']]
    values = [percentages.get(k, 0) for k in ['O', 'C', 'E', 'A', 'N']]
    
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    
    # Complete the loop
    values += values[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.plot(angles, values, color='#9b59b6', linewidth=2)
    ax.fill(angles, values, color='#9b59b6', alpha=0.25)
    
    ax.set_title(title, y=1.1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], color="grey", size=8)
    ax.set_ylim(0, 100)
    
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf

def generate_assessment_report(user_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterTitle', alignment=1, fontSize=24, spaceAfter=20, textColor=colors.HexColor("#2C3E50"), fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name='SubHeading', fontSize=16, spaceAfter=10, textColor=colors.HexColor("#34495E"), fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name='NormalText', fontSize=12, spaceAfter=10, leading=16, textColor=colors.HexColor("#333333")))
    
    Story = []
    
    # Determine track
    track = user_data.get('assessment_track', 'engineering')
    is_medical = (track == 'medical')
    is_commerce = (track == 'commerce')
    is_law = (track == 'law')
    is_gov = (track == 'government & defence')

    # Header
    Story.append(Paragraph("PathWise Career Assessment Report", styles['CenterTitle']))
    Story.append(Paragraph(f"<b>Name:</b> {user_data.get('first_name', 'Student')} {user_data.get('last_name', '')}", styles['NormalText']))
    if 'email' in user_data:
        Story.append(Paragraph(f"<b>Email:</b> {user_data.get('email')}", styles['NormalText']))
    
    if is_medical: track_label = "Medical"
    elif is_commerce: track_label = "Banking & Finance"
    elif is_law: track_label = "Law & Legal Studies"
    elif is_gov: track_label = "Gov, Defence & PSU"
    else: track_label = "Engineering"
    
    Story.append(Paragraph(f"<b>Assessment Track:</b> {track_label}", styles['NormalText']))
    Story.append(Spacer(1, 20))
    
    # Part 1: Initial Interest/Career Match
    if is_medical:
        # For medical: use career_priority_list (selected streams)
        priority_list = user_data.get('career_priority_list', [])
        if priority_list:
            Story.append(Paragraph("1. Primary Medical Stream Match", styles['SubHeading']))
            top_match = priority_list[0]
            Story.append(Paragraph(f"<b>Top Interest:</b> {top_match}", styles['NormalText']))
            if len(priority_list) > 1:
                Story.append(Paragraph(f"<b>Other interests:</b> {', '.join(priority_list[1:])}", styles['NormalText']))
            desc = "Based on your selected medical stream preferences, this stream aligns best with your career aspirations and areas of interest."
            Story.append(Paragraph(desc, styles['NormalText']))
            Story.append(Spacer(1, 15))
    elif is_commerce:
        # Commerce: use career_recommendation or priority list
        career_rec = user_data.get('career_recommendation')
        if career_rec:
            Story.append(Paragraph("1. Primary Banking & Finance Match", styles['SubHeading']))
            Story.append(Paragraph(f"<b>Top Match:</b> {career_rec.get('course')}", styles['NormalText']))
            desc = "Your interest profile suggests a strong alignment with this area of commerce, reflecting your professional preferences."
            Story.append(Paragraph(desc, styles['NormalText']))
            Story.append(Spacer(1, 15))
    elif is_gov:
        priority_list = user_data.get('career_priority_list', [])
        if priority_list:
            Story.append(Paragraph("1. Primary Gov & Defence Match", styles['SubHeading']))
            top_match = priority_list[0]
            Story.append(Paragraph(f"<b>Top Interest:</b> {top_match}", styles['NormalText']))
            desc = "Your interest in public service and national security aligns perfectly with this specific area of government and defence."
            Story.append(Paragraph(desc, styles['NormalText']))
            Story.append(Spacer(1, 15))
    else:
        # Engineering: use ML career_recommendation
        career_rec = user_data.get('career_recommendation')
        if career_rec:
            Story.append(Paragraph("1. Primary Engineering Stream Match", styles['SubHeading']))
            confidence = career_rec.get('confidence', 0)
            Story.append(Paragraph(f"<b>Top Match:</b> {career_rec.get('course')} ({confidence:.1f}%)", styles['NormalText']))
            desc = "Based on your initial task preferences, this stream aligns best with the activities you find interesting and engaging."
            Story.append(Paragraph(desc, styles['NormalText']))
            Story.append(Spacer(1, 15))
        
    # Part 2: Aptitude Match
    aptitude_rec = user_data.get('aptitude_recommendation')
    if aptitude_rec:
        if is_medical: section_title = "2. Medical Aptitude Match"
        elif is_commerce: section_title = "2. Financial & Business Aptitude Match"
        elif is_law: section_title = "2. Legal Reasoning & Aptitude Match"
        elif is_gov: section_title = "2. Public Service & Strategic Aptitude Match"
        else: section_title = "2. Technical Aptitude Match"
        
        Story.append(Paragraph(section_title, styles['SubHeading']))
        confidence2 = aptitude_rec.get('confidence', 0)
        Story.append(Paragraph(f"<b>Top Aptitude Match:</b> {aptitude_rec.get('recommended_stream')} ({confidence2:.1f}%)", styles['NormalText']))
        
        if is_medical:
            desc = "This recommendation is based on your performance across biology, clinical, pharmaceutical, and anatomical problem-solving tasks."
        elif is_commerce:
            desc = "This recommendation reflects your performance across analytical, numerical, and business-logical evaluation tasks."
        elif is_law:
            desc = "This recommendation is based on your performance across critical thinking, legal reasoning, and analytical evaluation tasks."
        elif is_gov:
            desc = "This recommendation is based on your performance across strategic thinking, observation skills, and logic-based problem solving."
        else:
            desc = "This recommendation is based on your performance across algorithmic, logical, and computational problem-solving tasks."
        Story.append(Paragraph(desc, styles['NormalText']))
        
        scores = aptitude_rec.get('scores', {})
        if scores:
            data = [["Category", "Score"]]
            for k, v in scores.items():
                data.append([k, str(v)])
            t = Table(data, colWidths=[200, 150])
            
            header_color = colors.HexColor("#3498DB")
            if is_medical: header_color = colors.HexColor("#E74C3C")
            elif is_commerce: header_color = colors.HexColor("#2C3E50")
            elif is_law: header_color = colors.HexColor("#8E44AD")
            
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), header_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8F9FA")),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            Story.append(t)
            Story.append(Spacer(1, 15))
            
            # Add Aptitude Bar Chart
            probs = aptitude_rec.get('probabilities', {})
            if probs:
                if is_medical: chart_title = "Medical Stream Probabilities (Confidence %)"
                elif is_commerce: chart_title = "Banking & Finance Specializations (Confidence %)"
                elif is_law: chart_title = "Law Field Specializations (Confidence %)"
                else: chart_title = "Aptitude Probabilities (Confidence %)"
                
                chart_buf = create_bar_chart(probs, chart_title)
                chart_img = Image(chart_buf, width=400, height=266)
                Story.append(chart_img)
                Story.append(Spacer(1, 15))

        # --- Medical Thinking Skills section (Medical track only) ---
        if is_medical:
            thinking_skills = aptitude_rec.get('thinking_skills', {})
            dom_thinking = aptitude_rec.get('dominant_thinking_skill', '')
            rec_stream = aptitude_rec.get('recommended_stream', '')
            if thinking_skills:
                Story.append(Paragraph(
                    f"Thinking Skills Profile — {rec_stream}",
                    styles['SubHeading']
                ))
                Story.append(Paragraph(
                    f"Based on your recommended medical stream, the core cognitive skills you will need to develop are "
                    f"listed below. Your dominant thinking skill for this stream is <b>{dom_thinking}</b>.",
                    styles['NormalText']
                ))

                # Thinking skills table
                ts_data = [["Thinking Skill", "Required Weight (%)"]]
                for skill, pct in thinking_skills.items():
                    ts_data.append([skill, f"{pct}%"])

                ts_table = Table(ts_data, colWidths=[230, 130])
                ts_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#8E44AD")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8F9FA")),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F0ECF7")]),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#D5D5D5"))
                ]))
                Story.append(ts_table)
                Story.append(Spacer(1, 15))

                # Thinking skills bar chart
                chart_buf = plot_medical_skills(rec_stream)
                if chart_buf:
                    chart_img = Image(chart_buf, width=430, height=246)
                    Story.append(chart_img)
                    Story.append(Spacer(1, 15))

        # --- Gov Thinking Skills section ---
        if is_gov:
            thinking_skills = aptitude_rec.get('thinking_skills', {})
            dom_thinking = aptitude_rec.get('dominant_thinking_skill', '')
            rec_stream = aptitude_rec.get('recommended_stream', '')
            if thinking_skills:
                Story.append(Paragraph(f"Thinking Skills Profile — {rec_stream}", styles['SubHeading']))
                Story.append(Paragraph(
                    f"Based on your recommended government/defence stream, the core cognitive skills you will need to develop are "
                    f"listed below. Your dominant thinking skill for this stream is <b>{dom_thinking}</b>.",
                    styles['NormalText']
                ))

                ts_data = [["Thinking Skill", "Required Weight (%)"]]
                for skill, pct in thinking_skills.items():
                    ts_data.append([skill, f"{pct}%"])

                ts_table = Table(ts_data, colWidths=[230, 130])
                ts_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E67E22")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8F9FA")),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#D5D5D5"))
                ]))
                Story.append(ts_table)
                Story.append(Spacer(1, 15))

                # Thinking skills bar chart
                chart_buf = plot_gov_skills(rec_stream)
                if chart_buf:
                    chart_img = Image(chart_buf, width=430, height=246)
                    Story.append(chart_img)
                    Story.append(Spacer(1, 15))

        # --- Law Thinking Skills section ---
        if is_law:
            thinking_skills = aptitude_rec.get('thinking_skills', {})
            dom_thinking = aptitude_rec.get('dominant_thinking_skill', '')
            rec_stream = aptitude_rec.get('recommended_stream', '')
            if thinking_skills:
                Story.append(Paragraph(f"Thinking Skills Profile — {rec_stream}", styles['SubHeading']))
                Story.append(Paragraph(
                    f"Based on your recommended law stream, the core cognitive skills you will need to develop are "
                    f"listed below. Your dominant thinking skill for this stream is <b>{dom_thinking}</b>.",
                    styles['NormalText']
                ))

                ts_data = [["Thinking Skill", "Required Weight (%)"]]
                for skill, pct in thinking_skills.items():
                    ts_data.append([skill, f"{pct}%"])

                ts_table = Table(ts_data, colWidths=[230, 130])
                ts_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2980B9")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8F9FA")),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#D5D5D5"))
                ]))
                Story.append(ts_table)
                Story.append(Spacer(1, 15))


    personality_res = user_data.get('personality_result')
    if personality_res:
        Story.append(Paragraph("3. Big Five Personality Analysis", styles['SubHeading']))
        Story.append(Paragraph(
            "Your personality traits have been evaluated using the Big Five (OCEAN) model. "
            "Below are your scores and what they mean for your chosen career path.",
            styles['NormalText']
        ))
        percentages = personality_res.get('percentages', {})
        if percentages:
            # --- Score Table ---
            data = [["Trait", "Score (%)"]]
            trait_names = {'O': 'Openness', 'C': 'Conscientiousness', 'E': 'Extraversion', 'A': 'Agreeableness', 'N': 'Neuroticism'}
            for k, v in percentages.items():
                data.append([trait_names.get(k, k), f"{v:.1f}%"])
            t = Table(data, colWidths=[200, 150])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2ECC71")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8F9FA")),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            Story.append(t)
            Story.append(Spacer(1, 15))

            # --- Track-specific trait explanations ---
            TRAIT_EXPLANATIONS = {
                'engineering': {
                    'O': (
                        "Openness to Experience",
                        "A high Openness score indicates you enjoy exploring new ideas and technologies — a great trait "
                        "for engineers who must adapt to rapidly changing tools, frameworks, and problem domains. "
                        "You are likely drawn to research, innovation, and creative problem-solving."
                    ),
                    'C': (
                        "Conscientiousness",
                        "Conscientiousness reflects your discipline, attention to detail, and goal orientation. "
                        "In engineering, this translates to writing clean code, following design specifications meticulously, "
                        "and delivering projects on time. High scorers make excellent systems architects and project leads."
                    ),
                    'E': (
                        "Extraversion",
                        "Extraversion reflects how energized you are by social interactions and collaborative environments. "
                        "Engineers with high Extraversion thrive in team-based Agile workflows, client-facing roles, "
                        "and leadership positions such as tech lead or product manager."
                    ),
                    'A': (
                        "Agreeableness",
                        "Agreeableness measures your cooperation, empathy, and team-orientation. "
                        "In engineering teams, highly agreeable individuals act as effective collaborators and mediators, "
                        "helping to maintain healthy team dynamics and smooth cross-functional communication."
                    ),
                    'N': (
                        "Neuroticism (Emotional Stability)",
                        "A lower Neuroticism score indicates higher emotional stability — a key advantage in high-pressure "
                        "engineering environments with tight deadlines and production incidents. "
                        "Emotionally stable engineers handle debugging, outages, and client escalations more calmly."
                    ),
                },
                'medical': {
                    'O': (
                        "Openness to Experience",
                        "In medicine, high Openness correlates with a desire for continuous learning — essential given "
                        "how rapidly medical knowledge evolves. Doctors and researchers with this trait are more likely "
                        "to adopt evidence-based innovations, explore new treatment modalities, and pursue specialization."
                    ),
                    'C': (
                        "Conscientiousness",
                        "Conscientiousness is one of the most critical traits for medical professionals. "
                        "It reflects your commitment to precision, thoroughness, and adherence to protocols — "
                        "all vital in clinical settings where errors can have life-altering consequences. "
                        "High scorers excel in surgery, pharmacology, and diagnostic roles."
                    ),
                    'E': (
                        "Extraversion",
                        "Extraversion in medical contexts relates to your comfort in patient interactions and team-based care. "
                        "Physicians, nurses, and healthcare communicators with high Extraversion build stronger patient rapport, "
                        "perform better in emergency medicine, and thrive in multi-disciplinary care teams."
                    ),
                    'A': (
                        "Agreeableness",
                        "Agreeableness is strongly linked to patient-centred care. High scorers demonstrate empathy, "
                        "compassion, and respect for patient autonomy — core values in nursing, general medicine, "
                        "and palliative care. This trait supports effective doctor-patient communication and ethical decision-making."
                    ),
                    'N': (
                        "Neuroticism (Emotional Stability)",
                        "Medical professionals regularly encounter high-stress situations including emergencies, grief, "
                        "and ethical dilemmas. Lower Neuroticism (higher emotional stability) enables you to remain composed, "
                        "make clear decisions under pressure, and provide consistent care — critical qualities in surgery, "
                        "intensive care, and emergency medicine."
                    ),
                },
                'commerce': {
                    'O': (
                        "Openness to Experience",
                        "In commerce and finance, high Openness translates to adaptability in a dynamic global market. "
                        "It reflects a willingness to embrace new financial technologies (FinTech), innovative business "
                        "strategies, and diverse economic perspectives. High scorers excel in entrepreneurship and investment strategy."
                    ),
                    'C': (
                        "Conscientiousness",
                        "Conscientiousness is paramount for commerce professionals, especially in auditing, accounting, "
                        "and financial planning. It reflects your attention to detail, organizational skills, and "
                        "ethical standards. High scorers are reliable in managing portfolios and ensuring regulatory compliance."
                    ),
                    'E': (
                        "Extraversion",
                        "Extraversion is a key asset in business management, sales, and client relations. "
                        "It reflects your ability to network, lead teams, and present financial insights with confidence. "
                        "High scorers thrive in collaborative corporate environments and negotiation roles."
                    ),
                    'A': (
                        "Agreeableness",
                        "In a business context, Agreeableness facilitates effective teamwork and customer service. "
                        "It reflects your trustworthiness and cooperative nature, which are essential for building "
                        "long-term client relationships and maintaining a positive organizational culture."
                    ),
                    'N': (
                        "Neuroticism (Emotional Stability)",
                        "Financial markets and corporate management can be volatile and high-pressure. "
                        "Lower Neuroticism (higher stability) allows you to make objective decisions during market "
                        "fluctuations and handle professional setbacks without compromising your strategic focus."
                    ),
                },
                'law': {
                    'O': (
                        "Openness to Experience",
                        "In law, Openness indicates a receptivity to complex legal theories and diverse societal perspectives. "
                        "It is vital for legal research, constitutional interpretation, and adapting to legislative changes. "
                        "High scorers excel in academia, policy-making, and specialized legal advocacy."
                    ),
                    'C': (
                        "Conscientiousness",
                        "Conscientiousness is the hallmark of a successful lawyer. It reflects the meticulous attention "
                        "to detail required for contract drafting, case preparation, and procedural compliance. "
                        "High scorers are dependable, organized, and thorough in their legal investigations."
                    ),
                    'E': (
                        "Extraversion",
                        "Extraversion is key for litigation, negotiation, and client relationship management. "
                        "It reflects your ability to argue persuasively in court, network within the legal community, "
                        "and lead legal teams. High scorers thrive in courtroom advocacy and corporate law firms."
                    ),
                    'A': (
                        "Agreeableness",
                        "In a legal context, Agreeableness facilitates effective mediation, client empathy, and "
                        "cooperative negotiation. While lawyers must be firm, those with high Agreeableness bridge "
                        "opposing views and maintain professionalism in adversarial settings."
                    ),
                    'N': (
                        "Neuroticism (Emotional Stability)",
                        "The legal profession is inherently high-pressure, with demanding clients and high-stakes cases. "
                        "Lower Neuroticism (higher stability) enables you to maintain composure in court, handle "
                        "adverse judgments objectively, and manage professional stress effectively."
                    ),
                },
                'government & defence': {
                    'O': (
                        "Openness to Experience",
                        "In government and defence, high Openness correlates with adaptability to evolving "
                        "geopolitical landscapes and security technologies. It indicates a readiness to embrace "
                        "tactical innovations and strategic shifts essential for national safety."
                    ),
                    'C': (
                        "Conscientiousness",
                        "Conscientiousness is non-negotiable in defence and PSU roles. It reflects the discipline, "
                        "integrity, and strict adherence to protocols required in high-stakes environments. "
                        "High scorers excel in tactical operations, engineering, and administrative leadership."
                    ),
                    'E': (
                        "Extraversion",
                        "Extraversion is a vital asset for field leadership and multi-unit collaboration. "
                        "It reflects your ability to command respect, communicate clearly under pressure, "
                        "and coordinate effectively across diverse government departments."
                    ),
                    'A': (
                        "Agreeableness",
                        "In public service, Agreeableness supports team cohesion and community-oriented missions. "
                        "It reflects your commitment to the common good and your ability to work harmoniously "
                        "within large hierarchies to achieve shared national objectives."
                    ),
                    'N': (
                        "Neuroticism (Emotional Stability)",
                        "Defence and government roles often involve high-stress environments and life-critical decisions. "
                        "Lower Neuroticism (higher stability) is essential for remaining calm under tactical pressure, "
                        "managing crisis situations, and maintaining objective moral judgment."
                    ),
                }
            }

            explanations = TRAIT_EXPLANATIONS.get(track, TRAIT_EXPLANATIONS['engineering'])
            styles.add(ParagraphStyle(name='TraitTitle', fontSize=11, spaceAfter=2, textColor=colors.HexColor("#2ECC71"), fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='TraitBody', fontSize=10, spaceAfter=10, leading=14, textColor=colors.HexColor("#444444")))

            Story.append(Paragraph("Trait Insights for Your Career Path:", styles['SubHeading']))
            for trait_key in ['O', 'C', 'E', 'A', 'N']:
                score = percentages.get(trait_key, 0)
                if trait_key in explanations:
                    title, body = explanations[trait_key]
                    Story.append(Paragraph(f"{title}  —  Score: {score:.1f}%", styles['TraitTitle']))
                    Story.append(Paragraph(body, styles['TraitBody']))

            Story.append(Spacer(1, 10))

            # Add Personality Radar Chart
            chart_buf = create_radar_chart(percentages, "Big Five Personality Traits (%)")
            chart_img = Image(chart_buf, width=300, height=300)
            Story.append(chart_img)
            Story.append(Spacer(1, 15))

        
    # Optional Courses Recommended
    optional_courses = user_data.get('recommended_optional_courses', [])
    if optional_courses:
        Story.append(Paragraph("4. Recommended Optional Courses", styles['SubHeading']))
        Story.append(Paragraph("Based on your interests and skills, the following upskilling courses are highly recommended:", styles['NormalText']))
        for c in optional_courses:
            Story.append(Paragraph(f"• {c}", styles['NormalText']))
            
    doc.build(Story)
    buffer.seek(0)
    return buffer
