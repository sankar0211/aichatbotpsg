import os
import sys

# Add the parent directory to the path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import FAQ

def seed_faqs():
    app = create_app()
    with app.app_context():
        # Clear existing
        db.session.query(FAQ).delete()
        
        faq_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'PSG_chatbot.txt')
        if not os.path.exists(faq_file):
            print(f"Error: {faq_file} not found.")
            return

        count = 0
        with open(faq_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('?', 1)
                    if len(parts) == 2:
                        question, answer = parts
                        q_str = question.strip() + '?'
                        a_str = answer.strip()
                        
                        faq = FAQ(question=q_str, answer=a_str)
                        db.session.add(faq)
                        count += 1

        db.session.commit()
        print(f"Successfully seeded {count} FAQs into the database.")

if __name__ == "__main__":
    seed_faqs()
