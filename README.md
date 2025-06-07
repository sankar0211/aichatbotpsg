# 🎓 PSG College of Technology AI Chatbot

A conversational AI chatbot for PSG College of Technology, built using **Python**, **Flask**, **FAISS**, **Sentence Transformers**, and **Ollama (LLaMA 3)** for natural and FAQ-based AI interactions.

---

## 🚀 Features

✅ AI-powered responses using LLaMA 3 via Ollama  
✅ FAQ-aware intelligent answers using prompt injection (RAG technique)  
✅ Fast semantic search with FAISS and Sentence Transformers  
✅ Dark/Light mode toggle on chat, login, and registration screens  
✅ Secure login, registration, and session management  
✅ Persistent local user authentication with SQLite  
✅ Clean, modern web UI built with pure HTML/CSS/JS  

---

## 📦 Local Development Setup

### Prerequisites
- Python 3.10+
- Ollama installed and running (`ollama serve`)
- Required Python packages (see `requirements.txt`)

---

### 📥 Installation & Run

```bash
# 1️⃣ Clone the repository
git clone https://github.com/sankar0211/aichatbotpsg.git
cd aichatbotpsg

# 2️⃣ Install required Python libraries
pip install -r requirements.txt

# 3️⃣ Start Ollama server in a separate terminal
ollama serve

# 4️⃣ Run the Flask application
python app.py
```

Visit 👉 http://127.0.0.1:5000

---

## 📖 Project Structure

```bash
├── app.py                     # Main Flask backend server
├── PSG_chatbot.txt            # FAQ database for chatbot
├── users.db                   # SQLite user authentication database
├── requirements.txt           # Python dependencies
├── test_request.py            # Optional test script for chat requests
├── static/
│   ├── images/
│   │   ├── bot-avatar.png
│   │   ├── favicon.ico
│   │   ├── user-avatar.png
│   └── styles.css             # Optional shared CSS (if applicable)
├── templates/
│   ├── chat.html
│   ├── login.html
│   ├── register.html
├── README.md                  # Project documentation
└── .gitignore
```

---

## 📑 Data Files

- **PSG_chatbot.txt**: Plain text file containing question-answer pairs for embedding and semantic search.
- **users.db**: SQLite database automatically generated for storing user credentials securely.

---

## 📃 Notes

- Edit `PSG_chatbot.txt` to add or modify FAQ entries.
- To change the AI model, adjust `model='llama3'` in `app.py`.
- The current setup is suitable for development; enhance security and environment configs for production.

---

## 📸 Screenshots

✅ Clean Register/Login Pages  
✅ AI Chat Interface with Typing Indicators  
✅ Welcome Popups on login  
✅ FAQ-based responses integrated with AI model  


---

## 📣 Author

**Sankar S V**  
GitHub: [@sankar0211](https://github.com/sankar0211)

---

## 📄 License

Open-source project under the MIT License.
