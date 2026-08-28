from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.models import FAQ

class RAGService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None
        self.faq_list = []
        
    def build_index(self):
        self.faq_list = FAQ.query.all()
        if not self.faq_list:
            print("No FAQs in DB to build index.")
            self.tfidf_matrix = None
            return

        questions = [faq.question for faq in self.faq_list]
        self.tfidf_matrix = self.vectorizer.fit_transform(questions)
        print(f"TF-IDF index built with {len(self.faq_list)} FAQs.")

    def search(self, query: str, top_k: int = 1, threshold: float = 0.2):
        if self.tfidf_matrix is None or not self.faq_list:
            return None

        # Convert user query to TF-IDF vector
        query_vec = self.vectorizer.transform([query])
        
        # Calculate cosine similarity against all FAQs
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get the index of the highest similarity score
        best_match_idx = np.argmax(similarities)
        best_score = similarities[best_match_idx]
        
        if best_score >= threshold:
            return self.faq_list[best_match_idx]
        
        return None

rag_service = RAGService()
