# 🎓 PSG AI Chatbot V2

> **Your 24/7 Digital Senior at PSG Tech**
> 
> *Designed to help incoming freshmen instantly find answers about campus life, academics, and facilities—without having to wait for help from seniors or staff.*

---

## 🚀 Features (V2 Modernization)

✅ **Intelligent RAG Pipeline**: Combines FAISS vector search with LLaMA 3 for highly accurate, context-aware responses.  
✅ **Conversation Memory**: The AI remembers the context of the chat, allowing for natural, multi-turn conversations.  
✅ **Token Streaming**: Real-time server-sent events (SSE) stream responses directly to the UI, mimicking a premium ChatGPT-like experience.  
✅ **Secure Architecture**: Refactored with Flask Blueprints, SQLAlchemy ORM, and cryptographically hashed passwords.  
✅ **Premium UI/UX**: A completely redesigned glassmorphism interface with fluid animations, dynamic dark/light mode, and markdown rendering.

## 📦 Setup Instructions

### Prerequisites
- Python 3.10+
- Ollama installed and running (`ollama serve`) with the `llama3` model pulled.

### Installation

```bash
# 1. Navigate to the project directory
cd aichatbotpsg-v2

# 2. Install required Python libraries
pip install -r requirements.txt

# 3. Seed the database with FAQs
python scripts/seed_db.py

# 4. Start the application
python run.py
```

Visit 👉 http://127.0.0.1:5000
