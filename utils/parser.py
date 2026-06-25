import re
import spacy
import nltk
import logging
from typing import Dict, List, Any, Optional

# Import constants
from utils.constants import SKILL_CATEGORIES, SECTION_KEYWORDS, SOFT_SKILLS_LIST, DEGREE_LEVELS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure NLTK resources are available
for package in ['stopwords', 'punkt']:
    try:
        nltk.data.find(f'corpora/{package}' if package == 'stopwords' else f'tokenizers/{package}')
    except LookupError:
        nltk.download(package, quiet=True)

# Ensure spaCy model is loaded
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.info("Downloading spaCy model 'en_core_web_sm'...")
    import subprocess
    import sys
    try:
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], stdout=subprocess.DEVNULL)
        nlp = spacy.load("en_core_web_sm")
    except Exception as e:
        logger.error(f"Failed to download spaCy model: {e}. Falling back to basic parsing.")
        nlp = None


class ResumeParser:
    """
    Advanced Parser to segment the resume into 14+ sections and extract contact details,
    skills, location, name, and chronological experience dates.
    """
    
    def __init__(self, text: str):
        self.text = text
        self.clean_text = self._preprocess_text(text)
        
    def _preprocess_text(self, text: str) -> str:
        """
        Cleans extra spacing and carriage returns, keeping structure readable.
        """
        if not text:
            return ""
        lines = [line.strip() for line in text.split('\n')]
        return "\n".join([line for line in lines if line])

    def extract_contact_info(self) -> Dict[str, Optional[str]]:
        """
        Extract email, phone number, LinkedIn, GitHub, Location, and Portfolio URL.
        """
        info = {
            'name': None,
            'email': None,
            'phone': None,
            'linkedin': None,
            'github': None,
            'portfolio': None,
            'location': None
        }
        
        # 1. Extract Email
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        emails = re.findall(email_pattern, self.text)
        if emails:
            info['email'] = emails[0].strip()
            
        # 2. Extract Phone (supports local, international, spaces, dots, dashes, parentheses)
        phone_pattern = r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        phones = re.findall(phone_pattern, self.text)
        if phones:
            info['phone'] = phones[0].strip()
            
        # 3. Extract LinkedIn
        linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+'
        linkedins = re.findall(linkedin_pattern, self.text, re.IGNORECASE)
        if linkedins:
            info['linkedin'] = linkedins[0].strip()
            
        # 4. Extract GitHub
        github_pattern = r'(?:https?://)?(?:www\.)?github\.com/[\w\-]+'
        githubs = re.findall(github_pattern, self.text, re.IGNORECASE)
        if githubs:
            info['github'] = githubs[0].strip()
            
        # 5. Extract Portfolio (Personal URL that isn't GitHub or LinkedIn)
        url_pattern = r'(?:https?://)?(?:www\.)?[\w\-\.]+\.[a-zA-Z]{2,6}(?:/[\w\-\./\?%&=]*)?'
        urls = re.findall(url_pattern, self.text, re.IGNORECASE)
        portfolio_urls = []
        for url in urls:
            if not any(domain in url.lower() for domain in ['linkedin.com', 'github.com', 'email.com', 'candidate.com', 'w3.org']):
                portfolio_urls.append(url.strip())
        if portfolio_urls:
            info['portfolio'] = portfolio_urls[0]
            
        # 6. Extract Location (looks for City, ST or City, Country or zipcodes near header)
        loc_patterns = [
            r'\b[A-Z][a-zA-Z\s]{1,19},\s*[A-Z]{2}\b',                     # SF, CA or Dallas, TX
            r'\b[A-Z][a-zA-Z\s]{1,19},\s*[A-Z][a-zA-Z\s]{2,14}\b',         # London, United Kingdom
            r'\b[A-Za-z\s]{3,20}\s+\d{5}(?:-\d{4})?\b'                      # Austin 78701
        ]
        for pat in loc_patterns:
            locs = re.findall(pat, self.text[:600]) # Look near header
            if locs:
                # filter out false positives like sections or candidate name
                clean_loc = locs[0].strip()
                if not any(kw in clean_loc.lower() for kw in ['resume', 'curriculum', 'email', 'phone', 'portfolio']):
                    info['location'] = clean_loc
                    break
        
        # 7. Extract Name
        info['name'] = self._extract_name()
        
        return info

    def _extract_name(self) -> str:
        """
        Extract Name using NER or fallback layout heuristics.
        """
        lines = [l.strip() for l in self.text.split('\n') if l.strip()]
        if not lines:
            return "Candidate Name"
            
        # Inspect top 5 lines for name
        candidate_lines = lines[:5]
        
        if nlp:
            for line in candidate_lines:
                if "@" in line or "linkedin.com" in line or "github.com" in line or len(line) > 50:
                    continue
                doc = nlp(line)
                for ent in doc.ents:
                    if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
                        return ent.text.strip()
                        
        # Fallback heuristics
        for line in candidate_lines:
            if re.search(r'\d', line): # Skip if it contains numbers
                continue
            if "@" in line or "http" in line or "|" in line or "/" in line or "\\" in line:
                continue
            # Skip if it is a section header
            if any(h in line.lower() for headers in SECTION_KEYWORDS.values() for h in headers):
                continue
            words = line.split()
            if 2 <= len(words) <= 4:
                return line
                
        return lines[0]

    def extract_skills(self) -> Dict[str, List[str]]:
        """
        Extract categorized skills based on pattern matching.
        """
        extracted_skills = {cat: [] for cat in SKILL_CATEGORIES.keys()}
        lowercased_text = self.text.lower()
        
        for category, skills in SKILL_CATEGORIES.items():
            for skill in skills:
                # Build regex based on length of skill to prevent false matches (e.g. 'R' matching 'are')
                clean_skill = skill.replace('\\', '')
                if len(clean_skill) <= 3:
                    pattern = rf'\b{skill}\b'
                else:
                    pattern = rf'\b{skill}\b'
                
                # Check C++ & C# manually to handle regex boundaries correctly
                if skill == 'c\\+\\+':
                    pattern = r'(?:\b|(?<=[\s,]))c\+\+(?:\b|(?=[\s,]))'
                elif skill == 'c#':
                    pattern = r'(?:\b|(?<=[\s,]))c#(?:\b|(?=[\s,]))'
                
                if re.search(pattern, lowercased_text):
                    extracted_skills[category].append(clean_skill.upper() if len(clean_skill) <= 3 else clean_skill.title())
                    
        return extracted_skills

    def segment_sections(self) -> Dict[str, str]:
        """
        Segments the resume text into 14+ distinct sections.
        """
        sections = {sec: '' for sec in SECTION_KEYWORDS.keys()}
        sections['other'] = ''
        
        lines = self.text.split('\n')
        current_section = 'other'
        section_content = {sec: [] for sec in sections.keys()}
        
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
                
            # Check if this line is a section header
            header_detected = False
            for sec, keywords in SECTION_KEYWORDS.items():
                for kw in keywords:
                    # Look for exact or close matches (short lines containing or starting with keyword)
                    if len(line_clean) < 40 and (
                        line_clean.lower() == kw or 
                        line_clean.lower().startswith(kw + " ") or 
                        line_clean.lower().endswith(" " + kw) or
                        re.match(rf'^[^a-zA-Z]*{re.escape(kw)}[^a-zA-Z]*$', line_clean.lower())
                    ):
                        current_section = sec
                        header_detected = True
                        break
                if header_detected:
                    break
            
            if not header_detected:
                section_content[current_section].append(line_clean)
                
        # Join lines for each section
        for sec in sections.keys():
            sections[sec] = "\n".join(section_content[sec]).strip()
            
        return sections

    def parse_experience_timeline(self) -> List[Dict[str, Any]]:
        """
        Scans the experience section to extract dates, job titles, and companies.
        Returns a list of roles with start and end years for timeline visualizations.
        """
        exp_text = self.segment_sections().get('experience', '')
        if not exp_text:
            return []
            
        lines = exp_text.split('\n')
        timeline = []
        
        # Regex to find date ranges like 2018 - 2021, Jan 2020 - Present, etc.
        # Captures years or 'present'
        date_pattern = r'\b(19|20\d{2})\b\s*[-–—to\s]+\s*\b(present|current|19|20\d{2})\b'
        month_date_pattern = r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*(19|20\d{2})\b\s*[-–—to\s]+\s*(Present|Current|\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*(19|20\d{2})\b)'
        
        current_year = 2026 # Context local time is 2026
        
        for i, line in enumerate(lines):
            # Find date match
            match = re.search(date_pattern, line, re.IGNORECASE)
            m_match = re.search(month_date_pattern, line, re.IGNORECASE)
            
            if match or m_match:
                start_year = None
                end_year = None
                
                # Extract years
                years = re.findall(r'\b(19|20\d{2})\b', line)
                if len(years) >= 2:
                    start_year = int(years[0])
                    end_year = int(years[1])
                elif len(years) == 1:
                    start_year = int(years[0])
                    if re.search(r'present|current', line, re.IGNORECASE):
                        end_year = current_year
                    else:
                        end_year = start_year
                else:
                    continue
                
                # Heuristics for Title & Company
                # Usually on the same line, or the line above
                context_line = line
                if len(line) < 30 and i > 0:
                    # Date is probably on its own line, take the title from the line above
                    title_candidate = lines[i - 1].strip()
                else:
                    title_candidate = re.sub(date_pattern, '', line).strip()
                    title_candidate = re.sub(month_date_pattern, '', title_candidate).strip()
                    
                # Clean up title candidate (split on commas, pipes, dashes)
                parts = [p.strip() for p in re.split(r'[,|•\-\(]', title_candidate) if p.strip()]
                role = parts[0] if parts else "Professional Role"
                company = parts[1] if len(parts) > 1 else "Corporation"
                
                # Strip out common debris
                role = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', role).strip()
                company = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', company).strip()
                
                duration = max(0.5, end_year - start_year)
                
                timeline.append({
                    'role': role,
                    'company': company,
                    'start_year': start_year,
                    'end_year': end_year,
                    'end_year_label': 'Present' if re.search(r'present|current', line, re.IGNORECASE) else str(end_year),
                    'duration_years': round(duration, 1)
                })
                
        # Fallback if no chronological ranges found but we have experience text
        if not timeline:
            timeline.append({
                'role': 'Professional Experience',
                'company': 'Company',
                'start_year': current_year - 3,
                'end_year': current_year,
                'end_year_label': 'Present',
                'duration_years': 3.0
            })
            
        return timeline

    def get_full_analysis(self) -> Dict[str, Any]:
        """
        Aggregated parsed data.
        """
        contact = self.extract_contact_info()
        skills = self.extract_skills()
        sections = self.segment_sections()
        timeline = self.parse_experience_timeline()
        
        all_skills = []
        for s_list in skills.values():
            all_skills.extend(s_list)
            
        return {
            'contact': contact,
            'skills': skills,
            'all_skills': list(set(all_skills)),
            'sections': sections,
            'timeline': timeline,
            'text_length': len(self.text)
        }
