import os
import pickle
import re
import logging
from typing import List, Tuple, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeClassifier:
    """
    Wrapper class to load the TF-IDF Vectorizer and Logistic Regression model,
    predict role categories from resume text, and handle automatic fallback training.
    """
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        self.vectorizer_path = os.path.join(models_dir, "tfidf_vectorizer.pkl")
        self.classifier_path = os.path.join(models_dir, "classifier.pkl")
        self.vectorizer = None
        self.classifier = None
        self._load_models()
        
    def _load_models(self):
        """
        Loads models from disk. Trains them if they don't exist.
        """
        if not os.path.exists(self.vectorizer_path) or not os.path.exists(self.classifier_path):
            logger.info("Pickled models not found. Triggering automated model training...")
            try:
                # Import dynamically to avoid absolute dependency loops
                from notebooks.train_model import train_and_save_classifier
                train_and_save_classifier()
            except ImportError:
                # If path issues occur, try importing relative or run directly
                try:
                    import sys
                    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    from notebooks.train_model import train_and_save_classifier
                    train_and_save_classifier()
                except Exception as e:
                    logger.error(f"Failed to run train_model script programmatically: {e}")
                    raise RuntimeError("Model files missing and automated retraining failed.")
        
        # Load from disk
        try:
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            with open(self.classifier_path, 'rb') as f:
                self.classifier = pickle.load(f)
            logger.info("Successfully loaded Vectorizer and Classifier models.")
        except Exception as e:
            logger.error(f"Failed loading model pickle files: {e}")
            raise e

    def _clean_text(self, text: str) -> str:
        """
        Preprocess input text identically to training preprocessing.
        """
        if not text:
            return ""
        # Lowercase and clean special chars except hashtags/pluses (C++, C#)
        cleaned = text.lower()
        cleaned = re.sub(r'[^a-zA-Z\s#\+]', ' ', cleaned)
        return cleaned

    def predict_probabilities(self, text: str) -> List[Tuple[str, float]]:
        """
        Predict role probabilities for a given resume text.
        
        Returns:
            A sorted list of tuples (Role, Probability Percentage) in descending order.
        """
        if not self.vectorizer or not self.classifier:
            self._load_models()
            
        cleaned_text = self._clean_text(text)
        vec_text = self.vectorizer.transform([cleaned_text])
        probabilities = self.classifier.predict_proba(vec_text)[0]
        
        classes = self.classifier.classes_
        results = []
        for cls, prob in zip(classes, probabilities):
            results.append((cls, float(prob * 100)))
            
        # Sort by probability descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def predict_role(self, text: str) -> Tuple[str, float]:
        """
        Predict the most suitable single role.
        """
        probs = self.predict_probabilities(text)
        if probs:
            return probs[0]
        return ("Unknown", 0.0)
