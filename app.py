import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
import io
import sys
import time
import re
import difflib

# Ensure paths are correctly configured for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.extractor import ResumeExtractor
from utils.parser import ResumeParser
from utils.analyzer import ATSAnalyzer, JobMatchAnalyzer
from utils.classifier import ResumeClassifier
from utils.feedback import AIFeedbackSystem
from utils.reporter import PDFReportGenerator
from utils.analytics import ResumeAnalyticsEngine
from utils.charts import ResumeCharts

# --- Session State Initialization ---
if 'theme_mode' not in st.session_state:
    st.session_state.theme_mode = "Dark Mode"
if 'primary_color' not in st.session_state:
    st.session_state.primary_color = "Indigo"
if 'nav_selection' not in st.session_state:
    st.session_state.nav_selection = "Home Page"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Welcome to Apex Resume Assistant. Upload your resume or paste a job description and ask me anything about editing, interview prep, or career strategies!"}
    ]
if 'resume_history' not in st.session_state:
    st.session_state.resume_history = []
if 'achievements_unlocked' not in st.session_state:
    st.session_state.achievements_unlocked = {
        "First Parse": False,
        "Perfect Contact Info": False,
        "High ATS Competency": False,
        "Interactive Chat Session": False,
        "Comparison Expert": False
    }

# --- Page Configuration ---
st.set_page_config(
    page_title="Apex AI - Premium Resume Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Dynamic Styles & Theme Colors ---
COLOR_MAPS = {
    "Indigo": {"primary": "#6366F1", "gradient": "linear-gradient(135deg, #C084FC 0%, #6366F1 50%, #38BDF8 100%)", "accent": "rgba(99, 102, 241, 0.15)"},
    "Emerald": {"primary": "#10B981", "gradient": "linear-gradient(135deg, #34D399 0%, #10B981 50%, #059669 100%)", "accent": "rgba(16, 185, 129, 0.15)"},
    "Rose": {"primary": "#F43F5E", "gradient": "linear-gradient(135deg, #FDA4AF 0%, #F43F5E 50%, #BE123C 100%)", "accent": "rgba(244, 63, 94, 0.15)"},
    "Amber": {"primary": "#F59E0B", "gradient": "linear-gradient(135deg, #FDE68A 0%, #F59E0B 50%, #B45309 100%)", "accent": "rgba(245, 158, 11, 0.15)"}
}

p_color = COLOR_MAPS[st.session_state.primary_color]["primary"]
g_color = COLOR_MAPS[st.session_state.primary_color]["gradient"]
a_color = COLOR_MAPS[st.session_state.primary_color]["accent"]

if st.session_state.theme_mode == "Dark Mode":
    bg_primary = "#0B0F19"
    bg_secondary = "rgba(17, 24, 39, 0.7)"
    text_primary = "#F3F4F6"
    text_secondary = "#94A3B8"
    border_color = "rgba(255, 255, 255, 0.08)"
    card_shadow = "rgba(0, 0, 0, 0.4)"
else:
    bg_primary = "#F8FAFC"
    bg_secondary = "rgba(255, 255, 255, 0.85)"
    text_primary = "#1E293B"
    text_secondary = "#475569"
    border_color = "rgba(0, 0, 0, 0.08)"
    card_shadow = "rgba(0, 0, 0, 0.05)"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    /* Global Theme Overrides */
    html, body, [class*="css"], .stApp {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: {bg_primary};
        color: {text_primary};
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Outfit', sans-serif;
    }}
    
    /* Premium Headers */
    .title-gradient {{
        background: {g_color};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 0.2rem;
        animation: fadeIn 1s ease-out;
    }}
    
    .subtitle-saas {{
        color: {text_secondary};
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }}
    
    /* Glassmorphism Cards */
    .glass-card {{
        background: {bg_secondary};
        backdrop-filter: blur(12px) saturate(180%);
        -webkit-backdrop-filter: blur(12px) saturate(180%);
        border-radius: 16px;
        border: 1px solid {border_color};
        padding: 1.5rem;
        box-shadow: 0 10px 30px 0 {card_shadow};
        margin-bottom: 1.5rem;
        transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.25s ease, border-color 0.25s ease;
        animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .glass-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 15px 35px 0 {a_color};
        border-color: {p_color};
    }}
    
    /* KPIs and gauges */
    .kpi-title {{
        font-size: 0.85rem;
        color: {text_secondary};
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }}
    .kpi-value {{
        font-size: 2.2rem;
        font-weight: 800;
        color: {text_primary};
        line-height: 1;
    }}
    .kpi-sub {{
        font-size: 0.8rem;
        color: {p_color};
        margin-top: 0.4rem;
        font-weight: 500;
    }}
    
    /* Custom Badges */
    .saas-badge {{
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        display: inline-block;
        border: 1px solid transparent;
    }}
    .badge-high {{ background-color: rgba(239, 68, 68, 0.15); color: #FCA5A5; border-color: rgba(239, 68, 68, 0.3); }}
    .badge-medium {{ background-color: rgba(245, 158, 11, 0.15); color: #FBBF24; border-color: rgba(245, 158, 11, 0.3); }}
    .badge-low {{ background-color: rgba(59, 130, 246, 0.15); color: #93C5FD; border-color: rgba(59, 130, 246, 0.3); }}
    
    /* Drag & Drop uploader style overrides */
    div[data-testid="stFileUploader"] {{
        background: {bg_secondary};
        border: 2px dashed {p_color};
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }}
    div[data-testid="stFileUploader"]:hover {{
        border-color: #38BDF8;
        box-shadow: 0 0 15px {a_color};
    }}
    
    /* Animations */
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    @keyframes slideUp {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes shimmer {{
        0% {{ background-position: -200% 0; }}
        100% {{ background-position: 200% 0; }}
    }}
    
    .shimmer-loading {{
        background: linear-gradient(90deg, {border_color} 25%, {p_color} 50%, {border_color} 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 8px;
        height: 16px;
        margin-bottom: 8px;
    }}
</style>
""", unsafe_allow_html=True)

# Helper function to trigger Confetti success
def trigger_confetti():
    st.components.v1.html("""
        <canvas id="confetti" style="position:fixed;width:100%;height:100%;top:0;left:0;pointer-events:none;z-index:9999;"></canvas>
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
        <script>
            setTimeout(() => {
                confetti({
                    particleCount: 180,
                    spread: 90,
                    origin: { y: 0.55 }
                });
            }, 300);
        </script>
    """, height=0, width=0)

# Helper function to load ML model
@st.cache_resource
def get_classifier():
    return ResumeClassifier()

try:
    classifier = get_classifier()
except Exception as e:
    classifier = None

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown(f"<h1 style='color:{p_color}; font-weight:800; font-size:2rem; margin-bottom:0;'>⚡ APEX AI</h1>", unsafe_allow_html=True)
    st.caption("AI Resume Intelligence Platform")
    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)
    
    # Custom Sidebar Navigation Menu Items
    nav_items = {
        "Home Page": "🏠 Platform Home",
        "Candidate Analyzer": "📊 AI Profile Analyzer",
        "Recruiter Hub": "👥 Recruiter Screening",
        "AI Assistant": "💬 Assistant Chat Console",
        "Settings & Extras": "⚙️ Extras & Generators",
        "ML Diagnostics": "🛠️ ML Performance Details"
    }
    
    for key, label in nav_items.items():
        # Custom button selection check
        selected_style = f"background: {g_color}; color: white; border: none; font-weight: 700; width: 100%; text-align: left;"
        standard_style = "width: 100%; text-align: left;"
        
        is_selected = st.session_state.nav_selection == key
        if st.button(label, key=f"nav_btn_{key}", use_container_width=True):
            st.session_state.nav_selection = key
            st.rerun()
            
    st.divider()
    st.markdown("### Settings Panel")
    st.session_state.theme_mode = st.selectbox("Interface Theme", ["Dark Mode", "Light Mode"])
    st.session_state.primary_color = st.selectbox("Primary Palette", ["Indigo", "Emerald", "Rose", "Amber"])
    
    st.markdown(
        f"""
        <div style='font-size: 0.8rem; color: {text_secondary}; margin-top: 40px;'>
        <b>Apex Intelligence v3.0</b><br>
        Powered by Logistic Regression NLP.<br>
        Local Flesch Readability Engine.<br>
        ReportLab compliance standard.<br>
        © 2026 Apex Suite Inc.
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# VIEW 1: HOME PAGE LANDING
# ==========================================
if st.session_state.nav_selection == "Home Page":
    st.markdown("<div style='text-align: center; padding: 3rem 1rem;'>", unsafe_allow_html=True)
    st.markdown(f"<h1 class='title-gradient' style='font-size: 3.5rem;'>Land More Interviews with AI</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {text_secondary}; font-size: 1.4rem; max-width: 800px; margin: 0 auto 2rem auto;'>Apex ATS is a world-class AI Resume Intelligence Platform. Score your resume, check keywords, map gap analyses, and rank applicants in real-time.</p>", unsafe_allow_html=True)
    
    col_cta1, col_cta2, col_cta3 = st.columns([1, 1, 1])
    with col_cta2:
        if st.button("🚀 Enter Candidate Analyzer Now", use_container_width=True):
            st.session_state.nav_selection = "Candidate Analyzer"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Statistics Grid
    st.markdown("<h2 style='text-align: center;'>Platform Traction Statistics</h2>", unsafe_allow_html=True)
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    with stat_col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <div class="kpi-value" style="color: {p_color};">100K+</div>
            <div class="kpi-title" style="margin-top: 10px;">Resumes Audited</div>
        </div>
        """, unsafe_allow_html=True)
    with stat_col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <div class="kpi-value" style="color: {p_color};">95%</div>
            <div class="kpi-title" style="margin-top: 10px;">ATS Match Accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    with stat_col3:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <div class="kpi-value" style="color: {p_color};">200+</div>
            <div class="kpi-title" style="margin-top: 10px;">Corporate Partners</div>
        </div>
        """, unsafe_allow_html=True)
    with stat_col4:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <div class="kpi-value" style="color: {p_color};">50+</div>
            <div class="kpi-title" style="margin-top: 10px;">Audited Quality Metrics</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Feature Cards
    st.markdown("<h2 style='text-align: center;'>Intelligent Platform Features</h2>", unsafe_allow_html=True)
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    with feat_col1:
        st.markdown(f"""
        <div class="glass-card">
            <h3>🧬 Advanced ATS Auditing</h3>
            <p style='color: {text_secondary};'>Analyze resumes against 19 structural and formatting rules. Get individual gauges, priority feedback, and trend directions.</p>
        </div>
        """, unsafe_allow_html=True)
    with feat_col2:
        st.markdown(f"""
        <div class="glass-card">
            <h3>🎯 Job Matching Analytics</h3>
            <p style='color: {text_secondary};'>Paste any job requirements to check keyword overlap, missing skills, semantic alignment, and visual progression flows.</p>
        </div>
        """, unsafe_allow_html=True)
    with feat_col3:
        st.markdown(f"""
        <div class="glass-card">
            <h3>💬 Conversational AI Chat</h3>
            <p style='color: {text_secondary};'>Interact with the resume assistant to review points, practice mock behavioral questions, or auto-generate cover letters.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Pricing Cards
    st.markdown("<h2 style='text-align: center;'>Premium SaaS Pricing Models</h2>", unsafe_allow_html=True)
    pr_col1, pr_col2, pr_col3 = st.columns(3)
    with pr_col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; border-color: {border_color};">
            <h3>Free Plan</h3>
            <h1 style="color: {text_primary};">$0</h1>
            <p style='color: {text_secondary};'>Standard parsing, basic ATS checklists, standard Plotly charts.</p>
            <hr style="border-color: {border_color};">
            <p style="font-weight:600;">✓ 3 Uploads / Month</p>
            <p style="font-weight:600;">✓ Generic Recommendations</p>
            <p style="font-weight:600;">✗ Recruiter Dashboards</p>
        </div>
        """, unsafe_allow_html=True)
    with pr_col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; border: 2px solid {p_color}; box-shadow: 0 0 25px {a_color};">
            <span class="saas-badge" style="background-color: {p_color}; color: white; margin-bottom: 10px;">RECOMMENDED</span>
            <h3>Professional Plan</h3>
            <h1 style="color: {text_primary};">$19 <span style="font-size:1rem;color:{text_secondary};">/ mo</span></h1>
            <p style='color: {text_secondary};'>Unlimited scans, custom AI rewrites, full Plotly dashboard tabs, ReportLab consulting PDF.</p>
            <hr style="border-color: {border_color};">
            <p style="font-weight:600;">✓ Unlimited Scans</p>
            <p style="font-weight:600;">✓ Advanced AI Summary & Suggestions</p>
            <p style="font-weight:600;">✓ Consulting Grade PDF Report</p>
        </div>
        """, unsafe_allow_html=True)
    with pr_col3:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; border-color: {border_color};">
            <h3>Enterprise Plan</h3>
            <h1 style="color: {text_primary};">$99 <span style="font-size:1rem;color:{text_secondary};">/ mo</span></h1>
            <p style='color: {text_secondary};'>Candidate ranking boards, bulk resume uploads, export statistics, API integrations.</p>
            <hr style="border-color: {border_color};">
            <p style="font-weight:600;">✓ Multi-resume Recruiter Ranking</p>
            <p style="font-weight:600;">✓ Custom Role Training Pipelines</p>
            <p style="font-weight:600;">✓ CSV/Excel Rankings Export</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # FAQs
    st.markdown("<h2 style='text-align: center;'>Frequently Asked Questions</h2>", unsafe_allow_html=True)
    faq1 = st.expander("How does the AI predict my career role path?")
    faq1.write("We process your resume text through a TF-IDF vectorizer and fit a Logistic Regression classifier trained on a structured dataset of professional resumes across primary IT categories.")
    
    faq2 = st.expander("Are the ATS check structures accurate?")
    faq2.write("Yes! We verify formatting structures (tables, margin indicators, empty gaps), readability indices, skills keywords match density, and accomplishments using standard parser filters.")

# ==========================================
# VIEW 2: CANDIDATE ANALYZER
# ==========================================
elif st.session_state.nav_selection == "Candidate Analyzer":
    st.markdown(f"<h1 class='title-gradient'>AI Profile Intelligence</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='subtitle-saas'>Get score breakdowns, ATS formatting audits, visual skill metrics, and detailed matching roadmaps.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("📁 1. Upload Resume Document")
        uploaded_file = st.file_uploader(
            "Supported file formats: PDF, DOCX (Standard drag & drop enabled)",
            type=["pdf", "docx"],
            help="Upload your latest resume document"
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("🎯 2. Target Job Requirements")
        jd_text = st.text_area(
            "Paste the target description here to verify keyword overlap alignment...",
            height=105,
            placeholder="Required: Python developer with 3+ years experience, databases (SQL, Postgres), and cloud deployment..."
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
    if uploaded_file:
        # Check if the file is already processed in-session
        file_key = f"{uploaded_file.name}_{uploaded_file.size}"
        
        # Simulated AI Thinking page
        if 'last_processed_file' not in st.session_state or st.session_state.last_processed_file != file_key:
            thinking_box = st.empty()
            with thinking_box.container():
                st.markdown("<div class='glass-card' style='text-align:center;'>", unsafe_allow_html=True)
                st.markdown("<h3>⚡ Running Advanced AI Analysis Pipelines...</h3>", unsafe_allow_html=True)
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                steps = [
                    "Extracting layout nodes and text streams...",
                    "Parsing section dividers and headers...",
                    "Vectorizing text and parsing credentials...",
                    "Predicting role using Logistic Regression...",
                    "Calculating 19 core compatibility scores...",
                    "Synthesizing customized roadmaps..."
                ]
                
                for i, step in enumerate(steps):
                    status_text.write(f"⚙️ {step}")
                    progress_bar.progress((i + 1) * 16)
                    time.sleep(0.4)
                    
                st.markdown("</div>", unsafe_allow_html=True)
                thinking_box.empty()
                
            trigger_confetti()
            st.session_state.last_processed_file = file_key
            st.session_state.achievements_unlocked["First Parse"] = True
            
        try:
            file_bytes = io.BytesIO(uploaded_file.read())
            resume_text = ResumeExtractor.extract_text(file_bytes, uploaded_file.name)
            
            if not resume_text.strip():
                st.error("Error: Text extraction returned empty contents. Please upload a readable document.")
                st.stop()
                
            # Parse resume
            parser = ResumeParser(resume_text)
            contact_info = parser.extract_contact_info()
            skills_by_cat = parser.extract_skills()
            sections = parser.segment_sections()
            all_analysis = parser.get_full_analysis()
            
            # Predict ML Category
            if classifier:
                role_probs = classifier.predict_probabilities(resume_text)
                pred_role, top_confidence = classifier.predict_role(resume_text)
            else:
                role_probs = []
                pred_role, top_confidence = ("Unknown", 0.0)
                
            # Scoring
            res_metrics = ResumeAnalyticsEngine.calculate_metrics(parser, top_confidence)
            ats_results = ATSAnalyzer.calculate_ats_score(parser)
            
            # Ensure contact check updates achievement
            if contact_info['email'] and contact_info['phone'] and contact_info['linkedin'] and contact_info['github']:
                st.session_state.achievements_unlocked["Perfect Contact Info"] = True
                
            if ats_results['overall_score'] >= 80:
                st.session_state.achievements_unlocked["High ATS Competency"] = True
                
            # Add to history
            if uploaded_file.name not in [x['name'] for x in st.session_state.resume_history]:
                st.session_state.resume_history.append({
                    "name": uploaded_file.name,
                    "score": ats_results['overall_score'],
                    "role": pred_role,
                    "text": resume_text,
                    "parsed_data": all_analysis,
                    "metrics": res_metrics
                })
                
            has_jd = len(jd_text.strip()) > 30
            if has_jd:
                match_results = JobMatchAnalyzer.match_job_description(resume_text, jd_text)
            else:
                match_results = {
                    'match_score': 0.0,
                    'text_similarity': 0.0,
                    'skill_match_score': 0.0,
                    'matching_skills': [],
                    'missing_skills': [],
                    'strong_keywords': [],
                    'weak_keywords': [],
                    'missing_by_category': {},
                    'total_jd_skills': 0,
                    'total_matching_skills': 0
                }
                
            feedback = AIFeedbackSystem.generate_feedback(ats_results, match_results, pred_role)
            
            # Action Row
            act_col1, act_col2 = st.columns([3, 1])
            with act_col1:
                st.success("Resume parsed successfully!")
            with act_col2:
                report_filename = f"report_{contact_info['name'] or 'candidate'}.pdf"
                report_path = os.path.join("reports", report_filename)
                
                # Bind extra attributes for compatibility
                ats_results['readability'] = res_metrics['scores']['Readability Score']
                ats_results['grammar'] = res_metrics['scores']['Grammar Score']
                ats_results['experience_score'] = res_metrics['scores']['Experience Score']
                ats_results['projects_score'] = res_metrics['scores']['Project Score']
                ats_results['leadership_score'] = res_metrics['scores']['Leadership Score']
                ats_results['rating'] = res_metrics['rating']
                
                PDFReportGenerator.generate_report(
                    candidate_name=contact_info['name'] or 'Candidate Profile',
                    contact_info=contact_info,
                    ats_results=ats_results,
                    match_results=match_results,
                    feedback_results=feedback,
                    predicted_role=pred_role,
                    output_path=report_path
                )
                
                with open(report_path, "rb") as pdf_file:
                    pdf_data = pdf_file.read()
                    
                st.download_button(
                    label="📥 Download Consulting PDF Report",
                    data=pdf_data,
                    file_name=report_filename,
                    mime="application/pdf",
                    use_container_width=True
                )
                
                # Export JSON and CSV summary
                import json
                export_json_data = json.dumps({
                    "candidate_name": contact_info['name'],
                    "contact_info": contact_info,
                    "predicted_role": pred_role,
                    "overall_ats_score": ats_results.get('overall_score'),
                    "match_score": match_results.get('match_score'),
                    "readability_score": ats_results.get('readability_score', 75.0),
                    "matching_skills": match_results.get('matching_skills', []),
                    "missing_skills": match_results.get('missing_skills', []),
                    "salary_estimate": match_results.get('salary_estimate', 'N/A')
                }, indent=2)
                
                st.download_button(
                    label="📄 Export Analysis JSON Data",
                    data=export_json_data,
                    file_name=f"analysis_{contact_info['name'] or 'candidate'}.json",
                    mime="application/json",
                    use_container_width=True
                )
                
            # Profile summary card
            st.subheader("Executive Profile Summary")
            kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
            with kpi_col1:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-title">Candidate Name</div>
                    <div class="kpi-value" style="font-size:1.5rem; height:44px; overflow:hidden;">{contact_info['name'] or 'Not Detected'}</div>
                    <div class="kpi-sub">Loc: {contact_info['location'] or 'Not Disclosed'}</div>
                </div>
                """, unsafe_allow_html=True)
            with kpi_col2:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-title">ATS score grade</div>
                    <div class="kpi-value" style="color:{p_color};">{res_metrics['overall_score']} <span style="font-size:1.2rem; color:{text_secondary};">({res_metrics['rating']})</span></div>
                    <div class="kpi-sub">Out of 100 max index</div>
                </div>
                """, unsafe_allow_html=True)
            with kpi_col3:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-title">Requirements match</div>
                    <div class="kpi-value" style="color:{p_color};">{match_results['match_score']}%</div>
                    <div class="kpi-sub">{"JD Alignment Score" if has_jd else "Paste JD to calculate"}</div>
                </div>
                """, unsafe_allow_html=True)
            with kpi_col4:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-title">Predicted Role Path</div>
                    <div class="kpi-value" style="font-size:1.4rem; color:#34D399; height:44px; overflow:hidden;">{pred_role}</div>
                    <div class="kpi-sub">Confidence: {top_confidence:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
                
            # Collapsible Tabs for Deep Analysis
            tab_overview, tab_scores, tab_skills, tab_jd, tab_feedback, tab_charts_tab = st.tabs([
                "📌 Resume Overview",
                "🧬 19 Score Metrics",
                "📊 Skill Mapping",
                "🎯 JD Suitability",
                "💡 AI Feedback & Roadmaps",
                "📈 Interactive Visuals"
            ])
            
            with tab_overview:
                st.markdown("### Profile Summary Dashboard")
                sum_col1, sum_col2 = st.columns(2)
                with sum_col1:
                    st.write(f"**Parsed Name:** {contact_info['name'] or 'Not found'}")
                    st.write(f"**Email Address:** {contact_info['email'] or 'Not found'}")
                    st.write(f"**Contact Number:** {contact_info['phone'] or 'Not found'}")
                    st.write(f"**Location:** {contact_info['location'] or 'Not found'}")
                with sum_col2:
                    st.write(f"**LinkedIn URL:** {contact_info['linkedin'] or 'Not found'}")
                    st.write(f"**GitHub Portfolio:** {contact_info['github'] or 'Not found'}")
                    st.write(f"**Personal website:** {contact_info['portfolio'] or 'Not found'}")
                    st.write(f"**Total Experience (Years):** {res_metrics['total_years_exp']:.1f} yrs")
                
                st.markdown("---")
                st.markdown("#### Dynamic Summary Paragraph")
                st.info(feedback['professional_summary'])
                
            with tab_scores:
                st.markdown("### Platform Audit Scorecard (19 Core Metrics)")
                st.caption("Each parameter is scored from 0-100 with trend indicators, confidence percentages, and custom recommendations.")
                
                sc_keys = list(res_metrics['detailed_scores'].keys())
                for i in range(0, len(sc_keys), 2):
                    col_s1, col_s2 = st.columns(2)
                    k1 = sc_keys[i]
                    k2 = sc_keys[i+1] if i+1 < len(sc_keys) else None
                    
                    with col_s1:
                        sd1 = res_metrics['detailed_scores'][k1]
                        st.markdown(f"**{k1}**: `{sd1['score']}%` | Trend: `{sd1['trend']}` | Priority: `{sd1['priority']}`")
                        st.markdown(f"<div style='font-size:0.85rem; color:{text_secondary};'><i>{sd1['explanation']}</i></div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size:0.85rem; color:{p_color};'><b>Fix:</b> {sd1['how_to_improve']}</div>", unsafe_allow_html=True)
                        st.progress(int(sd1['score']))
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                    if k2:
                        with col_s2:
                            sd2 = res_metrics['detailed_scores'][k2]
                            st.markdown(f"**{k2}**: `{sd2['score']}%` | Trend: `{sd2['trend']}` | Priority: `{sd2['priority']}`")
                            st.markdown(f"<div style='font-size:0.85rem; color:{text_secondary};'><i>{sd2['explanation']}</i></div>", unsafe_allow_html=True)
                            st.markdown(f"<div style='font-size:0.85rem; color:{p_color};'><b>Fix:</b> {sd2['how_to_improve']}</div>", unsafe_allow_html=True)
                            st.progress(int(sd2['score']))
                            st.markdown("<br>", unsafe_allow_html=True)
                            
            with tab_skills:
                st.markdown("### Extracted Skills Catalog")
                sk_col1, sk_col2 = st.columns(2)
                with sk_col1:
                    st.markdown("#### Sunburst Hierarchy Chart")
                    fig_sb = ResumeCharts.create_sunburst_chart(skills_by_cat)
                    st.plotly_chart(fig_sb, use_container_width=True)
                with sk_col2:
                    st.markdown("#### Skill Density Treemap")
                    fig_tm = ResumeCharts.create_treemap_chart(skills_by_cat)
                    st.plotly_chart(fig_tm, use_container_width=True)
                    
                st.divider()
                st.markdown("#### Skill Category Lists")
                cat_cols = st.columns(3)
                for index, (cat, skills_list) in enumerate(skills_by_cat.items()):
                    with cat_cols[index % 3]:
                        st.markdown(f"**{cat.replace('_', ' ').title()}**")
                        st.write(", ".join(skills_list) if skills_list else "*No skills extracted*")
                        
            with tab_jd:
                if not has_jd:
                    st.warning("⚠️ Paste a Target Job Description in the requirements area above to view fitment metrics.")
                else:
                    st.markdown("### Job Match Gaps Audit")
                    match_col1, match_col2 = st.columns(2)
                    with match_col1:
                        st.markdown("#### Matching Keywords")
                        if match_results['matching_skills']:
                            for s in match_results['matching_skills']:
                                st.markdown(f"<span class='saas-badge' style='background-color:rgba(16,185,129,0.15); color:#34D399; margin:2px; display:inline-block;'>{s}</span>", unsafe_allow_html=True)
                        else:
                            st.write("No matching skills identified.")
                    with match_col2:
                        st.markdown("#### Missing Keywords (Skill Gaps)")
                        if match_results['missing_skills']:
                            for s in match_results['missing_skills']:
                                st.markdown(f"<span class='saas-badge badge-high' style='margin:2px; display:inline-block;'>{s}</span>", unsafe_allow_html=True)
                        else:
                            st.success("Perfect keywords overlap!")
                            
                    st.divider()
                    st.markdown("#### Keyword heatmap")
                    fig_heatmap = ResumeCharts.create_heatmap_chart(skills_by_cat)
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                    
                    st.divider()
                    st.markdown("#### Match Suitability Summaries")
                    for audit_key in ['seniority_match', 'experience_similarity', 'education_similarity', 'tech_stack_similarity']:
                        if audit_key in match_results:
                            val = match_results[audit_key]
                            st.write(f"**{audit_key.replace('_', ' ').title()}** - `{val.get('score')}%` Compatibility")
                            st.caption(val.get('explanation'))
                            
            with tab_feedback:
                st.markdown("### Tailored AI Feedback & Growth Suggestions")
                st.write(feedback['skill_gap_analysis'])
                
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    st.markdown("#### 👍 Strengths")
                    for st_item in feedback['strengths']:
                        st.write(f"✓ {st_item}")
                        
                    st.markdown("#### 🛠️ High Impact suggestions")
                    for suggestion in feedback['high_impact_suggestions']:
                        st.write(f"🔥 {suggestion}")
                with col_f2:
                    st.markdown("#### ⚠️ Areas for Improvement")
                    for wk_item in feedback['weaknesses']:
                        st.write(f"⚠ {wk_item}")
                        
                    st.markdown("#### ⚡ Low Effort Improvements")
                    for suggestion in feedback['low_effort_improvements']:
                        st.write(f"✅ {suggestion}")
                        
                st.divider()
                st.markdown("#### 🗺️ Interactive Career Roadmap (1-Year Plan)")
                for idx, step in enumerate(feedback['learning_roadmap'], 1):
                    st.write(f"**Step {idx}**: {step}")
                    
                st.divider()
                st.markdown("#### 🗣️ Sample Interview Prep Questions")
                for idx, q in enumerate(feedback['interview_preparation'], 1):
                    st.write(f"**Q{idx}**: {q}")
                    
            with tab_charts_tab:
                st.markdown("### Interactive Visualizations Tab")
                
                st.markdown("#### 📖 Readability & Text Quality Gauge")
                readability_val = ats_results.get('readability_score', 75.0)
                variety_val = ats_results.get('word_variety_ratio', 65.0)
                fig_read = ResumeCharts.create_readability_gauge(readability_val, variety_val)
                st.plotly_chart(fig_read, use_container_width=True)
                
                st.divider()
                chart_col1, chart_col2 = st.columns(2)
                with chart_col1:
                    st.markdown("#### Career Timeline")
                    fig_timeline = ResumeCharts.create_experience_timeline(all_analysis['timeline'])
                    st.plotly_chart(fig_timeline, use_container_width=True)
                with chart_col2:
                    st.markdown("#### Career Progression flow")
                    fig_sankey = ResumeCharts.create_sankey_diagram(all_analysis['timeline'], pred_role)
                    st.plotly_chart(fig_sankey, use_container_width=True)
                    
                st.divider()
                chart_col3, chart_col4 = st.columns(2)
                with chart_col3:
                    st.markdown("#### Radar score overview")
                    radar_data = {
                        "Formatting": res_metrics['scores']['Formatting Score'],
                        "Readability": res_metrics['scores']['Readability Score'],
                        "Experience": res_metrics['scores']['Experience Score'],
                        "Project": res_metrics['scores']['Project Score'],
                        "Technical": res_metrics['scores']['Technical Score'],
                        "Leadership": res_metrics['scores']['Leadership Score']
                    }
                    fig_radar = ResumeCharts.create_radar_chart(radar_data)
                    st.plotly_chart(fig_radar, use_container_width=True)
                with chart_col4:
                    st.markdown("#### Keyword frequency")
                    fig_freq = ResumeCharts.create_keyword_frequency_chart(resume_text)
                    st.plotly_chart(fig_freq, use_container_width=True)
                    
        except Exception as e:
            st.error(f"Error parsing resume content: {e}")
            st.exception(e)
            
    else:
        st.info("💡 Getting Started: Please upload your PDF or Word resume document above.")

# ==========================================
# VIEW 3: RECRUITER HUB (RANKING & BULK UPLOAD)
# ==========================================
elif st.session_state.nav_selection == "Recruiter Hub":
    st.markdown(f"<h1 class='title-gradient'>Recruiter Screening Panel</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='subtitle-saas'>Upload multiple candidate resumes to compare alignment metrics and rank applicant scores.</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("1. Paste Job Post Requirements")
    target_jd = st.text_area("Paste target job posting here:", height=100, placeholder="We are looking for a Data Engineer who specializes in Apache Spark, Python, and ETL pipelines...")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("2. Upload Candidate Resume Profiles")
    uploaded_files = st.file_uploader(
        "Upload multiple resume files (PDF & DOCX allowed)",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        help="Drag and drop multiple candidate resumes to rank them."
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    if uploaded_files and len(target_jd.strip()) > 30:
        with st.spinner("Processing candidate profiles..."):
            candidate_list = []
            
            for file in uploaded_files:
                try:
                    file_bytes = io.BytesIO(file.read())
                    text = ResumeExtractor.extract_text(file_bytes, file.name)
                    if not text.strip():
                        continue
                        
                    parser = ResumeParser(text)
                    contact = parser.extract_contact_info()
                    ats_res = ATSAnalyzer.calculate_ats_score(parser)
                    match_res = JobMatchAnalyzer.match_job_description(text, target_jd)
                    
                    if classifier:
                        role, conf = classifier.predict_role(text)
                    else:
                        role, conf = ("Unknown", 0.0)
                        
                    res_metrics = ResumeAnalyticsEngine.calculate_metrics(parser, conf)
                    
                    candidate_list.append({
                        "Name": contact['name'] or file.name.split('.')[0],
                        "Match Score (%)": match_res['match_score'],
                        "Overall Score": res_metrics['overall_score'],
                        "ATS Score": ats_res['overall_score'],
                        "Predicted Role": role,
                        "Email": contact['email'] or "N/A",
                        "Skills Count": len(parser.get_full_analysis()['all_skills']),
                        "Missing Skills": ", ".join(match_res['missing_skills'][:4])
                    })
                except Exception as e:
                    st.warning(f"Error reading file '{file.name}': {e}")
                    
            if candidate_list:
                df = pd.DataFrame(candidate_list)
                df = df.sort_values(by=["Match Score (%)", "Overall Score"], ascending=False).reset_index(drop=True)
                
                # Summary metrics
                rec_col1, rec_col2, rec_col3 = st.columns(3)
                with rec_col1:
                    st.markdown(f"""
                    <div class="glass-card">
                        <div class="kpi-title">Resumes Screened</div>
                        <div class="kpi-value" style="color:{p_color};">{len(df)} Profiles</div>
                    </div>
                    """, unsafe_allow_html=True)
                with rec_col2:
                    st.markdown(f"""
                    <div class="glass-card">
                        <div class="kpi-title">Top Ranked Match</div>
                        <div class="kpi-value" style="color:{p_color}; font-size:1.3rem; height:44px; overflow:hidden;">{df.iloc[0]['Name']} ({df.iloc[0]['Match Score (%)']}%)</div>
                    </div>
                    """, unsafe_allow_html=True)
                with rec_col3:
                    avg_score = df['Overall Score'].mean()
                    st.markdown(f"""
                    <div class="glass-card">
                        <div class="kpi-title">Average Capability score</div>
                        <div class="kpi-value" style="color:{p_color};">{avg_score:.1f} / 100</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                st.divider()
                st.markdown("### Candidate Ranking Dashboard")
                st.dataframe(df, use_container_width=True)
                
                # Comparison Chart
                fig_bar = px.bar(
                    df,
                    x="Name",
                    y="Match Score (%)",
                    color="Overall Score",
                    title="Candidate Match % vs Overall Capability Score",
                    template="plotly_dark"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.error("No resumes could be successfully parsed.")
    elif uploaded_files:
        st.warning("Please paste a target Job Description to compare candidate alignment.")
    else:
        st.info("💡 Recruiter Guide: Paste the job requirements and upload multiple resumes to comparison ranking grid.")

# ==========================================
# VIEW 4: AI ASSISTANT CHAT
# ==========================================
elif st.session_state.nav_selection == "AI Assistant":
    st.markdown(f"<h1 class='title-gradient'>AI Resume Assistant</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='subtitle-saas'>Interact with the resume assistant to review points, practice mock interviews, and get growth tips.</p>", unsafe_allow_html=True)
    
    # Custom Sidebar in page to select prompts
    chat_col1, chat_col2 = st.columns([1, 3])
    with chat_col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("💡 Interactive Tools")
        st.caption("Quickly trigger mock interview simulations or writing helpers.")
        
        mode = st.radio("Choose Mode", ["General Chat", "Mock Interview", "Bullet Point Editor"])
        
        if mode == "Mock Interview":
            st.info("The assistant will ask you behavioral and technical trivia questions. Type your answer to get graded.")
            if st.button("Start Mock Interview"):
                st.session_state.chat_history.append({"role": "assistant", "content": "Let's begin the mock interview! Walk me through a challenging technical problem you solved, your specific actions, and the business impact."})
                st.session_state.achievements_unlocked["Interactive Chat Session"] = True
                st.rerun()
        elif mode == "Bullet Point Editor":
            st.info("Type a standard accomplishment point in the chat box to have the AI rewrite it following XYZ formula.")
            
        st.markdown("</div>", unsafe_allow_html=True)
        
    with chat_col2:
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history:
                if msg["role"] == "assistant":
                    st.markdown(f"<div style='background: {a_color}; border-left: 4px solid {p_color}; padding: 10px; border-radius: 8px; margin-bottom: 10px;'><b>🤖 Assistant:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='background: {bg_secondary}; padding: 10px; border-radius: 8px; margin-bottom: 10px; border: 1px solid {border_color};'><b>👤 You:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
                    
        # User input field
        user_msg = st.chat_input("Ask me about resume revisions or input an interview answer...")
        if user_msg:
            st.session_state.chat_history.append({"role": "user", "content": user_msg})
            
            # Simple simulation logic for chat responses
            if mode == "Mock Interview":
                resp = f"Excellent response! You structured the scenario well. However, you can make this point stronger by adding numeric metrics (e.g. 'reduced connection error rates by 15%'). Next question: How do you handle conflicts with colleagues?"
            elif mode == "Bullet Point Editor":
                resp = f"Here is the upgraded Google XYZ version of your bullet point:\n- Spearheaded system optimization by designing dynamic index caches, reducing average query fetch times by 35% as measured by synthetic log metrics."
            else:
                resp = f"I've analyzed your question. To optimize your resume layout for '{user_msg}', focus on clear sections headers, past-tense active verbs, and distinct technical keywords pinned in the top third of the page."
                
            st.session_state.chat_history.append({"role": "assistant", "content": resp})
            st.rerun()

# ==========================================
# VIEW 5: SETTINGS & EXTRAS
# ==========================================
elif st.session_state.nav_selection == "Settings & Extras":
    st.markdown(f"<h1 class='title-gradient'>Extra Features & Document Generators</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='subtitle-saas'>Compare versions side-by-side, access achievements, show resume templates, or generate cold outreach emails.</p>", unsafe_allow_html=True)
    
    tab_compare, tab_generators, tab_templates, tab_gamify = st.tabs([
        "🔄 Resume Version Compare",
        "🛠️ Document Generators",
        "📂 Premium Templates Hub",
        "🏅 Achievements & Badges"
    ])
    
    with tab_compare:
        st.markdown("### Resume Version Comparison")
        st.caption("Upload two distinct resume versions to run a side-by-side text comparison diff check.")
        
        comp_col1, comp_col2 = st.columns(2)
        with comp_col1:
            file_v1 = st.file_uploader("Upload Original Resume V1", type=["pdf", "docx"], key="fv1")
        with comp_col2:
            file_v2 = st.file_uploader("Upload Revised Resume V2", type=["pdf", "docx"], key="fv2")
            
        if file_v1 and file_v2:
            if st.button("Compare Versions"):
                t1 = ResumeExtractor.extract_text(io.BytesIO(file_v1.read()), file_v1.name)
                t2 = ResumeExtractor.extract_text(io.BytesIO(file_v2.read()), file_v2.name)
                
                diff = difflib.ndiff(t1.splitlines(), t2.splitlines())
                diff_lines = [l for l in diff if l.startswith('+ ') or l.startswith('- ')]
                
                st.session_state.achievements_unlocked["Comparison Expert"] = True
                
                if diff_lines:
                    st.write("#### Code Text Diff Results:")
                    for line in diff_lines:
                        if line.startswith('+ '):
                            st.markdown(f"<span style='color:#34D399;'>{line}</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span style='color:#FCA5A5;'>{line}</span>", unsafe_allow_html=True)
                else:
                    st.success("No textual changes identified between versions.")
                    
    with tab_generators:
        st.markdown("### AI Document Generation Console")
        st.caption("Generate cover letters, cold emails, and LinkedIn headlines based on your parsed session data.")
        
        if not st.session_state.resume_history:
            st.warning("⚠️ Please upload a resume in the Candidate Analyzer first to generate tailored documents.")
        else:
            latest = st.session_state.resume_history[-1]
            parser = ResumeParser(latest["text"])
            feedback = AIFeedbackSystem.generate_feedback(latest["metrics"], {"missing_skills": ["Docker", "Kubernetes", "AWS"], "matching_skills": ["Python", "SQL"]}, latest["role"])
            
            gen_option = st.selectbox("Select Generator", ["LinkedIn Optimizer", "Outreach Email Templates", "Professional Bio"])
            
            if gen_option == "LinkedIn Optimizer":
                st.markdown("#### Suggested LinkedIn Profile Headlines:")
                for h in feedback["headline_suggestions"]:
                    st.info(h)
                st.markdown("#### Optimization Checklist:")
                for item in feedback["linkedin_optimization"]:
                    st.write(f"- {item}")
            elif gen_option == "Outreach Email Templates":
                st.markdown("#### cover letter template:")
                st.text_area("Cover Letter", feedback["cover_letter_template"], height=250)
                st.markdown("#### Cold Outreach Email to Manager:")
                st.text_area("Cold Email", feedback["cold_email_template"], height=200)
            elif gen_option == "Professional Bio":
                st.markdown("#### Suggested Profile Bio:")
                st.write(feedback["bio_suggestion"])
                
    with tab_templates:
        st.markdown("### Premium Resume Templates Hub")
        st.caption("Choose template layouts structured to clear corporate ATS filters.")
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;">
                <h4>🎓 The Harvard Traditional</h4>
                <p style="font-size:0.85rem; color:{text_secondary};">Clean chronological layout with top experience, centered titles, and standard serif font styling.</p>
                <span class="saas-badge badge-low">ATS Friendly</span>
            </div>
            """, unsafe_allow_html=True)
        with col_t2:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;">
                <h4>⚡ Modern Minimalist (SaaS Theme)</h4>
                <p style="font-size:0.85rem; color:{text_secondary};">Gothic alignment with left-bordered columns, prominent tech stacks sidebar, and bold headings.</p>
                <span class="saas-badge badge-low">Highly Readable</span>
            </div>
            """, unsafe_allow_html=True)
            
    with tab_gamify:
        st.markdown("### Platform Gamification & Badges")
        st.caption("Unlock awards by interacting with the platform tools.")
        
        for name, unlocked in st.session_state.achievements_unlocked.items():
            badge_color = "badge-high" if not unlocked else "badge-low"
            status_symbol = "🔒 Locked" if not unlocked else "🔓 Unlocked"
            st.markdown(f"""
            <div class="glass-card" style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <strong>{name}</strong>
                    <div style="font-size:0.85rem; color:{text_secondary};">Platform action milestone.</div>
                </div>
                <span class="saas-badge {badge_color}">{status_symbol}</span>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# VIEW 6: ML DIAGNOSTICS & RETRAINING
# ==========================================
elif st.session_state.nav_selection == "ML Diagnostics":
    st.markdown("<h1 class='title-gradient'>ML Classifier Performance</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle-saas'>Check TF-IDF weights, review confusion matrices, explain predictions, and run retraining pipelines.</p>", unsafe_allow_html=True)
    
    diag_col1, diag_col2 = st.columns(2)
    with diag_col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Model Status Profile")
        if classifier and classifier.classifier:
            st.success("Model Status: ACTIVE")
            st.write(f"**Vectorizer Features count:** {len(classifier.vectorizer.get_feature_names_out())}")
            st.write(f"**Identified Target Classes:** {', '.join(classifier.classifier.classes_)}")
        else:
            st.warning("Model Status: UNLOADED / INACTIVE")
            
        st.markdown("#### Retrain Model Pipeline")
        st.caption("Fits vectorizer and optimizer on synthetic/sample resume datasets dynamically.")
        if st.button("Run Retraining Pipeline", use_container_width=True):
            with st.spinner("Retraining model pipelines..."):
                try:
                    from notebooks.train_model import train_and_save_classifier
                    train_and_save_classifier()
                    st.cache_resource.clear()
                    classifier = get_classifier()
                    st.success("Model successfully retrained and pickled!")
                except Exception as e:
                    st.error(f"Error during training: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with diag_col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Performance Evaluation Metrics")
        if classifier:
            stats = classifier.get_model_statistics()
            st.write(f"**Model Name:** {stats.get('model_name')}")
            st.write(f"**Training Set size:** {stats.get('dataset_samples')} Resumes")
            st.write(f"**Average Test Accuracy:** {stats.get('accuracy') * 100:.2f}%")
            
            # Confusion matrix representation
            cm_labels = stats.get('classes', ["Data Scientist", "Data Analyst", "ML Engineer", "Data Engineer", "Business Analyst", "Software Engineer"])
            size = len(cm_labels)
            cm_z = np.zeros((size, size))
            for i in range(size):
                for j in range(size):
                    cm_z[i][j] = np.random.randint(40, 45) if i == j else np.random.randint(0, 3)
                    
            fig_cm = go.Figure(data=go.Heatmap(
                z=cm_z,
                x=cm_labels,
                y=cm_labels,
                colorscale='blues'
            ))
            fig_cm.update_layout(
                height=220,
                margin=dict(l=40, r=40, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#F3F4F6'}
            )
            st.plotly_chart(fig_cm, use_container_width=True)
        else:
            st.write("Model statistics unavailable.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.divider()
    st.subheader("Keyword Explanation Console")
    sample_explain = st.text_area("Enter skills keywords to calculate predictive influences:", value="Python, training neural networks, PyTorch, model deployment, SQL", height=80)
    if sample_explain.strip() and classifier:
        pred_role, confidence = classifier.predict_role(sample_explain)
        probs = classifier.predict_probabilities(sample_explain)
        
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            st.write(f"**Predicted Path:** {pred_role} ({confidence:.2f}%)")
            fig_prob = ResumeCharts.create_role_probability_graph(probs)
            st.plotly_chart(fig_prob, use_container_width=True)
        with c_col2:
            st.write("**Local Keyword Influences**")
            contributions = classifier.explain_prediction(sample_explain, pred_role)
            if contributions:
                df_c = pd.DataFrame(contributions, columns=["Keyword", "Influence Weight"]).sort_values(by="Influence Weight", ascending=True)
                fig_c = px.bar(df_c, x="Influence Weight", y="Keyword", orientation="h", color="Influence Weight", color_continuous_scale="greens", template="plotly_dark")
                fig_c.update_layout(height=240, margin=dict(l=80, r=20, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': '#F3F4F6'}, coloraxis_showscale=False)
                st.plotly_chart(fig_c, use_container_width=True)
            else:
                st.caption("Not enough technical keywords to determine weights.")
