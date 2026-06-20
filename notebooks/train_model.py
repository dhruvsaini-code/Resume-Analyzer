import os
import pickle
import random
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

# Predefined templates and vocabulary for synthetic resume generation
ROLES = [
    "Data Scientist",
    "Data Analyst",
    "Machine Learning Engineer",
    "Data Engineer",
    "Business Analyst",
    "Software Engineer"
]

SKILLS_BY_ROLE = {
    "Data Scientist": [
        "python", "r", "pandas", "numpy", "scikit-learn", "sklearn", "statistics", "statistical modeling",
        "machine learning", "deep learning", "nlp", "natural language processing", "linear regression",
        "random forest", "clustering", "ab testing", "exploratory data analysis", "eda", "sql", "tableau"
    ],
    "Data Analyst": [
        "sql", "excel", "tableau", "power bi", "powerbi", "data cleaning", "dashboards", "reporting",
        "data visualization", "google analytics", "business intelligence", "bi", "metrics", "kpi",
        "pandas", "numpy", "statistics", "data warehousing", "spreadsheet"
    ],
    "Machine Learning Engineer": [
        "python", "pytorch", "tensorflow", "keras", "xgboost", "deep learning", "neural networks",
        "mlops", "model deployment", "docker", "kubernetes", "fastapi", "git", "ci/cd", "computer vision",
        "transformers", "bert", "gpu", "model optimization", "aws", "gcp"
    ],
    "Data Engineer": [
        "sql", "python", "etl", "data pipelines", "spark", "pyspark", "hadoop", "airflow", "apache airflow",
        "data warehousing", "snowflake", "redshift", "bigquery", "kafka", "apache kafka", "scala",
        "postgresql", "nosql", "aws", "gcp", "data lake", "dbms"
    ],
    "Business Analyst": [
        "business analysis", "requirements gathering", "agile", "scrum", "jira", "confluence",
        "user stories", "use cases", "gap analysis", "stakeholder communication", "sql", "excel",
        "tableau", "process modeling", "bpm", "project management", "sdlc", "product manager"
    ],
    "Software Engineer": [
        "java", "spring boot", "javascript", "typescript", "react", "nodejs", "node.js", "c++", "c#",
        "git", "github", "rest api", "apis", "microservices", "html", "css", "docker", "unit testing",
        "databases", "sql", "system design", "data structures", "algorithms"
    ]
}

EXPERIENCE_TEMPLATES = [
    "Experienced professionals with a demonstrated history of working in the {industry} industry. Skilled in {skills}.",
    "Results-driven professional with over {years} years of experience specializing in {skills} and executing high-impact projects.",
    "Detail-oriented team player with expertise in {skills}. Proven track record of optimizing system performance and solving complex problems.",
    "Dynamic and analytical professional focusing on {skills}. Strong background in design, development, and system integration."
]

PROJECT_TEMPLATES = [
    "Led the development of a {proj_name} using {skills}, improving efficiency by {pct}%.",
    "Designed and implemented a {proj_name} leveraging {skills} to process and analyze large volumes of data.",
    "Built a secure and scalable {proj_name} using {skills}, resolving critical performance bottlenecks.",
    "Collaborated on a cross-functional project to deploy a {proj_name} with {skills}, reducing operational costs by {pct}%."
]

PROJECT_NAMES = {
    "Data Scientist": ["predictive customer churn model", "recommendation system engine", "fraud detection pipeline", "healthcare classification model"],
    "Data Analyst": ["interactive executive dashboard", "sales performance metrics reporter", "customer segmentation dashboard", "marketing ROI analysis"],
    "Machine Learning Engineer": ["distributed LLM inference API", "real-time object detection service", "automated document parsing pipeline", "reinforcement learning trading bot"],
    "Data Engineer": ["serverless ETL pipeline", "real-time clickstream data lake", "automated data migration framework", "multi-source warehouse synchronization"],
    "Business Analyst": ["agile billing system migration", "CRM software requirements specification", "operational workflow redesign", "e-commerce checkout flow optimization"],
    "Software Engineer": ["e-commerce microservices backend", "real-time collaborative task manager", "single page dashboard application", "automated API testing framework"]
}

INDUSTRIES = ["financial services", "healthcare", "technology", "e-commerce", "logistics", "telecommunications"]

def generate_synthetic_resume(role: str) -> str:
    """
    Generate a realistic resume text containing role-specific keywords.
    """
    skills = SKILLS_BY_ROLE[role]
    sampled_skills_1 = random.sample(skills, k=min(len(skills), 6))
    sampled_skills_2 = random.sample(skills, k=min(len(skills), 6))
    sampled_skills_3 = random.sample(skills, k=min(len(skills), 5))
    
    # Structure parts
    contact_header = f"Candidate Profile - {role}\nEmail: contact@candidate.com | Phone: +1 123 456 7890 | Location: San Francisco, CA\nLinkedIn: linkedin.com/in/candidate | GitHub: github.com/candidate\n\n"
    
    summary = f"SUMMARY\nProfessional seeking a career as a {role}. " + random.choice(EXPERIENCE_TEMPLATES).format(
        industry=random.choice(INDUSTRIES),
        years=random.randint(2, 10),
        skills=", ".join(sampled_skills_1)
    ) + "\n\n"
    
    skills_sec = "TECHNICAL SKILLS\n" + ", ".join(skills) + "\n\n"
    
    # 2 Projects
    proj_list = []
    for _ in range(2):
        proj_name = random.choice(PROJECT_NAMES[role])
        proj_skills = ", ".join(random.sample(skills, k=min(len(skills), 3)))
        proj_list.append(random.choice(PROJECT_TEMPLATES).format(
            proj_name=proj_name,
            skills=proj_skills,
            pct=random.randint(10, 45)
        ))
    projects = "PROJECTS\n- " + "\n- ".join(proj_list) + "\n\n"
    
    # Education & Certifications
    edu = f"EDUCATION\nBachelor of Science in Computer Science / Information Systems\nUniversity of Technology, {random.randint(2015, 2022)}\n\n"
    certs = f"CERTIFICATIONS\nCertified {role} Specialist, AWS Certified Cloud Practitioner"
    
    return contact_header + summary + skills_sec + projects + edu + certs

def train_and_save_classifier():
    """
    Generate synthetic dataset, split, vectorize (TF-IDF), train Logistic Regression, and save.
    """
    print("Generating synthetic resume dataset...")
    data = []
    # Generate 45 resumes per category to have a decent dataset of 270 samples
    samples_per_role = 45
    for role in ROLES:
        for _ in range(samples_per_role):
            text = generate_synthetic_resume(role)
            data.append({"resume_text": text, "label": role})
            
    df = pd.DataFrame(data)
    
    # Create datasets folder if it doesn't exist
    os.makedirs("datasets", exist_ok=True)
    dataset_path = "datasets/sample_resumes.csv"
    df.to_csv(dataset_path, index=False)
    print(f"Dataset generated and saved to {dataset_path} ({len(df)} samples)")
    
    # Preprocess text (simple cleaning for TF-IDF)
    df['clean_text'] = df['resume_text'].str.lower().str.replace(r'[^a-zA-Z\s#\+]', ' ', regex=True)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        df['clean_text'], df['label'], test_size=0.2, random_state=42, stratify=df['label']
    )
    
    print("Fitting TF-IDF Vectorizer...")
    # Using ngram_range=(1, 2) to capture double-word phrases like "machine learning"
    vectorizer = TfidfVectorizer(max_features=2500, stop_words='english', ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    print("Training Logistic Regression Model...")
    classifier = LogisticRegression(C=1.0, max_iter=200, random_state=42)
    classifier.fit(X_train_vec, y_train)
    
    # Evaluate
    y_pred = classifier.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nModel training complete. Test Accuracy: {acc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save models
    os.makedirs("models", exist_ok=True)
    with open("models/tfidf_vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    with open("models/classifier.pkl", "wb") as f:
        pickle.dump(classifier, f)
    print("Vectorizer and Classifier pickled successfully in models/ directory.")

if __name__ == "__main__":
    train_and_save_classifier()
