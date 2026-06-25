# Centralized Constants and Keyword Collections

# 1. Expanded Skill Categories for parsing and matching
SKILL_CATEGORIES = {
    'programming': [
        'python', 'r', 'java', 'c\\+\\+', 'c#', 'c', 'javascript', 'typescript', 'go', 'golang', 
        'scala', 'rust', 'ruby', 'php', 'bash', 'shell', 'html', 'css', 'perl', 'swift', 'kotlin',
        'dart', 'clojure', 'haskell', 'lua', 'fortran', 'cobol'
    ],
    'data_science': [
        'pandas', 'numpy', 'scipy', 'data analysis', 'data wrangling', 'exploratory data analysis', 
        'eda', 'statistics', 'statistical modeling', 'probability', 'hypothesis testing', 
        'ab testing', 'regression analysis', 'time series', 'feature engineering', 'data mining',
        'quantitative analysis', 'econometrics', 'mathematics', 'scikit-learn', 'linear regression',
        'logistic regression', 'decision trees', 'random forest', 'gradient boosting'
    ],
    'machine_learning': [
        'scikit-learn', 'sklearn', 'tensorflow', 'keras', 'pytorch', 'xgboost', 'lightgbm', 'catboost',
        'machine learning', 'deep learning', 'nlp', 'natural language processing', 'computer vision', 
        'cv', 'neural networks', 'cnn', 'rnn', 'lstm', 'transformers', 'bert', 'gpt', 'llm', 'reinforcement learning',
        'unsupervised learning', 'supervised learning', 'clustering', 'kmeans', 'svm', 'naive bayes',
        'dimensionality reduction', 'pca', 't-sne', 'autoencoders', 'gan', 'stable diffusion', 'langchain',
        'llama', 'huggingface', 'vector database', 'milvus', 'pinecone', 'chromadb', 'faiss'
    ],
    'visualization': [
        'matplotlib', 'seaborn', 'plotly', 'bokeh', 'ggplot', 'tableau', 'power bi', 'powerbi', 
        'd3.js', 'd3', 'looker', 'superset', 'dashboarding', 'dash', 'qlik', 'metabase', 'grafana', 'kibana'
    ],
    'database': [
        'sql', 'mysql', 'postgresql', 'postgres', 'sqlite', 'mongodb', 'redis', 'cassandra', 
        'dynamodb', 'mariadb', 'oracle', 'neo4j', 'nosql', 'hive', 'impala', 'snowflake',
        'clickhouse', 'elasticsearch', 'couchdb', 'firebase', 'firestore'
    ],
    'cloud_devops': [
        'aws', 'amazon web services', 'gcp', 'google cloud', 'azure', 'microsoft azure', 
        'docker', 'kubernetes', 'k8s', 'jenkins', 'git', 'github', 'gitlab', 'ci/cd', 'airflow', 
        'presto', 'spark', 'pyspark', 'hadoop', 'mapreduce', 'databricks', 'terraform', 'ansible',
        'circleci', 'argocd', 'helm', 'prometheus', 'elk stack', 'openshift', 'cloudformation'
    ]
}

# 2. Section Headers Mapping
SECTION_KEYWORDS = {
    'education': [
        'education', 'academic background', 'academic profile', 'qualifications', 
        'academic credentials', 'academic training', 'degrees', 'schooling', 'studies'
    ],
    'experience': [
        'experience', 'work experience', 'professional experience', 'employment history', 
        'work history', 'professional background', 'career history', 'employment', 'career details'
    ],
    'projects': [
        'projects', 'academic projects', 'personal projects', 'key projects', 
        'technical projects', 'major projects', 'featured projects', 'open source work'
    ],
    'internships': [
        'internships', 'internship', 'co-op', 'industrial training', 'apprenticeship', 'cooperative education'
    ],
    'achievements': [
        'achievements', 'awards', 'honors', 'accolades', 'recognitions', 'prizes', 'distinctions'
    ],
    'publications': [
        'publications', 'published works', 'articles', 'bibliography', 'conference papers'
    ],
    'research_papers': [
        'research papers', 'research', 'scientific papers', 'patents', 'thesis', 'dissertation'
    ],
    'hackathons': [
        'hackathons', 'hackathon', 'competitions', 'coding challenges', 'contests'
    ],
    'languages': [
        'languages', 'languages spoken', 'linguistic skills', 'multilingual'
    ],
    'certifications': [
        'certifications', 'certificates', 'licenses', 'credentials', 'courses', 
        'professional certifications', 'accreditations', 'training courses'
    ],
    'soft_skills': [
        'soft skills', 'interpersonal skills', 'core strengths', 'personal skills', 'competencies'
    ],
    'technical_skills': [
        'technical skills', 'skills', 'technologies', 'expertise', 'core technologies',
        'key skills', 'skills profile', 'proficiencies', 'tools'
    ],
    'leadership': [
        'leadership', 'leadership roles', 'extracurricular leadership', 'activities', 'leadership activities'
    ],
    'volunteer_work': [
        'volunteer work', 'volunteering', 'community service', 'social work', 'pro bono'
    ]
}

# 3. Action Verbs for impact scoring
ACTION_VERBS = [
    'achieved', 'acquired', 'adapted', 'addressed', 'administered', 'advised', 'analyzed',
    'authored', 'budgeted', 'built', 'calculated', 'chaired', 'clarified', 'collaborated',
    'compiled', 'completed', 'composed', 'conducted', 'consolidated', 'constructed', 'consulted',
    'coordinated', 'created', 'decreased', 'delivered', 'designed', 'detected', 'determined',
    'developed', 'devised', 'directed', 'distributed', 'documented', 'doubled', 'drafted',
    'edited', 'eliminated', 'enforced', 'engineered', 'enhanced', 'established', 'evaluated',
    'executed', 'expanded', 'expedited', 'facilitated', 'formulated', 'founded', 'generated',
    'guided', 'handled', 'headed', 'identified', 'implemented', 'improved', 'increased',
    'influenced', 'informed', 'initiated', 'inspected', 'installed', 'instituted', 'instructed',
    'integrated', 'introduced', 'invented', 'investigated', 'launched', 'led', 'managed',
    'marketed', 'mediated', 'moderated', 'monitored', 'negotiated', 'obtained', 'operated',
    'optimized', 'orchestrated', 'organized', 'overhauled', 'oversaw', 'participated', 'performed',
    'pioneered', 'planned', 'prepared', 'presented', 'produced', 'programmed', 'promoted',
    'proposed', 'provided', 'published', 'purchased', 'recorded', 'reduced', 'reorganized',
    'represented', 'researched', 'resolved', 'restructured', 'retrieved', 'reviewed', 'revised',
    'saved', 'scheduled', 'screened', 'selected', 'served', 'shaped', 'solved', 'spearheaded',
    'sponsored', 'staffed', 'standardized', 'steered', 'stimulated', 'streamlined', 'structured',
    'supervised', 'supported', 'surpassed', 'synthesized', 'systematized', 'trained', 'transformed',
    'translated', 'upgraded', 'validated', 'wrote'
]

# 4. Leadership Indicators
LEADERSHIP_VERBS = [
    'managed', 'led', 'directed', 'supervised', 'spearheaded', 'founded', 'steered', 'chaired',
    'headed', 'coordinated', 'orchestrated', 'overlooked', 'oversaw', 'pioneered', 'coached',
    'mentored', 'guided', 'governed', 'established', 'recruited', 'organized', 'conducted'
]

# 5. Soft Skills Catalog
SOFT_SKILLS_LIST = [
    'communication', 'teamwork', 'collaboration', 'problem solving', 'critical thinking',
    'adaptability', 'flexibility', 'leadership', 'mentorship', 'time management',
    'work ethic', 'creativity', 'interpersonal', 'negotiation', 'conflict resolution',
    'public speaking', 'presentation', 'active listening', 'decision making', 'empathy',
    'emotional intelligence', 'self-motivation', 'persuasion', 'patience'
]

# 6. Education Degree Indicators
DEGREE_LEVELS = {
    'phd': ['ph.d', 'phd', 'doctor of philosophy', 'doctorate'],
    'master': ['master', 'ms', 'm.s', 'm.tech', 'mtech', 'mba', 'm.b.a', 'msc', 'm.sc', 'ma', 'm.a'],
    'bachelor': ['bachelor', 'bs', 'b.s', 'b.tech', 'btech', 'ba', 'b.a', 'b.sc', 'bsc', 'bba', 'b.b.a', 'be', 'b.e']
}

# 7. Seniority Levels
SENIORITY_KEYWORDS = {
    'exec': ['director', 'vp', 'vice president', 'cto', 'cio', 'cfo', 'ceo', 'head of', 'chief'],
    'senior': ['senior', 'sr', 'lead', 'principal', 'staff', 'manager'],
    'mid': ['mid', 'intermediate', 'experienced', 'associate'],
    'junior': ['junior', 'jr', 'entry', 'associate', 'trainee', 'apprentice', 'intern']
}

# 8. Detailed Role Recommendations for Career Roadmaps & Gaps
ROLE_RECOMMENDATIONS = {
    "Data Scientist": {
        "projects": [
            "Customer Retention Predictor: Build an end-to-end classification system using XGBoost, deploy it as a REST API with FastAPI, and containerize it using Docker.",
            "Visual Search Recommender: Build a deep learning image retrieval system using PyTorch and ResNet to recommend visually similar items from an e-commerce dataset.",
            "LLM-Driven Search Enhancer: Build a RAG system using LangChain, OpenAI API, and ChromaDB vector store to search internal technical documents."
        ],
        "certifications": [
            "Microsoft Certified: Azure Data Scientist Associate",
            "Google Professional Data Scientist Certificate",
            "Databricks Certified Machine Learning Associate"
        ],
        "roadmap": [
            "Advanced Statistics & A/B Testing: Deepen knowledge in hypothesis testing, experimental design, and metrics selection.",
            "Advanced Machine Learning: Study ensemble methods, gradient boosting parameter tuning, and feature store architectures (e.g., Feast).",
            "Model Deployment & Monitoring: Learn FastAPI, Streamlit, and Prometheus/Grafana for model monitoring.",
            "LLM Fine-Tuning: Learn QLoRA fine-tuning for open-weights models like Llama or Mistral."
        ],
        "resources": [
            "Book: 'Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow' by Aurélien Géron",
            "Course: 'Deep Learning Specialization' by Andrew Ng (Coursera)",
            "Documentation: PyTorch and Scikit-Learn user guides"
        ]
    },
    "Data Analyst": {
        "projects": [
            "Interactive E-commerce Executive Dashboard: Build a multi-page Tableau or Power BI dashboard analyzing sales performance, customer acquisition, and seasonal trends.",
            "Product Cohort Analysis: Use advanced SQL (window functions, CTEs) and Pandas to run retention and cohort analyses on user activity data.",
            "Marketing Attribution Modeling: Write a Python module comparing first-touch, last-touch, and multi-touch marketing attribution models on simulated web traffic data."
        ],
        "certifications": [
            "Google Advanced Data Analytics Professional Certificate",
            "PL-300: Microsoft Power BI Data Analyst Certification",
            "Tableau Desktop Certified Associate"
        ],
        "roadmap": [
            "Mastering SQL: Learn window functions, query optimization, indexing, and CTEs.",
            "BI Tool Optimization: Deepen Dax queries in Power BI or LOD calculations in Tableau.",
            "Business Communication: Focus on executive storytelling, slide design, and translating metrics into business actions.",
            "Introduction to Python: Learn basic Pandas and Numpy data manipulation."
        ],
        "resources": [
            "Book: 'Storytelling with Data' by Cole Nussbaumer Knaflic",
            "Course: 'Google Data Analytics Professional Certificate' (Coursera)",
            "Platform: LeetCode/HackerRank SQL challenges"
        ]
    },
    "Machine Learning Engineer": {
        "projects": [
            "LLM Fine-Tuning Pipeline: Fine-tune a Llama-3 model on a custom dataset using LoRA/QLoRA and deploy it with vLLM on cloud hardware.",
            "Real-Time Object Detection API: Deploy an optimized YOLO model via an asynchronous FastAPI service utilizing Redis queues for image pre-processing.",
            "Distributed Training Cluster: Implement a pipeline using PyTorch DistributedDataParallel (DDP) to train a BERT classifier across multiple GPU nodes."
        ],
        "certifications": [
            "AWS Certified Machine Learning - Specialty",
            "TensorFlow Developer Certificate (or DeepLearning.AI credentials)",
            "Google Cloud Professional Machine Learning Engineer"
        ],
        "roadmap": [
            "MLOps Practices: Implement automated CI/CD pipelines using GitHub Actions for model retraining and validation.",
            "System Design & Scale: Learn distributed inference, Triton Inference Server, and ONNX model optimization.",
            "Deep Learning Foundations: Gain hands-on practice building custom architectures (Attention Mechanisms, CNNs, Transformers) in PyTorch.",
            "Infrastructure as Code: Understand Terraform and Kubernetes orchestration for ML scaling."
        ],
        "resources": [
            "Book: 'Designing Machine Learning Systems' by Chip Huyen",
            "Course: 'Machine Learning Engineering for Production (MLOps)' by DeepLearning.AI",
            "GitHub: 'mlops-zoomcamp' by DataTalksClub"
        ]
    },
    "Data Engineer": {
        "projects": [
            "Real-Time Clickstream ETL Pipeline: Use Apache Kafka to ingest clickstream events, process them with PySpark Structured Streaming, and write results to Snowflake.",
            "Serverless Data Lake Ingestion: Build an AWS-native pipeline using Lambda, EventBridge, Glue, and Athena to crawl and query unstructured data in S3.",
            "Incremental Lakehouse Pipeline: Design a multi-layered (bronze/silver/gold) Delta Lake using Spark on Databricks with dbt core for SQL transformations."
        ],
        "certifications": [
            "Snowflake SnowPro Core Certification",
            "Google Cloud Professional Data Engineer",
            "AWS Certified Data Engineer - Associate"
        ],
        "roadmap": [
            "Distributed Computing: Master Apache Spark, PySpark optimization, partitioning, and memory management.",
            "Data Pipeline Orchestration: Build complex DAGs in Apache Airflow, Prefect, or Dagster.",
            "Data Modeling & Warehousing: Understand Kimball methodologies, Star/Snowflake schemas, and slowly changing dimensions (SCD).",
            "NoSQL & Cache Engines: Study DynamoDB, Cassandra, and Redis caching strategies."
        ],
        "resources": [
            "Book: 'Designing Data-Intensive Applications' by Martin Kleppmann",
            "Course: 'Data Engineering Zoomcamp' by DataTalksClub",
            "Documentation: Apache Spark and Delta Lake guides"
        ]
    },
    "Business Analyst": {
        "projects": [
            "Software Migration Requirements Document: Write a comprehensive Agile Product Backlog with detailed User Stories, Acceptance Criteria, and UML activity diagrams.",
            "Operational Cost-Benefit Model: Build an interactive financial model in Excel/Python analyzing ROI and payback periods for a proposed cloud migration.",
            "BPMN Workflows Optimization: Map and simulate as-is vs to-be business processes for a customer onboarding flow in Signavio or Camunda."
        ],
        "certifications": [
            "IIBA Certified Business Analysis Professional (CBAP)",
            "PMI Professional in Business Analysis (PMI-PBA)",
            "Certified Scrum Product Owner (CSPO)"
        ],
        "roadmap": [
            "Agile Frameworks: Gain deep knowledge of Scrum, Kanban, and product roadmap development using Jira/Confluence.",
            "Data Literacy: Learn standard SQL query structures and simple data visualization strategies in Power BI.",
            "Business Process Modeling: Study BPMN standards, mapping business state diagrams, and gap analysis methodologies.",
            "Stakeholder Management: Focus on facilitation, presentation techniques, and conflict resolution."
        ],
        "resources": [
            "Book: 'Business Analysis Body of Knowledge (BABOK Guide)' by IIBA",
            "Course: 'Agile Planning and Portfolio Management' (Coursera)",
            "Documentation: Atlassian Jira and Confluence user guides"
        ]
    },
    "Software Engineer": {
        "projects": [
            "Microservices E-commerce Platform: Build a backend system using Spring Boot / Node.js, implementing service discovery, API gateway, and Postgres databases.",
            "Real-Time Collaborative Dashboard: Create a responsive React/TypeScript frontend that connects to a WebSockets server for live multiplayer interactions.",
            "High-Throughput Cache proxy: Build an asynchronous proxy server in Go that caches web requests in Redis, utilizing go-routines for high concurrent performance."
        ],
        "certifications": [
            "AWS Certified Solutions Architect - Associate",
            "Oracle Certified Professional: Java SE Developer",
            "Google Cloud Associate Cloud Engineer"
        ],
        "roadmap": [
            "System Design: Study scalability, caching mechanisms (Redis), load balancing, and partitioning.",
            "Code Quality & Testing: Master unit testing, integration tests, mock frameworks, and Clean Code principles.",
            "Cloud Deployment: Learn Docker, container scheduling (Kubernetes), and serverless architectures.",
            "Data Structures & Algorithms: Focus on dynamic programming, graph traversal, and time/space complexity."
        ],
        "resources": [
            "Book: 'Clean Code: A Handbook of Agile Software Craftsmanship' by Robert C. Martin",
            "Course: 'System Design Interview' by Alex Xu",
            "Platform: LeetCode coding practice"
        ]
    }
}
