import re
import nltk
from typing import Dict, Any, List
from utils.parser import ResumeParser
from utils.constants import ACTION_VERBS, LEADERSHIP_VERBS, SOFT_SKILLS_LIST, DEGREE_LEVELS

def count_syllables(word: str) -> int:
    """
    Heuristically counts syllables in a word.
    """
    word = word.lower().strip()
    if not word:
        return 0
    
    # Trim punctuation
    word = re.sub(r'[^a-z]', '', word)
    if not word:
        return 0
        
    vowels = "aeiouy"
    count = 0
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
            
    if word.endswith("e"):
        count -= 1
    # Adjust for common suffixes
    if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
        count += 1
    if count == 0:
        count = 1
    return count

class ResumeAnalyticsEngine:
    """
    Computes 20 visual score indicators assessing structure, syntax, impact, and content quality.
    """
    
    @staticmethod
    def calculate_metrics(parser: ResumeParser, classifier_confidence: float = 0.0) -> Dict[str, Any]:
        analysis = parser.get_full_analysis()
        text = parser.text
        sections = analysis['sections']
        contact = analysis['contact']
        all_skills = analysis['all_skills']
        timeline = analysis['timeline']
        
        words = [w for w in re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())]
        word_count = len(words)
        
        # Split text into sentences using nltk
        try:
            sentences = nltk.sent_tokenize(text)
        except Exception:
            # Fallback sentence splitter
            sentences = [s.strip() for s in re.split(r'[.!?]\s+', text) if s.strip()]
        sentence_count = max(1, len(sentences))
        
        # 1. Readability Score (Flesch Reading Ease)
        total_syllables = sum(count_syllables(w) for w in words)
        if word_count > 0:
            asl = word_count / sentence_count  # Average sentence length
            asw = total_syllables / word_count # Average syllables per word
            # Flesch Reading Ease Formula
            flesch_score = 206.835 - (1.015 * asl) - (84.6 * asw)
            readability_score = max(0.0, min(100.0, flesch_score))
        else:
            readability_score = 0.0
            
        # 2. Grammar Score (Heuristic checks)
        # Scan for duplicate words (e.g. "the the"), passive voice ("was created by", "were designed by"),
        # and checking capitalization at start of lines.
        grammar_deductions = 0
        
        # Duplicate words check
        dups = re.findall(r'\b([a-z]+)\s+\1\b', text.lower())
        grammar_deductions += len(dups) * 5
        
        # Passive voice count
        passive_markers = re.findall(r'\b(?:am|is|are|was|were|be|been|being)\s+[a-z]+ed\b', text.lower())
        grammar_deductions += len(passive_markers) * 2
        
        # Check start-of-sentence capitalization
        for s in sentences[:15]: # Look at first 15 sentences to avoid scanning entire huge text
            if s and s[0].islower():
                grammar_deductions += 3
                
        grammar_score = max(50.0, min(100.0, 100.0 - grammar_deductions))
        
        # 3. Action Verb Score (Count density of active verbs)
        action_verb_count = 0
        for verb in ACTION_VERBS:
            # Match word boundary
            matches = re.findall(rf'\b{verb}\b', text.lower())
            action_verb_count += len(matches)
        # Target: at least 15 action verbs for a high score
        action_verb_score = min(100.0, (action_verb_count / 15.0) * 100.0)
        
        # 4. Impact Score (percentage of lines with metrics: counts, $, % or impact terms)
        impact_lines = 0
        success_keywords = ['saved', 'optimized', 'achieved', 'increased', 'decreased', 'delivered', 'revenue', 'profit', 'scale', 'efficiency']
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines:
            has_metric = bool(re.search(r'\b\d+(?:\.\d+)?%|\$\d+|\b(?:million|billion|k)\b', line.lower()))
            has_success = any(sk in line.lower() for sk in success_keywords)
            if has_metric or has_success:
                impact_lines += 1
        
        total_lines = max(1, len(lines))
        impact_ratio = impact_lines / total_lines
        impact_score = min(100.0, (impact_ratio / 0.25) * 100.0) # 25% of lines containing metrics is a perfect score
        
        # 5. Resume Density Score
        # Word density: sweet spot is 12-18 words per line on average. Too dense or too sparse gets penalized.
        avg_words_per_line = word_count / total_lines if total_lines > 0 else 0
        if 10 <= avg_words_per_line <= 20:
            density_score = 100.0
        elif avg_words_per_line < 10:
            density_score = max(40.0, (avg_words_per_line / 10.0) * 100.0)
        else:
            density_score = max(40.0, 100.0 - (avg_words_per_line - 20) * 4)
            
        # 6. Keyword Density
        # Ratio of tech keywords to overall words
        keyword_density_ratio = len(all_skills) / max(100, word_count)
        # Target: 5% to 15% keyword density
        if 0.04 <= keyword_density_ratio <= 0.15:
            keyword_density_score = 100.0
        elif keyword_density_ratio < 0.04:
            keyword_density_score = (keyword_density_ratio / 0.04) * 100.0
        else:
            keyword_density_score = max(50.0, 100.0 - (keyword_density_ratio - 0.15) * 200)
            
        # 7. Resume Completeness
        # Count present sections (out of 14 sections)
        sections_present = [sec for sec, val in sections.items() if len(val.strip()) > 30 and sec != 'other']
        # We check 13 key section types (excluding 'other')
        completeness_score = (len(sections_present) / 13.0) * 100.0
        completeness_score = min(100.0, completeness_score * 1.5) # Scale so that 8 sections is 100% complete
        
        # 8. ATS Compatibility
        # Checks formatting rules, bullets, file lengths, contact details
        ats_checks = 0
        if bool(re.search(r'[-*•►▪|]', text)):
            ats_checks += 25
        if 150 <= word_count <= 800:
            ats_checks += 25
        if contact['email'] and contact['phone']:
            ats_checks += 25
        # Penalize tables indicators in raw text (like many | separators)
        if text.count('|') < 10:
            ats_checks += 25
        ats_compatibility_score = ats_checks
        
        # 9. Section Quality
        # Assess average length and quality of Experience, Education, Projects
        sec_quality_val = 0
        core_secs = ['experience', 'education', 'projects']
        for s in core_secs:
            content = sections.get(s, '')
            if len(content.strip()) > 150:
                sec_quality_val += 33.3
            elif len(content.strip()) > 50:
                sec_quality_val += 15.0
        section_quality_score = min(100.0, sec_quality_val)
        
        # 10. Formatting Score
        # Check formatting consistency, bullets, spacing
        format_checks = 0
        if bool(re.search(r'•|▪|►', text)):
            format_checks += 40
        if '\n\n\n' not in text: # No huge empty line gaps
            format_checks += 30
        if word_count > 150:
            format_checks += 30
        formatting_score = format_checks
        
        # 11. Experience Score
        # Calculate years of experience from timeline and quality of text
        total_years = sum(t.get('duration_years', 0) for t in timeline)
        # 10 years experience = 100% score
        experience_score = min(100.0, (total_years / 10.0) * 100.0)
        if not timeline:
            experience_score = 30.0 # Entry-level fallback
            
        # 12. Project Score
        # Based on length of projects section and keywords
        proj_text = sections.get('projects', '')
        if len(proj_text.strip()) > 200:
            project_score = 100.0
        elif len(proj_text.strip()) > 50:
            project_score = 70.0
        else:
            project_score = 20.0
            
        # 13. Education Score
        # Check for degree keywords in education section
        edu_text = sections.get('education', '').lower()
        edu_score = 20.0
        for deg, keywords in DEGREE_LEVELS.items():
            if any(kw in edu_text for kw in keywords):
                if deg == 'phd':
                    edu_score = 100.0
                elif deg == 'master':
                    edu_score = 90.0
                elif deg == 'bachelor':
                    edu_score = 80.0
                break
        if edu_text and edu_score == 20.0:
            edu_score = 50.0 # Some school text found
        education_score = edu_score
        
        # 14. Certification Score
        # Count certifications found
        cert_text = sections.get('certifications', '').lower()
        cert_count = len(re.findall(r'certified|certification|certificate|license', cert_text))
        certification_score = min(100.0, 30.0 + (cert_count * 25.0)) if cert_text else 20.0
        
        # 15. Leadership Score
        # Check for leadership action verbs
        leadership_count = 0
        for l_verb in LEADERSHIP_VERBS:
            matches = re.findall(rf'\b{l_verb}\b', text.lower())
            leadership_count += len(matches)
        leadership_score = min(100.0, (leadership_count / 5.0) * 100.0)
        
        # 16. Technical Score
        # Scales based on unique tech skills count
        tech_skills_count = len(all_skills)
        technical_score = min(100.0, (tech_skills_count / 12.0) * 100.0)
        
        # 17. Soft Skills Score
        # Search for soft skills in text
        soft_skills_found = 0
        for sk in SOFT_SKILLS_LIST:
            if sk in text.lower():
                soft_skills_found += 1
        soft_skills_score = min(100.0, (soft_skills_found / 4.0) * 100.0)
        
        # 18. Communication Score
        # Average of Readability, Grammar, Formatting
        communication_score = (readability_score + grammar_score + formatting_score) / 3.0
        
        # 19. Confidence Score
        # Classifier prediction confidence
        confidence_score = classifier_confidence if classifier_confidence > 0 else 75.0
        
        # 20. Overall Resume Rating
        # Weighted average of components
        weights = {
            'ats_compatibility': 0.15,
            'technical': 0.15,
            'experience': 0.10,
            'projects': 0.10,
            'education': 0.05,
            'certifications': 0.05,
            'completeness': 0.10,
            'impact': 0.10,
            'communication': 0.10,
            'leadership': 0.10
        }
        
        weighted_sum = (
            ats_compatibility_score * weights['ats_compatibility'] +
            technical_score * weights['technical'] +
            experience_score * weights['experience'] +
            project_score * weights['projects'] +
            education_score * weights['education'] +
            certification_score * weights['certifications'] +
            completeness_score * weights['completeness'] +
            impact_score * weights['impact'] +
            communication_score * weights['communication'] +
            leadership_score * weights['leadership']
        )
        
        overall_score = round(weighted_sum, 1)
        
        # Map score to standard letter rating
        if overall_score >= 90:
            rating = "A+"
        elif overall_score >= 80:
            rating = "A"
        elif overall_score >= 70:
            rating = "B+"
        elif overall_score >= 60:
            rating = "B"
        elif overall_score >= 50:
            rating = "C"
        else:
            rating = "D"
            
        return {
            'overall_score': overall_score,
            'rating': rating,
            'scores': {
                'Readability Score': round(readability_score, 1),
                'Grammar Score': round(grammar_score, 1),
                'Action Verb Score': round(action_verb_score, 1),
                'Impact Score': round(impact_score, 1),
                'Resume Density Score': round(density_score, 1),
                'Keyword Density': round(keyword_density_score, 1),
                'Resume Completeness': round(completeness_score, 1),
                'ATS Compatibility': round(ats_compatibility_score, 1),
                'Section Quality': round(section_quality_score, 1),
                'Formatting Score': round(formatting_score, 1),
                'Experience Score': round(experience_score, 1),
                'Project Score': round(project_score, 1),
                'Education Score': round(education_score, 1),
                'Certification Score': round(certification_score, 1),
                'Leadership Score': round(leadership_score, 1),
                'Technical Score': round(technical_score, 1),
                'Soft Skills Score': round(soft_skills_score, 1),
                'Communication Score': round(communication_score, 1),
                'Confidence Score': round(confidence_score, 1)
            },
            'word_count': word_count,
            'sentence_count': sentence_count,
            'action_verb_count': action_verb_count,
            'total_years_exp': round(total_years, 1),
            'skills_count': tech_skills_count,
            'sections_found': len(sections_present)
        }
