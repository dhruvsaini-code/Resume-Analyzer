import re
from typing import Dict, Any, List
from utils.constants import ROLE_RECOMMENDATIONS, SOFT_SKILLS_LIST

class AIFeedbackSystem:
    """
    Generates structured, premium feedback, career roadmaps, and dynamic document writes
    based on resume analysis, job matching details, and predicted role category.
    """
    
    @staticmethod
    def generate_feedback(ats_data: Dict[str, Any], match_data: Dict[str, Any], predicted_role: str) -> Dict[str, Any]:
        """
        Synthesizes strengths, weaknesses, formatting/ATS fixes, certifications, roadmap,
        priority actions, interview prep questions, and advanced document generation scripts.
        """
        strengths = []
        weaknesses = []
        immediate_improvements = []
        ats_improvements = []
        formatting_improvements = []
        grammar_improvements = []
        
        # 1. Basic checks
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
            
        # Section Checks
        section_status = ats_data.get('section_status', {})
        missing_sections = [sec.replace('_', ' ').title() for sec, ok in section_status.items() if not ok]
        if missing_sections:
            weaknesses.append(f"Missing Core Sections: {', '.join(missing_sections)} sections were not found.")
            ats_improvements.append(f"Add dedicated section headers for: {', '.join(missing_sections)}.")
        else:
            strengths.append("Structural Completeness: All standard resume sections are correctly mapped.")
            
        # Job Match specific feedback
        missing_skills = match_data.get('missing_skills', [])
        matching_skills = match_data.get('matching_skills', [])
        if missing_skills:
            weaknesses.append(f"Skill Gap: Missing {len(missing_skills)} critical keywords listed in the job requirements.")
            immediate_improvements.append(f"Integrate key missing technologies like: {', '.join(missing_skills[:4])} naturally into your skills section.")
        else:
            strengths.append("High Skills Alignment: Exceptional coverage of keywords specified in the Job Description.")
            
        # Formatting and Grammar heuristic feedback
        if not contact_status.get('linkedin') or not contact_status.get('github'):
            formatting_improvements.append("Include links to LinkedIn and GitHub in the header for easier access.")
            
        # Grammar suggestions
        grammar_improvements.append("Use strong action verbs in the past tense for previous projects (e.g. 'Initiated', 'Refactored').")
        grammar_improvements.append("Ensure capitalization of abbreviations and tech stacks (e.g., use 'SQL' instead of 'sql', 'GitHub' instead of 'github').")
        
        # Extract role suggestions (centralized constants)
        role_recs = ROLE_RECOMMENDATIONS.get(predicted_role, ROLE_RECOMMENDATIONS['Software Engineer'])
        projects = role_recs['projects']
        certifications = role_recs['certifications']
        roadmap_steps = role_recs['roadmap']
        resources = role_recs.get('resources', ["LeetCode / HackerRank", "W3Schools tutorials"])
        
        # Priority list
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
        
        priority_improvements.append({
            'priority': 'Low',
            'category': 'Aesthetic',
            'text': "Use standard fonts (Arial, Calibri) and ensure margin symmetry."
        })
        
        high_impact = [
            "Quantify project achievements with percentages or dollar values.",
            f"Integrate key tech stacks required in JD: {', '.join(missing_skills[:3]) if missing_skills else 'relevance keywords'}."
        ]
        low_effort = [
            "Add contact links (LinkedIn / GitHub / Portfolio).",
            "Change section names to standard titles like 'Experience' and 'Education'."
        ]
        
        interview_prep = [
            f"Walk me through a complex project on your resume that aligns with the skills of a {predicted_role}.",
            "How do you handle disagreement with stakeholders or team members during product specification?",
            f"What is your approach to learning and adopting new framework technologies (e.g. {missing_skills[0] if missing_skills else 'new tools'})?"
        ]

        # --- ADVANCED AI FEATURES GENERATION ---
        # 1. Professional Summary Generator
        skills_snippet = ", ".join(matching_skills[:3]) if matching_skills else "software engineering, modern cloud frameworks, and databases"
        years_exp = ats_data.get('total_years_exp', 3.0)
        career_stage = "Senior Specialist" if years_exp > 7 else ("Mid-Level Professional" if years_exp > 3 else "Entry-Level Specialist")
        summary_gen = f"Results-driven {predicted_role} and {career_stage} with approximately {years_exp} years of hands-on experience specializing in {skills_snippet}. Proven track record of spearheading project design, writing scalable code bases, and optimizing data processing pipelines. Adept at leveraging automated tests and standardizing workflow layouts to deliver enterprise-grade performance."

        # 2. Career Highlights
        highlights = [
            f"Successfully architected code solutions and frameworks utilizing: {', '.join(matching_skills[:4]) if matching_skills else 'Python, SQL, Cloud infrastructures'}.",
            f"Engineered workflows over a {years_exp}-year career timeline, demonstrating technical depth and adaptive learning.",
            "Spearheaded software project deployments, reducing complexity while establishing performance metrics and analytical audits."
        ]

        # 3. Skill Gap Analysis details
        gap_analysis = f"Your profile covers a solid spectrum of tools. However, the job requirements explicitly ask for {', '.join(missing_skills[:4]) if missing_skills else 'additional frameworks'}. Learning these will bridge the compatibility index from {ats_data.get('overall_score', 75)}% to over 95%."

        # 4. Career Growth Suggestions
        if years_exp < 3:
            growth_suggestions = [
                "Focus on building 2-3 end-to-end projects demonstrating complete deployment lifecycles.",
                "Acquire basic certifications (AWS Cloud Practitioner, Azure Fundamentals) to validate cloud concepts."
            ]
        elif years_exp < 7:
            growth_suggestions = [
                "Seek mentorship roles or lead small agile project modules in your current position.",
                "Focus on advanced architecture patterns: system design, caching databases, and distributed ETL loads."
            ]
        else:
            growth_suggestions = [
                "Transition into strategic architecture, technical leadership, and engineering management roles.",
                "Author technical blogs, speak at conferences, or contribute to open-source foundation modules."
            ]

        # 5. Resume Rewrite Suggestions (Section-by-Section)
        rewrite_suggestions = {
            "Summary": "Revise summary to highlight measurable business metrics (e.g. 'boosted pipeline efficiency by 25%') rather than qualitative adjectives.",
            "Experience": "Restructure job points to start with unique action verbs and follow the XYZ formula.",
            "Skills": "Group technologies into subcategories (e.g., 'Languages', 'Frameworks', 'Databases') to avoid cluttered lists."
        }

        # 6. Bullet Point Improvements (XYZ formula rewrites)
        bullet_improvements = [
            {
                "original": "Worked on the backend database and added new features to speed up code query times.",
                "improved": f"Optimized SQL query parameters and indices for the core relational database, reducing data fetch latency by 32% and improving concurrent connection throughput."
            },
            {
                "original": "Helped the team deploy models and build dashboard reports for executive staff.",
                "improved": f"Co-developed and launched automated deployment pipelines with Docker and Jenkins, slashing release cycle times by 40% and deploying interactive executive dashboards."
            }
        ]

        # 7. Achievement Rewriting
        achievement_rewriting = [
            {
                "original": "Got first place in the internal code challenge.",
                "improved": "Awarded 1st place out of 80+ engineers in the annual Hackathon for designing a serverless data ingestion prototype."
            }
        ]

        # 8. Grammar Improvements details
        grammar_improvements_detailed = [
            {
                "issue": "Frequent passive phrasing (e.g. 'code was updated by me').",
                "fix": "Rephrase to active voice: 'Refactored backend codebase to support async requests'."
            }
        ]

        # 9. Action Verb Suggestions
        verb_suggestions = {
            "worked": ["Architected", "Spearheaded", "Constructed", "Orchestrated"],
            "helped": ["Collaborated", "Facilitated", "Empowered", "Supported"],
            "made": ["Engineered", "Pioneered", "Implemented", "Devised"]
        }

        # 10. Document Generators
        headline_gen = [
            f"{predicted_role} | Specialized in {skills_snippet} | Building Scalable Enterprise Apps",
            f"Solutions-Oriented {predicted_role} | {years_exp}+ Years Experience | Expert in Cloud & Microservices",
            f"Technical Lead & {predicted_role} | Spearheading High-Performance Backend & Database Optimizations"
        ]

        bio_gen = f"Professional profile bio: A passionate technical expert with {years_exp} years of history in {predicted_role} domains. Known for delivering robust backend systems, accelerating data processes, and mentoring software developers. Always learning new technologies and engineering high-impact SaaS platforms."

        linkedin_opt = [
            "Headline: Use a formula like 'Role | Key Skills | Business Value' instead of just your job title.",
            "About Section: Write in the first person, highlighting your technical journey, core tech stacks, and career milestones.",
            "Skills Section: Add at least 15 technical skills and pin the top 3 corresponding to your primary job focus.",
            "Featured Section: Link to your GitHub, a live portfolio website, or key project slides."
        ]

        # Email templates
        cover_letter = f"""Subject: Application for {predicted_role} role at [Company Name]

Dear [Hiring Manager Name],

I am writing to express my strong interest in the {predicted_role} position at [Company Name]. With over {years_exp} years of experience building scalable backend software and specializing in technologies like {skills_snippet}, I am confident in my ability to immediately add value to your engineering team.

In my previous roles, I have:
- Designed and deployed robust system architectures.
- Improved database query performance, reducing lag times.
- Collaborated across teams to standardise codebases.

I admire [Company Name]'s focus on product innovation and would love the opportunity to discuss how my technical skills align with your engineering goals. Thank you for your time and consideration.

Sincerely,
[Your Name]
{contact_status.get('email', 'candidate@email.com')} | {contact_status.get('phone', 'Phone Number')}
"""

        cold_email = f"""Subject: Synergies in {predicted_role} Engineering - [Your Name]

Dear [Manager Name],

I recently came across your team's work on [Product or Initiative] and was highly impressed by your approach to scalability. 

As a {predicted_role} with {years_exp} years of history specializing in {skills_snippet}, I have spent my career solving similar challenges. In my previous position, I engineered deployment pipelines that reduced deployment overhead.

I wanted to reach out to see if you have any open roles or contract needs for an engineer of my profile. I'd love to chat briefly next week.

Best regards,
[Your Name]
LinkedIn: {contact_status.get('linkedin', 'linkedin.com/in/profile')}
"""

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
            "interview_preparation": interview_prep,
            
            # Expanded AI items
            "professional_summary": summary_gen,
            "career_highlights": highlights,
            "skill_gap_analysis": gap_analysis,
            "career_growth_suggestions": growth_suggestions,
            "resume_rewrite_suggestions": rewrite_suggestions,
            "bullet_point_improvements": bullet_improvements,
            "achievement_rewriting": achievement_rewriting,
            "grammar_improvements_detailed": grammar_improvements_detailed,
            "action_verb_suggestions": verb_suggestions,
            
            # Document outputs
            "headline_suggestions": headline_gen,
            "bio_suggestion": bio_gen,
            "linkedin_optimization": linkedin_opt,
            "cover_letter_template": cover_letter,
            "cold_email_template": cold_email
        }
