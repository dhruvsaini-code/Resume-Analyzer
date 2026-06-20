import os
from utils.parser import ResumeParser
from utils.classifier import ResumeClassifier
from utils.analyzer import ATSAnalyzer, JobMatchAnalyzer
from utils.feedback import AIFeedbackSystem
from utils.reporter import PDFReportGenerator

print("--- Starting Pipeline Integration Test ---")
print("Verifying imports... OK")

resume_text = """
John Doe
john.doe@email.com | +1 123 456 7890 | linkedin.com/in/johndoe | github.com/johndoe

Summary
Lead Data Scientist with 5 years of experience building predictive models and machine learning pipelines.

Skills
Python, R, SQL, Pandas, NumPy, Scikit-Learn, TensorFlow, Tableau, AWS, Docker

Experience
Senior Data Scientist at TechCorp (2021-Present)
- Built a predictive customer churn model using Scikit-Learn, improving efficiency by 25%.
- Implemented data visualization dashboards in Tableau for executive reporting.

Education
Master of Science in Data Science, University of California, 2021
"""

# Test Parser
parser = ResumeParser(resume_text)
contact = parser.extract_contact_info()
print("\n[Parser Test]")
print("  Name:", contact['name'])
print("  Email:", contact['email'])
print("  Phone:", contact['phone'])
print("  LinkedIn:", contact['linkedin'])
print("  GitHub:", contact['github'])

skills = parser.extract_skills()
print("  Skills Extracted:")
for cat, sk_list in skills.items():
    if sk_list:
        print(f"    {cat.title()}: {', '.join(sk_list)}")

# Test Classifier
classifier = ResumeClassifier()
role, conf = classifier.predict_role(resume_text)
print("\n[Classifier Test]")
print(f"  Predicted Role: {role} ({conf:.2f}%)")

# Test ATS Analyzer
ats = ATSAnalyzer.calculate_ats_score(parser)
print("\n[ATS Score Test]")
print("  Overall ATS Score:", ats['overall_score'])
print("  Breakdown:", {k: v for k, v in ats.items() if 'score' in k})

# Test Job Match
jd = "We are looking for a Data Scientist with Python, SQL, AWS, and Machine Learning experience."
match = JobMatchAnalyzer.match_job_description(resume_text, jd)
print("\n[Job Match Test]")
print("  Job Match Score:", match['match_score'])
print("  Matching Skills:", match['matching_skills'])
print("  Missing Skills:", match['missing_skills'])

# Test Feedback
feedback = AIFeedbackSystem.generate_feedback(ats, match, role)
print("\n[Feedback Test]")
print("  Strengths Count:", len(feedback['strengths']))
print("  Weaknesses Count:", len(feedback['weaknesses']))
print("  Suggested Project Sample:", feedback['project_suggestions'][0])
print("  Suggested Certification Sample:", feedback['certification_suggestions'][0])

# Test PDF Generator
report_path = "reports/test_report.pdf"
PDFReportGenerator.generate_report(
    candidate_name=contact['name'] or 'John Doe',
    contact_info=contact,
    ats_results=ats,
    match_results=match,
    feedback_results=feedback,
    predicted_role=role,
    output_path=report_path
)
print("\n[PDF Report Test]")
print("  PDF Report generated at:", report_path)
print("  File exists check:", os.path.exists(report_path))

print("\n--- Pipeline Integration Test Complete: SUCCESS ---")
