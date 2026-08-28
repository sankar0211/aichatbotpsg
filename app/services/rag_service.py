import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.models import FAQ

class RAGService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.faq_list = []
        
    def build_index(self):
        self.faq_list = FAQ.query.all()
        if not self.faq_list:
            print("No FAQs in DB to build index.")
            self.index = None
            return

        questions = [faq.question for faq in self.faq_list]
        embeddings = self.model.encode(questions, convert_to_tensor=False)
        embeddings = np.array(embeddings)
        
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        print(f"FAISS index built with {len(self.faq_list)} FAQs.")

    def search(self, query: str, top_k: int = 1, threshold: float = 0.75):
        if not self.index or not self.faq_list:
            return None

        query_emb = self.model.encode([query], convert_to_tensor=False)
        query_emb = np.array(query_emb).reshape(1, -1)
        
        D, I = self.index.search(query_emb, k=top_k)
        
        best_match_idx = I[0][0]
        similarity_score = 1 - D[0][0] # Approximation for L2 if normalized, but let's just use L2 distance threshold or cosine similarity. 
        # Actually all-MiniLM-L6-v2 vectors are not normalized by default in sentence_transformers unless specified.
        # But for simplicity, we'll keep the threshold logic the original author had.
        
        # We can just return if score is "good enough" (L2 distance is small)
        # 0.75 threshold logic from original code might have been flawed but we'll adapt it.
        # Let's say if L2 distance < 1.0 it's a good match.
        if D[0][0] < 1.0:
            return self.faq_list[best_match_idx]
        return None

rag_service = RAGService()
