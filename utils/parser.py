import re
import spacy
import nltk
import logging
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure NLTK resources are available
for package in ['stopwords', 'punkt']:
    try:
        nltk.data.find(f'corpora/{package}' if package == 'stopwords' else f'tokenizers/{package}')
    except LookupError:
        nltk.download(package, quiet=True)

# Ensure SpaCy model is loaded
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

# Define Skill Categories
SKILL_CATEGORIES = {
    'programming': [
        'python', 'r', 'java', 'c\\+\\+', 'c#', 'c', 'javascript', 'typescript', 'go', 'golang', 
        'scala', 'rust', 'ruby', 'php', 'bash', 'shell', 'html', 'css', 'perl', 'swift', 'kotlin'
    ],
    'data_science': [
        'pandas', 'numpy', 'scipy', 'data analysis', 'data wrangling', 'exploratory data analysis', 
        'eda', 'statistics', 'statistical modeling', 'probability', 'hypothesis testing', 
        'ab testing', 'regression analysis', 'time series', 'feature engineering', 'data mining'
    ],
    'machine_learning': [
        'scikit-learn', 'sklearn', 'tensorflow', 'keras', 'pytorch', 'xgboost', 'lightgbm', 'catboost',
        'machine learning', 'deep learning', 'nlp', 'natural language processing', 'computer vision', 
        'cv', 'neural networks', 'cnn', 'rnn', 'lstm', 'transformers', 'bert', 'gpt', 'llm', 'reinforcement learning',
        'random forest', 'gradient boosting', 'decision trees', 'svm', 'clustering', 'kmeans', 'unsupervised learning',
        'supervised learning'
    ],
    'visualization': [
        'matplotlib', 'seaborn', 'plotly', 'bokeh', 'ggplot', 'tableau', 'power bi', 'powerbi', 
        'd3.js', 'd3', 'looker', 'superset', 'dashboarding', 'dash'
    ],
    'database': [
        'sql', 'mysql', 'postgresql', 'postgres', 'sqlite', 'mongodb', 'redis', 'cassandra', 
        'dynamodb', 'mariadb', 'oracle', 'neo4j', 'nosql', 'hive', 'impala', 'snowflake'
    ],
    'cloud': [
        'aws', 'amazon web services', 'gcp', 'google cloud', 'azure', 'microsoft azure', 
        'docker', 'kubernetes', 'k8s', 'jenkins', 'git', 'github', 'gitlab', 'ci/cd', 'airflow', 
        'presto', 'spark', 'pyspark', 'hadoop', 'mapreduce', 'databricks', 'terraform', 'ansible'
    ]
}

# Define Section Header Mappings
SECTION_KEYWORDS = {
    'education': [
        'education', 'academic background', 'academic profile', 'qualifications', 
        'academic credentials', 'academic training', 'degrees'
    ],
    'experience': [
        'experience', 'work experience', 'professional experience', 'employment history', 
        'work history', 'professional background', 'career history', 'employment'
    ],
    'projects': [
        'projects', 'academic projects', 'personal projects', 'key projects', 
        'technical projects', 'major projects'
    ],
    'certifications': [
        'certifications', 'certificates', 'licenses', 'credentials', 'courses', 
        'professional certifications', 'accreditations'
    ]
}

class ResumeParser:
    """
    Parser class to extract contact info, skills, education, experience, and projects.
    """
    
    def __init__(self, text: str):
        self.text = text
        self.clean_text = self._preprocess_text(text)
        
    def _preprocess_text(self, text: str) -> str:
        """
        Basic preprocessing: clean extra spacing, keeping layout readable.
        """
        if not text:
            return ""
        # Replace multiple spaces with single space, keep lines
        lines = [line.strip() for line in text.split('\n')]
        return "\n".join([line for line in lines if line])

    def extract_contact_info(self) -> Dict[str, Optional[str]]:
        """
        Extract email, phone number, LinkedIn, GitHub, and Name.
        """
        info = {
            'name': None,
            'email': None,
            'phone': None,
            'linkedin': None,
            'github': None
        }
        
        # 1. Extract Email
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        emails = re.findall(email_pattern, self.text)
        if emails:
            info['email'] = emails[0].strip()
            
        # 2. Extract Phone (various formats: +1-123-456-7890, (123) 456 7890, etc.)
        phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
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
            
        # 5. Extract Name
        info['name'] = self._extract_name()
        
        return info

    def _extract_name(self) -> str:
        """
        Extract Name using NER or fallback layout heuristics.
        """
        lines = [l.strip() for l in self.text.split('\n') if l.strip()]
        if not lines:
            return "Candidate Name"
            
        # Look at the first 5 lines for name
        candidate_lines = lines[:5]
        
        # If spaCy NER is available, check for PERSON entities in the top lines
        if nlp:
            for line in candidate_lines:
                # Skip lines that are likely links or emails
                if "@" in line or "linkedin.com" in line or "github.com" in line or len(line) > 50:
                    continue
                doc = nlp(line)
                for ent in doc.ents:
                    if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
                        return ent.text.strip()
                        
        # Fallback heuristic: take the first line if it looks like a name
        # (usually short, doesn't contain digits or common resume headers/emails)
        for line in candidate_lines:
            if re.search(r'\d', line): # Skip if it contains numbers (likely address/phone)
                continue
            if "@" in line or "http" in line or "|" in line or "/" in line:
                continue
            # Skip if it is a known resume section header
            if any(h in line.lower() for headers in SECTION_KEYWORDS.values() for h in headers):
                continue
            words = line.split()
            if 2 <= len(words) <= 4:
                return line
                
        # Ultimate fallback
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
                if len(skill.replace('\\', '')) <= 3:
                    pattern = rf'\b{skill}\b'
                else:
                    pattern = rf'\b{skill}\b'  # Standard boundary match
                
                # Check for c++ separately since regex boundary with special chars can fail
                if skill == 'c\\+\\+':
                    pattern = r'(?:\b|(?<=[\s,]))c\+\+(?:\b|(?=[\s,]))'
                elif skill == 'c#':
                    pattern = r'(?:\b|(?<=[\s,]))c#(?:\b|(?=[\s,]))'
                
                if re.search(pattern, lowercased_text):
                    # Save clean skill name (without regex escapes)
                    clean_skill = skill.replace('\\', '')
                    extracted_skills[category].append(clean_skill.upper() if len(clean_skill) <= 3 else clean_skill.title())
                    
        return extracted_skills

    def segment_sections(self) -> Dict[str, str]:
        """
        Segments the resume text into distinct sections.
        """
        sections = {
            'education': '',
            'experience': '',
            'projects': '',
            'certifications': '',
            'other': ''
        }
        
        lines = self.text.split('\n')
        current_section = 'other'
        section_content = {sec: [] for sec in sections.keys()}
        
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
                
            # Check if this line matches any section header
            header_detected = False
            for sec, keywords in SECTION_KEYWORDS.items():
                for kw in keywords:
                    # Look for exact or close matches (e.g. line is exactly the header or starts with it)
                    if len(line_clean) < 30 and (
                        line_clean.lower() == kw or 
                        line_clean.lower().startswith(kw + " ") or 
                        line_clean.lower().endswith(" " + kw)
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

    def get_full_analysis(self) -> Dict[str, Any]:
        """
        Helper method to get all parsed information.
        """
        contact = self.extract_contact_info()
        skills = self.extract_skills()
        sections = self.segment_sections()
        
        all_skills = []
        for s_list in skills.values():
            all_skills.extend(s_list)
            
        return {
            'contact': contact,
            'skills': skills,
            'all_skills': list(set(all_skills)),
            'sections': sections,
            'text_length': len(self.text)
        }
