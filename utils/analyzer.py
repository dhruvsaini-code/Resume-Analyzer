import re
import numpy as np
from typing import Dict, Any, List, Set, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.parser import ResumeParser
from utils.constants import DEGREE_LEVELS, SENIORITY_KEYWORDS, ACTION_VERBS, SKILL_CATEGORIES

class ATSAnalyzer:
    """
    Analyzes a resume to calculate an ATS compatibility score and section breakdown.
    Delegates to the advanced ResumeAnalyticsEngine while preserving backward-compatible structure.
    """
    
    @staticmethod
    def calculate_ats_score(parser: ResumeParser) -> Dict[str, Any]:
        """
        Calculates an ATS score (0-100) and returns structural details.
        """
        # Delegate to the advanced analytics system for the backend score
        from utils.analytics import ResumeAnalyticsEngine
        res = ResumeAnalyticsEngine.calculate_metrics(parser)
        
        # Build backward-compatible structure expected by older modules
        analysis = parser.get_full_analysis()
        sections = analysis['sections']
        contact = analysis['contact']
        text = parser.text
        
        # Re-verify sections check
        section_status = {}
        for sec in ['education', 'experience', 'projects', 'certifications']:
            section_status[sec] = len(sections.get(sec, '').strip()) > 50
            
        # Re-verify contacts check
        contact_status = {}
        for key in ['name', 'email', 'phone', 'linkedin', 'github']:
            contact_status[key] = contact.get(key) is not None and len(str(contact.get(key)).strip()) > 3
            
        has_bullets = bool(re.search(r'[-*•►▪|]', text))
        has_metrics = bool(re.search(r'\b\d+(?:\.\d+)?%|\$\d+|\b(?:million|billion|increased|decreased|reduced|saved|improved)\b', text.lower()))
        
        return {
            'overall_score': res['scores']['ATS Compatibility'],
            'skills_score': res['scores']['Technical Score'] * 0.3, # Scaled down to max 30
            'sections_score': res['scores']['Resume Completeness'] * 0.3, # Scaled down to max 30
            'contact_score': res['scores']['Formatting Score'] * 0.2, # Scaled down to max 20
            'formatting_score': res['scores']['Section Quality'] * 0.2, # Scaled down to max 20
            'section_status': section_status,
            'contact_status': contact_status,
            'metrics_detected': has_metrics,
            'bullets_detected': has_bullets,
            'word_count': res['word_count']
        }


class JobMatchAnalyzer:
    """
    Advanced Job Description matching module.
    """
    
    @staticmethod
    def match_job_description(resume_text: str, jd_text: str) -> Dict[str, Any]:
        """
        Performs a multi-dimensional assessment of resume text against Job Description, evaluating:
        - Text Similarity (Cosine TF-IDF)
        - Skill Overlap (Strong vs Weak, Missing)
        - Seniority Match
        - Technology Stack Alignment
        - Years of Experience Comparison
        - Education Level Matching
        - Action Verbs Density
        - Industry Terminology
        """
        # 1. Parse both texts
        resume_parser = ResumeParser(resume_text)
        jd_parser = ResumeParser(jd_text)
        
        resume_analysis = resume_parser.get_full_analysis()
        jd_analysis = jd_parser.get_full_analysis()
        
        resume_skills_cat = resume_analysis['skills']
        jd_skills_cat = jd_analysis['skills']
        
        # Flatten skills
        resume_skills_flat = {s.lower() for s_list in resume_skills_cat.values() for s in s_list}
        jd_skills_flat = {s.lower() for s_list in jd_skills_cat.values() for s in s_list}
        
        # Skill splits: Matching, Missing, Strong, Weak
        matching_skills = resume_skills_flat.intersection(jd_skills_flat)
        missing_skills = jd_skills_flat.difference(resume_skills_flat)
        
        # Strong keywords: Present in both with multiple occurrences, or matching core skill categories
        strong_skills = []
        weak_skills = []
        for s in matching_skills:
            # Count occurrences in resume
            count = len(re.findall(rf'\b{re.escape(s)}\b', resume_text.lower()))
            if count >= 2:
                strong_skills.append(s.title())
            else:
                weak_skills.append(s.title())
                
        # Skill Overlap Score
        if jd_skills_flat:
            skill_overlap_score = (len(matching_skills) / len(jd_skills_flat)) * 100
        else:
            skill_overlap_score = 0.0
            
        # 2. Text Cosine Similarity
        clean_resume = re.sub(r'[^a-zA-Z\s]', ' ', resume_text.lower())
        clean_jd = re.sub(r'[^a-zA-Z\s]', ' ', jd_text.lower())
        
        tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        try:
            tfidf_matrix = tfidf.fit_transform([clean_resume, clean_jd])
            text_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100
        except Exception:
            text_sim = 0.0
            
        # 3. Seniority Match
        resume_sen = 'mid'
        jd_sen = 'mid'
        for lvl, kws in SENIORITY_KEYWORDS.items():
            if any(kw in resume_text.lower() for kw in kws):
                resume_sen = lvl
                break
        for lvl, kws in SENIORITY_KEYWORDS.items():
            if any(kw in jd_text.lower() for kw in kws):
                jd_sen = lvl
                break
                
        seniority_scores = {'exec': 4, 'senior': 3, 'mid': 2, 'junior': 1}
        if seniority_scores[resume_sen] >= seniority_scores[jd_sen]:
            seniority_score = 100.0
            seniority_explanation = f"Match Success: Resume indicates '{resume_sen.upper()}' qualifications, meeting or exceeding the job requirement of '{jd_sen.upper()}'."
        else:
            seniority_score = 60.0
            seniority_explanation = f"Warning: The job description calls for '{jd_sen.upper()}' seniority, whereas your resume matches '{resume_sen.upper()}' level terminology."
            
        # 4. Tech Stack Similarity (compare Programming, Cloud/DevOps, and Database counts)
        tech_categories = ['programming', 'database', 'cloud_devops']
        tech_matched = 0
        tech_total = 0
        for cat in tech_categories:
            resume_cat_skills = {s.lower() for s in resume_skills_cat.get(cat, [])}
            jd_cat_skills = {s.lower() for s in jd_skills_cat.get(cat, [])}
            tech_total += len(jd_cat_skills)
            tech_matched += len(resume_cat_skills.intersection(jd_cat_skills))
            
        tech_stack_score = (tech_matched / tech_total) * 100.0 if tech_total > 0 else 80.0
        
        # 5. Experience Years Similarity
        # Parse years from JD e.g., "5+ years", "3 years", "8 years of experience"
        jd_years_needed = 2 # default fallback
        years_matches = re.findall(r'\b(\d{1,2})\s*\+?\s*years?(?:\s+of)?\s+experience\b', jd_text.lower())
        if years_matches:
            jd_years_needed = int(years_matches[0])
            
        resume_years = sum(t.get('duration_years', 0) for t in resume_analysis['timeline'])
        if resume_years >= jd_years_needed:
            exp_score = 100.0
            exp_explanation = f"Success: Candidate has approximately {resume_years:.1f} years of experience, exceeding the required {jd_years_needed} years."
        else:
            exp_score = max(30.0, (resume_years / jd_years_needed) * 100.0)
            exp_explanation = f"Gap: The job description requests {jd_years_needed} years of experience, but only {resume_years:.1f} years were parsed from your experience timeline."
            
        # 6. Education Rank Similarity
        resume_edu_rank = 0
        jd_edu_rank = 0
        
        resume_edu_text = resume_analysis['sections'].get('education', '').lower()
        jd_edu_text = jd_text.lower()
        
        for deg, keywords in DEGREE_LEVELS.items():
            if any(kw in resume_edu_text for kw in keywords):
                if deg == 'phd': resume_edu_rank = 3
                elif deg == 'master': resume_edu_rank = 2
                elif deg == 'bachelor': resume_edu_rank = 1
                break
        for deg, keywords in DEGREE_LEVELS.items():
            if any(kw in jd_edu_text for kw in keywords):
                if deg == 'phd': jd_edu_rank = 3
                elif deg == 'master': jd_edu_rank = 2
                elif deg == 'bachelor': jd_edu_rank = 1
                break
                
        if resume_edu_rank >= jd_edu_rank:
            edu_match_score = 100.0
            edu_explanation = "Success: Your education credentials meet or exceed the target job description requirements."
        else:
            edu_match_score = 70.0
            edu_explanation = f"Caution: The job description indicates a preference for higher academic levels (e.g. Master/PhD) than detected in your profile."
            
        # 7. Action Verbs Comparison
        # Check action verb count in resume vs count in JD
        resume_av = sum(len(re.findall(rf'\b{verb}\b', resume_text.lower())) for verb in ACTION_VERBS)
        jd_av = sum(len(re.findall(rf'\b{verb}\b', jd_text.lower())) for verb in ACTION_VERBS)
        
        av_score = min(100.0, (resume_av / max(5, jd_av)) * 100.0)
        av_explanation = f"Action Verbs density: Found {resume_av} in resume vs {jd_av} requested in JD. Active voice improves ATS compliance."
        
        # 8. Industry Terminology Match
        # Identify common business/tech acronyms in JD (e.g. ETL, NLP, CI/CD, ROI, KPI, BI)
        industry_acronyms = set(re.findall(r'\b[A-Z]{2,5}\b', jd_text))
        matched_acronyms = {acr for acr in industry_acronyms if acr in resume_text}
        
        industry_score = (len(matched_acronyms) / len(industry_acronyms)) * 100.0 if industry_acronyms else 80.0
        industry_explanation = f"Matched {len(matched_acronyms)} standard industry acronyms out of {len(industry_acronyms)}: {', '.join(list(matched_acronyms)[:6])}."
        
        # 9. Role Match Cosine Similarity
        # Compare job title or predicted role
        role_score = text_sim # heuristic fallback
        
        # 10. Combine all into a master Match Score
        # Weights: Cosine text similarity (20%), Skill overlap (35%), Tech stack (15%), Experience years (15%), Education (5%), Seniority (10%)
        weighted_score = (
            text_sim * 0.20 +
            skill_overlap_score * 0.35 +
            tech_stack_score * 0.15 +
            exp_score * 0.15 +
            edu_match_score * 0.05 +
            seniority_score * 0.10
        )
        
        overall_match = round(weighted_score, 1)
        
        # Categorize missing skills by domain
        missing_by_category = {}
        for category, jd_skills_in_cat in jd_skills_cat.items():
            missing_in_cat = []
            for s in jd_skills_in_cat:
                if s.lower() in missing_skills:
                    missing_in_cat.append(s)
            if missing_in_cat:
                missing_by_category[category] = missing_in_cat
                
        return {
            'match_score': overall_match,
            'text_similarity': round(text_sim, 1),
            'skill_match_score': round(skill_overlap_score, 1),
            'matching_skills': [s.title() for s in matching_skills],
            'missing_skills': [s.title() for s in missing_skills],
            'strong_keywords': strong_skills,
            'weak_keywords': weak_skills,
            'missing_by_category': missing_by_category,
            'total_jd_skills': len(jd_skills_flat),
            'total_matching_skills': len(matching_skills),
            
            # Advanced analysis breakdowns
            'seniority_match': {
                'candidate': resume_sen.upper(),
                'required': jd_sen.upper(),
                'score': seniority_score,
                'explanation': seniority_explanation
            },
            'tech_stack_similarity': {
                'score': round(tech_stack_score, 1),
                'explanation': f"Matched {tech_matched} out of {tech_total} requested framework/developer skills across databases & cloud tools."
            },
            'experience_similarity': {
                'score': round(exp_score, 1),
                'explanation': exp_explanation
            },
            'education_similarity': {
                'score': round(edu_match_score, 1),
                'explanation': edu_explanation
            },
            'action_verbs_comparison': {
                'score': round(av_score, 1),
                'explanation': av_explanation
            },
            'industry_terminology': {
                'score': round(industry_score, 1),
                'explanation': industry_explanation
            }
        }
