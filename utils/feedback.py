from typing import Dict, Any, List

ROLE_RECOMMENDATIONS = {
    "Data Scientist": {
        "projects": [
            "Customer Retention Predictor: Build an end-to-end classification system using XGBoost, deploy it as a REST API with FastAPI, and containerize it using Docker.",
            "Visual Search Recommender: Build a deep learning image retrieval system using PyTorch and ResNet to recommend visually similar items from an e-commerce dataset."
        ],
        "certifications": [
            "Microsoft Certified: Azure Data Scientist Associate",
            "Google Professional Data Scientist Certificate"
        ],
        "roadmap": [
            "Advanced Statistics & A/B Testing: Deepen knowledge in hypothesis testing, experimental design, and metrics selection.",
            "Advanced Machine Learning: Study ensemble methods, gradient boosting parameter tuning, and feature store architectures (e.g., Feast).",
            "Model Deployment & Monitoring: Learn FastAPI, Streamlit, and Prometheus/Grafana for model monitoring."
        ]
    },
    "Data Analyst": {
        "projects": [
            "Interactive E-commerce Executive Dashboard: Build a multi-page Tableau or Power BI dashboard analyzing sales performance, customer acquisition, and seasonal trends.",
            "Product Cohort Analysis: Use advanced SQL (window functions, CTEs) and Pandas to run retention and cohort analyses on user activity data."
        ],
        "certifications": [
            "Google Advanced Data Analytics Professional Certificate",
            "PL-300: Microsoft Power BI Data Analyst Certification"
        ],
        "roadmap": [
            "Mastering SQL: Learn window functions, query optimization, indexing, and CTEs.",
            "BI Tool Optimization: Deepen Dax queries in Power BI or LOD calculations in Tableau.",
            "Business Communication: Focus on executive storytelling, slide design, and translating metrics into business actions."
        ]
    },
    "Machine Learning Engineer": {
        "projects": [
            "LLM Fine-Tuning Pipeline: Fine-tune a Llama-3 model on a custom dataset using LoRA/QLoRA and deploy it with vLLM on cloud hardware.",
            "Real-Time Object Detection API: Deploy an optimized YOLO model via an asynchronous FastAPI service utilizing Redis queues for image pre-processing."
        ],
        "certifications": [
            "AWS Certified Machine Learning - Specialty",
            "TensorFlow Developer Certificate (or DeepLearning.AI credentials)"
        ],
        "roadmap": [
            "MLOps Practices: Implement automated CI/CD pipelines using GitHub Actions for model retraining and validation.",
            "System Design & Scale: Learn distributed inference, Triton Inference Server, and ONNX model optimization.",
            "Deep Learning Foundations: Gain hands-on practice building custom architectures (Attention Mechanisms, CNNs, Transformers) in PyTorch."
        ]
    },
    "Data Engineer": {
        "projects": [
            "Real-Time Clickstream ETL Pipeline: Use Apache Kafka to ingest clickstream events, process them with PySpark Structured Streaming, and write results to Snowflake.",
            "Serverless Data Lake Ingestion: Build an AWS-native pipeline using Lambda, EventBridge, Glue, and Athena to crawl and query unstructured data in S3."
        ],
        "certifications": [
            "Snowflake SnowPro Core Certification",
            "Google Cloud Professional Data Engineer"
        ],
        "roadmap": [
            "Distributed Computing: Master Apache Spark, PySpark optimization, partitioning, and memory management.",
            "Data Pipeline Orchestration: Build complex DAGs in Apache Airflow, Prefect, or Dagster.",
            "Data Modeling & Warehousing: Understand Kimball methodologies, Star/Snowflake schemas, and slowly changing dimensions (SCD)."
        ]
    },
    "Business Analyst": {
        "projects": [
            "Software Migration Requirements Document: Write a comprehensive Agile Product Backlog with detailed User Stories, Acceptance Criteria, and UML activity diagrams.",
            "Operational Cost-Benefit Model: Build an interactive financial model in Excel/Python analyzing ROI and payback periods for a proposed cloud migration."
        ],
        "certifications": [
            "IIBA Certified Business Analysis Professional (CBAP)",
            "PMI Professional in Business Analysis (PMI-PBA)"
        ],
        "roadmap": [
            "Agile Frameworks: Gain deep knowledge of Scrum, Kanban, and product roadmap development using Jira/Confluence.",
            "Data Literacy: Learn standard SQL query structures and simple data visualization strategies in Power BI.",
            "Business Process Modeling: Study BPMN standards, mapping business state diagrams, and gap analysis methodologies."
        ]
    },
    "Software Engineer": {
        "projects": [
            "Microservices E-commerce Platform: Build a backend system using Spring Boot / Node.js, implementing service discovery, API gateway, and Postgres databases.",
            "Real-Time Collaborative Dashboard: Create a responsive React/TypeScript frontend that connects to a WebSockets server for live multiplayer interactions."
        ],
        "certifications": [
            "AWS Certified Solutions Architect - Associate",
            "Oracle Certified Professional: Java SE Developer"
        ],
        "roadmap": [
            "System Design: Study scalability, caching mechanisms (Redis), load balancing, and partitioning.",
            "Code Quality & Testing: Master unit testing, integration tests, mock frameworks, and Clean Code principles.",
            "Cloud Deployment: Learn Docker, container scheduling, and serverless architectures."
        ]
    }
}

class AIFeedbackSystem:
    """
    Generates tailored feedback, suggestions, and roadmaps based on resume parse analysis
    and ML classifier role prediction.
    """
    
    @staticmethod
    def generate_feedback(ats_data: Dict[str, Any], match_data: Dict[str, Any], predicted_role: str) -> Dict[str, Any]:
        """
        Synthesizes overall strengths, weaknesses, project suggestions, and learning roadmap.
        """
        strengths = []
        weaknesses = []
        
        # 1. Evaluate Strengths
        # Check contact completeness
        filled_contacts = [k for k, v in ats_data['contact_status'].items() if v]
        if 'email' in filled_contacts and 'phone' in filled_contacts:
            strengths.append("Strong contact structure: Both email and phone number are clearly visible and parseable.")
        if 'linkedin' in filled_contacts:
            strengths.append("Professional profile linkage: Valid LinkedIn account is provided for recruiter reference.")
        if 'github' in filled_contacts:
            strengths.append("Technical portfolio linkage: GitHub link is present, highlighting active open-source contributions.")
            
        # Check sections
        filled_sections = [k for k, v in ats_data['section_status'].items() if v]
        if len(filled_sections) >= 3:
            strengths.append(f"Well-structured resume: Found key logical sections including {', '.join([s.title() for s in filled_sections])}.")
            
        # Check metrics & formatting
        if ats_data['metrics_detected']:
            strengths.append("Impact-driven description: Quantified project metrics and business impact found in text.")
        if ats_data['bullets_detected']:
            strengths.append("Recruiter-friendly layout: Utilizes structured list formatting and bullet points for high readability.")
            
        # Check skill diversity
        if ats_data['skills_score'] >= 20:
            strengths.append("Rich technical vocabulary: Extracted a diverse range of technical skills across multiple domains.")
            
        # 2. Evaluate Weaknesses
        missing_contacts = [k for k, v in ats_data['contact_status'].items() if not v]
        if 'linkedin' in missing_contacts:
            weaknesses.append("Missing professional socials: Consider adding a LinkedIn profile to build professional trust.")
        if 'github' in missing_contacts and predicted_role in ['Software Engineer', 'Machine Learning Engineer', 'Data Engineer']:
            weaknesses.append(f"Portfolio gap: As a potential {predicted_role}, adding a GitHub profile is highly recommended to showcase code.")
            
        missing_sections = [k for k, v in ats_data['section_status'].items() if not v]
        for sec in missing_sections:
            weaknesses.append(f"Missing section '{sec.title()}': Including dedicated space for {sec} provides complete background details.")
            
        if not ats_data['metrics_detected']:
            weaknesses.append("Lack of metrics/quantified results: Recruiters prefer seeing data impact. Add numbers (%, $, count) showing the result of your work.")
            
        if ats_data['word_count'] < 150:
            weaknesses.append("Resume content is too sparse: Provide more detailed descriptions of your tasks and projects to increase ATS keyword matching.")
        elif ats_data['word_count'] > 1000:
            weaknesses.append("Resume is overly verbose: Try to condense the information. Maintain a tight 1-to-2 page length for maximum focus.")
            
        # 3. Job Match specific feedback
        missing_skills = match_data.get('missing_skills', [])
        if missing_skills:
            weaknesses.append(f"Skill gap for Job Description: Missing {len(missing_skills)} key skills listed in the target job requirements.")
            
        # Ensure we have at least some default strengths/weaknesses
        if not strengths:
            strengths.append("Basic resume layout is established. Keep refining headers to highlight skills.")
        if not weaknesses:
            weaknesses.append("No critical defects found. Focus on tailoring resume bullet points to your dream jobs.")

        # 4. Extract Project & Certification recommendations
        recs = ROLE_RECOMMENDATIONS.get(predicted_role, ROLE_RECOMMENDATIONS['Software Engineer'])
        
        # 5. Formulate learning roadmap
        roadmap = []
        if missing_skills:
            # If we have missing skills, start the roadmap by tackling those first
            roadmap.append(f"Bridge Job Description gaps: Learn the missing technologies: {', '.join(missing_skills[:5])}.")
        
        # Append general roadmap for the predicted role
        roadmap.extend(recs['roadmap'])
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "project_suggestions": recs['projects'],
            "certification_suggestions": recs['certifications'],
            "learning_roadmap": roadmap
        }
