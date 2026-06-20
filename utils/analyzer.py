import re
import numpy as np
from typing import Dict, Any, List, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.parser import ResumeParser

class ATSAnalyzer:
    """
    Analyzes a resume to calculate an ATS compatibility score and section breakdown.
    """
    
    @staticmethod
    def calculate_ats_score(parser: ResumeParser) -> Dict[str, Any]:
        """
        Calculates an ATS score (0-100) based on:
        1. Skill density & variety (30%)
        2. Section completeness (30%)
        3. Contact details completeness (20%)
        4. Structure & metric density (20%)
        """
        analysis = parser.get_full_analysis()
        skills = analysis['skills']
        sections = analysis['sections']
        contact = analysis['contact']
        text = parser.text
        
        # 1. Skill Score (Max 30)
        # Count total skills found
        total_skills_count = len(analysis['all_skills'])
        # Score scales up to 10 skills (3 points per skill)
        skills_score = min(total_skills_count * 3.0, 30.0)
        
        # 2. Section Completeness (Max 30)
        # 7.5 points for each section header detected
        sections_score = 0.0
        section_status = {}
        for sec in ['education', 'experience', 'projects', 'certifications']:
            has_content = len(sections.get(sec, '').strip()) > 50 # Must have some substantive text
            section_status[sec] = has_content
            if has_content:
                sections_score += 7.5
                
        # 3. Contact Info Completeness (Max 20)
        # 4 points for each core element: Name, Email, Phone, LinkedIn, GitHub
        contact_score = 0.0
        contact_status = {}
        for key in ['name', 'email', 'phone', 'linkedin', 'github']:
            val = contact.get(key)
            has_val = val is not None and len(str(val).strip()) > 3
            contact_status[key] = has_val
            if has_val:
                contact_score += 4.0
                
        # 4. Formatting and Metrics (Max 20)
        # - Has bullet points or lists (5 pts)
        # - Mention of percentages, metrics, or dollar amounts representing impact (10 pts)
        # - Resume length is appropriate (150-1000 words) (5 pts)
        formatting_score = 0.0
        
        # Bullet points check
        has_bullets = bool(re.search(r'[-*•►▪|]', text))
        if has_bullets:
            formatting_score += 5.0
            
        # Metrics check (numbers followed by %, $, or keywords like "increase", "reduce", "million", "billion")
        has_metrics = bool(re.search(r'\b\d+(?:\.\d+)?%|\$\d+|\b(?:million|billion|increased|decreased|reduced|saved|improved)\b', text.lower()))
        if has_metrics:
            formatting_score += 10.0
            
        # Word count check
        word_count = len(text.split())
        if 150 <= word_count <= 1000:
            formatting_score += 5.0
        elif word_count > 1000:
            formatting_score += 3.0 # Slightly penalize extremely long resumes
            
        overall_score = skills_score + sections_score + contact_score + formatting_score
        
        return {
            'overall_score': round(overall_score, 1),
            'skills_score': round(skills_score, 1),
            'sections_score': round(sections_score, 1),
            'contact_score': round(contact_score, 1),
            'formatting_score': round(formatting_score, 1),
            'section_status': section_status,
            'contact_status': contact_status,
            'metrics_detected': has_metrics,
            'bullets_detected': has_bullets,
            'word_count': word_count
        }


class JobMatchAnalyzer:
    """
    Compares a resume with a Job Description to calculate suitability scores.
    """
    
    @staticmethod
    def match_job_description(resume_text: str, jd_text: str) -> Dict[str, Any]:
        """
        Compares resume text with Job Description.
        Calculates:
        - Match Score (%) - combined cosine similarity and skill match
        - Matching Skills
        - Missing Skills (skills in JD that are missing in resume)
        - Matching Keywords / Key phrase comparisons
        """
        # Parse skills from both
        resume_parser = ResumeParser(resume_text)
        jd_parser = ResumeParser(jd_text)
        
        resume_skills_cat = resume_parser.extract_skills()
        jd_skills_cat = jd_parser.extract_skills()
        
        # Flatten skills
        resume_skills = set()
        for s_list in resume_skills_cat.values():
            resume_skills.update([s.lower() for s in s_list])
            
        jd_skills = set()
        for s_list in jd_skills_cat.values():
            jd_skills.update([s.lower() for s in s_list])
            
        # Calculate Skill Match
        matching_skills = resume_skills.intersection(jd_skills)
        missing_skills = jd_skills.difference(resume_skills)
        
        if jd_skills:
            skill_match_score = (len(matching_skills) / len(jd_skills)) * 100
        else:
            skill_match_score = 0.0
            
        # Calculate Text Similarity (Cosine Similarity using TF-IDF)
        clean_resume = re.sub(r'[^a-zA-Z\s]', ' ', resume_text.lower())
        clean_jd = re.sub(r'[^a-zA-Z\s]', ' ', jd_text.lower())
        
        tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        try:
            tfidf_matrix = tfidf.fit_transform([clean_resume, clean_jd])
            text_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100
        except Exception:
            text_sim = 0.0
            
        # Combine Scores
        # 60% Skill overlap, 40% Semantic Text similarity
        if len(jd_skills) > 0:
            match_score = (skill_match_score * 0.6) + (text_sim * 0.4)
        else:
            # Fallback to pure text similarity if no skills found in JD
            match_score = text_sim
            
        # Apply scaling to make the score realistic yet encouraging
        # A good match might yield ~0.3 similarity, so we scale it.
        if len(jd_skills) == 0:
            match_score = min(100.0, match_score * 1.8)
            
        # Sort skills for display
        display_matching = [s.title() for s in matching_skills]
        display_missing = [s.title() for s in missing_skills]
        
        # Category breakdown of missing skills
        missing_by_category = {}
        for category, jd_skills_in_cat in jd_skills_cat.items():
            missing_in_cat = []
            for s in jd_skills_in_cat:
                if s.lower() in missing_skills:
                    missing_in_cat.append(s)
            if missing_in_cat:
                missing_by_category[category] = missing_in_cat
                
        return {
            'match_score': round(match_score, 1),
            'text_similarity': round(text_sim, 1),
            'skill_match_score': round(skill_match_score, 1),
            'matching_skills': display_matching,
            'missing_skills': display_missing,
            'missing_by_category': missing_by_category,
            'total_jd_skills': len(jd_skills),
            'total_matching_skills': len(matching_skills)
        }
