#!/usr/bin/env python
import os
import io
import time
import logging
from datetime import datetime
from typing import Dict, Any, Callable, Tuple

# Import pipeline components
from utils.extractor import ResumeExtractor
from utils.parser import ResumeParser
from utils.classifier import ResumeClassifier
from utils.analyzer import ATSAnalyzer, JobMatchAnalyzer
from utils.feedback import AIFeedbackSystem
from utils.reporter import PDFReportGenerator

# --- Styling & Output Configurations ---
ANSI_GREEN = "\033[92m"
ANSI_RED = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_CYAN = "\033[96m"
ANSI_BOLD = "\033[1m"
ANSI_RESET = "\033[0m"

# Simple test input values
SAMPLE_RESUME_TEXT = """
John Doe
john.doe@email.com | +1 123 456 7890 | San Francisco, CA
linkedin.com/in/johndoe | github.com/johndoe | jdoe-portfolio.com

Summary
Experienced Data Scientist with 5+ years of experience designing and deploying machine learning models.

Skills
Python, R, SQL, Pandas, NumPy, Scikit-Learn, PyTorch, Tableau, AWS, Docker, Git

Experience
Senior Data Scientist at TechCorp (2022 - Present)
- Mapped client churn behaviors using Scikit-Learn gradient boosting, saving $2M in annual retention costs.
- Developed real-time data visualization dashboards in Tableau for executive KPIs.

Education
Master of Science in Data Science - University of California (2020 - 2022)

Certifications
Certified AWS Machine Learning Specialist, AWS Cloud Practitioner
"""

SAMPLE_JOB_DESCRIPTION = """
We are looking for a Data Scientist with 3+ years experience.
Must be skilled in Python, SQL, AWS, and Machine Learning libraries like Scikit-Learn.
Prior experience in Tableau dashboarding and containerization (Docker) is highly preferred.
Degree in Data Science or Computer Science.
"""


def get_timestamp() -> str:
    """
    Returns the current local timestamp formatted for console logging.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def log_step(name: str):
    """
    Logs a visual separator for a new testing phase.
    """
    print(f"\n{ANSI_BOLD}{ANSI_CYAN}--- [{get_timestamp()}] RUNNING TEST: {name} ---{ANSI_RESET}")


def log_info(msg: str):
    """
    Logs generic execution logs.
    """
    print(f"[{ANSI_CYAN}INFO{ANSI_RESET}] {get_timestamp()} - {msg}")


def log_pass(name: str):
    """
    Logs a green bold PASS status badge.
    """
    print(f"[{ANSI_GREEN}{ANSI_BOLD}PASS{ANSI_RESET}] {get_timestamp()} - {name} successfully verified.")


def log_fail(name: str, reason: str):
    """
    Logs a red bold FAIL status badge.
    """
    print(f"[{ANSI_RED}{ANSI_BOLD}FAIL{ANSI_RESET}] {get_timestamp()} - {name} failed validation: {reason}")


class IntegrationTestSuite:
    """
    SaaS ATS integration test suite evaluating extraction, parsing, analytics,
    ML classifications, matching, suggestions, and reporting.
    """
    
    def __init__(self):
        self.tests_total = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.start_time = 0.0
        self.execution_time = 0.0
        
    def run_test(self, test_name: str, test_func: Callable[[], Tuple[bool, str]]):
        """
        Executes an individual test block safely and counts stats.
        """
        self.tests_total += 1
        log_step(test_name)
        
        try:
            passed, message = test_func()
            if passed:
                log_pass(test_name)
                self.tests_passed += 1
            else:
                log_fail(test_name, message)
                self.tests_failed += 1
        except Exception as e:
            log_fail(test_name, f"Unhandled exception: {str(e)}")
            self.tests_failed += 1

    def test_resume_extraction(self) -> Tuple[bool, str]:
        """
        1. Test Resume Extraction
        Builds a small PDF stream dynamically using ReportLab, extracts text,
        and verifies content output.
        """
        from reportlab.pdfgen import canvas
        
        log_info("Generating mock PDF document stream using ReportLab...")
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer)
        c.drawString(100, 750, "John Doe Profile Text")
        c.drawString(100, 730, "john.doe@email.com")
        c.drawString(100, 710, "Python, SQL, PyTorch")
        c.save()
        buffer.seek(0)
        
        log_info("Extracting text contents from memory buffer stream...")
        extracted_text = ResumeExtractor.extract_text(buffer, "test_resume.pdf")
        
        if not extracted_text:
            return False, "Extracted text content is empty."
            
        if "John Doe" not in extracted_text or "john.doe@email.com" not in extracted_text:
            return False, f"Extracted text lacks expected entities. Content: {extracted_text[:100]}"
            
        log_info("Extracted content validated successfully.")
        return True, ""

    def test_resume_parsing(self) -> Tuple[bool, str]:
        """
        2. Test Resume Parsing
        Parses text and validates name, email, and skills.
        """
        log_info("Initializing parser for sample resume text...")
        parser = ResumeParser(SAMPLE_RESUME_TEXT)
        analysis = parser.get_full_analysis()
        
        # ✓ Parsed name exists
        name = analysis['contact']['name']
        if not name:
            return False, "Candidate name extraction returned None."
        log_info(f"✓ Mapped Name: {name}")
        
        # ✓ Email extracted
        email = analysis['contact']['email']
        if not email or email != "john.doe@email.com":
            return False, f"Candidate email extraction failed. Extracted: {email}"
        log_info(f"✓ Mapped Email: {email}")
        
        # ✓ Skills detected
        skills = analysis['all_skills']
        if not skills or len(skills) < 5:
            return False, f"Expected multiple skills detected. Extracted: {skills}"
        log_info(f"✓ Skills Detected ({len(skills)}): {', '.join(skills[:6])}...")
        
        return True, ""

    def test_ats_analyzer(self) -> Tuple[bool, str]:
        """
        3. Test ATS Analyzer
        Verifies ATS compatibility scoring ranges.
        """
        log_info("Running ATS compatibility analyzer...")
        parser = ResumeParser(SAMPLE_RESUME_TEXT)
        ats_results = ATSAnalyzer.calculate_ats_score(parser)
        
        # ✓ ATS score between 0-100
        score = ats_results.get('overall_score', -1)
        if not (0 <= score <= 100):
            return False, f"ATS score {score} falls outside valid 0-100 limit bounds."
        log_info(f"✓ ATS Compatibility Score: {score}/100")
        
        return True, ""

    def test_resume_classifier(self) -> Tuple[bool, str]:
        """
        4. Test Resume Classifier
        Verifies ML predictions and probability values.
        """
        log_info("Loading ML Resume Classifier wrapper...")
        classifier = ResumeClassifier()
        
        # Predict
        role, confidence = classifier.predict_role(SAMPLE_RESUME_TEXT)
        log_info(f"Predicted Role: {role} (Confidence: {confidence:.2f}%)")
        
        # ✓ Classifier confidence valid
        if not (0.0 <= confidence <= 100.0):
            return False, f"Classifier confidence value {confidence} is invalid (not between 0-100%)."
            
        # Verify explainable coefficients features extraction
        explanation = classifier.explain_prediction(SAMPLE_RESUME_TEXT, role)
        if not explanation:
            return False, "Feature prediction explanation returned empty list."
        log_info(f"✓ Top Predictive Keyword: '{explanation[0][0]}' (influence weight: {explanation[0][1]:.4f})")
        
        return True, ""

    def test_job_match_analyzer(self) -> Tuple[bool, str]:
        """
        5. Test Job Match Analyzer
        Verifies multi-dimensional job description alignment scoring ranges.
        """
        log_info("Analyzing resume fit against target requirements...")
        match_results = JobMatchAnalyzer.match_job_description(SAMPLE_RESUME_TEXT, SAMPLE_JOB_DESCRIPTION)
        
        # ✓ Job Match score between 0-100
        match_score = match_results.get('match_score', -1)
        if not (0 <= match_score <= 100):
            return False, f"Job Match score {match_score} falls outside valid 0-100 limit bounds."
        log_info(f"✓ Job Match Score: {match_score}%")
        
        return True, ""

    def test_ai_feedback(self) -> Tuple[bool, str]:
        """
        6. Test AI Feedback
        Verifies that roadmaps and upsell feedback are calculated.
        """
        log_info("Calculating ATS alignment metrics...")
        parser = ResumeParser(SAMPLE_RESUME_TEXT)
        ats_res = ATSAnalyzer.calculate_ats_score(parser)
        match_res = JobMatchAnalyzer.match_job_description(SAMPLE_RESUME_TEXT, SAMPLE_JOB_DESCRIPTION)
        
        log_info("Generating tailored AI feedback roadmaps...")
        feedback = AIFeedbackSystem.generate_feedback(ats_res, match_res, "Data Scientist")
        
        required_keys = ['strengths', 'weaknesses', 'project_suggestions', 'certification_suggestions', 'learning_roadmap']
        for key in required_keys:
            if key not in feedback or not feedback[key]:
                return False, f"Missing or empty feedback recommendation list: '{key}'"
                
        log_info(f"✓ Mapped strengths count: {len(feedback['strengths'])}")
        log_info(f"✓ Custom certification recommendation: {feedback['certification_suggestions'][0]}")
        return True, ""

    def test_pdf_report_generator(self) -> Tuple[bool, str]:
        """
        7. Test PDF Report Generator
        Generates and verifies PDF existence on disk.
        """
        parser = ResumeParser(SAMPLE_RESUME_TEXT)
        contact = parser.extract_contact_info()
        ats_res = ATSAnalyzer.calculate_ats_score(parser)
        match_res = JobMatchAnalyzer.match_job_description(SAMPLE_RESUME_TEXT, SAMPLE_JOB_DESCRIPTION)
        feedback = AIFeedbackSystem.generate_feedback(ats_res, match_res, "Data Scientist")
        
        report_path = "reports/test_pipeline_report.pdf"
        
        # Clean existing report to ensure fresh creation
        if os.path.exists(report_path):
            os.remove(report_path)
            
        log_info(f"Generating PDF report file at: {report_path}")
        PDFReportGenerator.generate_report(
            candidate_name=contact['name'] or "Test Candidate",
            contact_info=contact,
            ats_results=ats_res,
            match_results=match_res,
            feedback_results=feedback,
            predicted_role="Data Scientist",
            output_path=report_path
        )
        
        # ✓ PDF report successfully generated
        if not os.path.exists(report_path):
            return False, "PDF report document was not found on disk."
            
        size = os.path.getsize(report_path)
        if size == 0:
            return False, "Generated PDF report file size is 0 bytes (empty document)."
            
        log_info(f"✓ PDF report verified on disk (size: {size} bytes).")
        
        # Clean up generated file
        try:
            os.remove(report_path)
            log_info("Temporary PDF report cleaned from disk.")
        except Exception as e:
            logger.warning(f"Could not delete temporary report: {e}")
            
        return True, ""

    def execute_all(self):
        """
        Executes the entire integration testing suite and prints stats.
        """
        print(f"{ANSI_BOLD}{ANSI_YELLOW}==================================================")
        print("          APEX ATS INTEGRATION TEST SUITE")
        print(f"=================================================={ANSI_RESET}")
        
        self.start_time = time.time()
        
        # Execute individual test steps
        self.run_test("Resume Document Text Extraction", self.test_resume_extraction)
        self.run_test("Resume Parser Entity Mapping", self.test_resume_parsing)
        self.run_test("ATS Compatibility Scoring", self.test_ats_analyzer)
        self.run_test("ML Role Prediction & Explanation", self.test_resume_classifier)
        self.run_test("Job Description Match Analysis", self.test_job_match_analyzer)
        self.run_test("AI Feedback Recommendation Roadmaps", self.test_ai_feedback)
        self.run_test("PDF report document compilation", self.test_pdf_report_generator)
        
        self.execution_time = time.time() - self.start_time
        
        # Print Summary
        overall_status = "PASS" if self.tests_failed == 0 else "FAIL"
        status_color = ANSI_GREEN if overall_status == "PASS" else ANSI_RED
        
        print(f"\n{ANSI_BOLD}==================================================")
        print("                  TEST SUMMARY")
        print(f"=================================================={ANSI_RESET}")
        print(f"Total Tests    : {self.tests_total}")
        print(f"Passed         : {ANSI_GREEN}{self.tests_passed}{ANSI_RESET}")
        print(f"Failed         : {ANSI_RED if self.tests_failed > 0 else ANSI_GREEN}{self.tests_failed}{ANSI_RESET}")
        print(f"Execution Time : {self.execution_time:.3f} seconds")
        print(f"Overall Status : {status_color}{ANSI_BOLD}{overall_status}{ANSI_RESET}")
        print(f"{ANSI_BOLD}=================================================={ANSI_RESET}")
        
        if self.tests_failed > 0:
            sys.exit(1)


if __name__ == "__main__":
    import sys
    suite = IntegrationTestSuite()
    suite.execute_all()
