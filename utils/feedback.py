from typing import Dict, Any, List
from utils.constants import ROLE_RECOMMENDATIONS, SOFT_SKILLS_LIST

class AIFeedbackSystem:
    """
    Generates structured, premium feedback and career roadmaps based on resume analysis,
    job matching details, and predicted role category.
    """
    
    @staticmethod
    def generate_feedback(ats_data: Dict[str, Any], match_data: Dict[str, Any], predicted_role: str) -> Dict[str, Any]:
        """
        Synthesizes strengths, weaknesses, formatting/ATS fixes, certifications, roadmap,
        priority actions, and interview prep questions.
        """
        strengths = []
        weaknesses = []
        immediate_improvements = []
        ats_improvements = []
        formatting_improvements = []
        grammar_improvements = []
        
        # 1. Strengths Check
        contact_status = ats_data.get('contact_status', {})
        if contact_status.get('email') and contact_status.get('phone'):
            strengths.append("Verified Contacts: Email and phone number are present and parseable.")
        if contact_status.get('linkedin'):
            strengths.append("LinkedIn Profile Integrated: Allows recruiters to review professional socials.")
        if contact_status.get('github'):
            strengths.append("GitHub Portfolio Present: Showcases open-source projects and code samples.")
            
        word_cnt = ats_data.get('word_count', 0)
        if 150 <= word_cnt <= 800:
            strengths.append(f"Ideal Word Count: Your resume is {word_cnt} words, falling in the optimal range.")
        else:
            if word_cnt < 150:
                weaknesses.append("Content too short: Your resume has fewer than 150 words. Add more context to projects and jobs.")
                immediate_improvements.append("Expand job and project descriptions to reach at least 400 words.")
            else:
                weaknesses.append("Resume too verbose: Word count exceeds 800 words. Keep it focused on high impact details.")
                formatting_improvements.append("Condense experience summaries to fit a clean 1-2 page layout.")
                
        # Check bullets and metrics
        if ats_data.get('bullets_detected', False):
            strengths.append("Structured Layout: Bullet lists detected, enhancing parsing readability.")
        else:
            weaknesses.append("Wall of Text: No standard lists/bullet points detected.")
            ats_improvements.append("Replace paragraph blocks in Experience sections with clean bullet points.")
            
        if ats_data.get('metrics_detected', False):
            strengths.append("Quantified Achievements: Includes numeric impact metrics (%, $, rates).")
        else:
            weaknesses.append("Vague Descriptions: Lacks quantified results and business impact.")
            immediate_improvements.append("Revise project bullets using the XYZ formula: 'Accomplished [X] as measured by [Y], by doing [Z]'.")
            
        # 2. Section Checks
        section_status = ats_data.get('section_status', {})
        missing_sections = [sec.replace('_', ' ').title() for sec, ok in section_status.items() if not ok]
        if missing_sections:
            weaknesses.append(f"Missing Core Sections: {', '.join(missing_sections)} sections were not found.")
            ats_improvements.append(f"Add dedicated section headers for: {', '.join(missing_sections)}.")
        else:
            strengths.append("Structural Completeness: All standard resume sections are correctly mapped.")
            
        # 3. Job Match specific feedback
        missing_skills = match_data.get('missing_skills', [])
        if missing_skills:
            weaknesses.append(f"Skill Gap: Missing {len(missing_skills)} critical keywords listed in the job requirements.")
            immediate_improvements.append(f"Integrate key missing technologies like: {', '.join(missing_skills[:4])} naturally into your skills section.")
        else:
            strengths.append("High Skills Alignment: Exceptional coverage of keywords specified in the Job Description.")
            
        # 4. Formatting and Grammar heuristic feedback
        if not contact_status.get('linkedin') or not contact_status.get('github'):
            formatting_improvements.append("Include links to LinkedIn and GitHub in the header for easier access.")
            
        # Grammar suggestions
        grammar_improvements.append("Use strong action verbs in the past tense for previous projects (e.g. 'Initiated', 'Refactored').")
        grammar_improvements.append("Ensure capitalization of abbreviations and tech stacks (e.g., use 'SQL' instead of 'sql', 'GitHub' instead of 'github').")
        
        # 5. Extract role suggestions (centralized constants)
        role_recs = ROLE_RECOMMENDATIONS.get(predicted_role, ROLE_RECOMMENDATIONS['Software Engineer'])
        projects = role_recs['projects']
        certifications = role_recs['certifications']
        roadmap_steps = role_recs['roadmap']
        resources = role_recs.get('resources', ["LeetCode / HackerRank", "W3Schools tutorials"])
        
        # 6. Specific Priority Improvements list
        priority_improvements = []
        if missing_skills:
            priority_improvements.append({
                'priority': 'High',
                'category': 'Keywords Gap',
                'text': f"Add missing keywords: {', '.join(missing_skills[:4])}."
            })
        if not ats_data.get('metrics_detected', False):
            priority_improvements.append({
                'priority': 'High',
                'category': 'Impact Metrics',
                'text': "Add numerical figures (e.g. 'reduced latency by 30%') to your experience bullets."
            })
        if missing_sections:
            priority_improvements.append({
                'priority': 'Medium',
                'category': 'Structure',
                'text': f"Add headers for: {', '.join(missing_sections)}."
            })
        if not contact_status.get('github') and predicted_role in ['Software Engineer', 'Machine Learning Engineer', 'Data Engineer']:
            priority_improvements.append({
                'priority': 'Medium',
                'category': 'Portfolio',
                'text': "Create a GitHub account and paste the link in your contact info."
            })
        priority_improvements.append({
            'priority': 'Low',
            'category': 'Aesthetic',
            'text': "Use standard fonts (Arial, Calibri) and ensure margin symmetry."
        })
        
        # 7. High Impact vs Low Effort categorization
        high_impact = [
            "Quantify project achievements with percentages or dollar values.",
            f"Integrate key tech stacks required in JD: {', '.join(missing_skills[:3]) if missing_skills else 'relevance keywords'}."
        ]
        low_effort = [
            "Add contact links (LinkedIn / GitHub / Portfolio).",
            "Change section names to standard titles like 'Experience' and 'Education'."
        ]
        
        # 8. Custom Interview Prep Questions
        interview_prep = [
            f"Walk me through a complex project on your resume that aligns with the skills of a {predicted_role}.",
            "How do you handle disagreement with stakeholders or team members during product specification?",
            f"What is your approach to learning and adopting new framework technologies (e.g. {missing_skills[0] if missing_skills else 'new tools'})?"
        ]
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "immediate_improvements": immediate_improvements,
            "ats_improvements": ats_improvements,
            "formatting_improvements": formatting_improvements,
            "grammar_improvements": grammar_improvements,
            "project_suggestions": projects,
            "certification_suggestions": certifications,
            "learning_roadmap": roadmap_steps,
            "learning_resources": resources,
            "priority_improvements": priority_improvements,
            "high_impact_suggestions": high_impact,
            "low_effort_improvements": low_effort,
            "interview_preparation": interview_prep
        }
