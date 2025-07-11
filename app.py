from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import sqlite3
import ollama
import os
from sentence_transformers import SentenceTransformer, util
import faiss
import numpy as np

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.before_request
def skip_ngrok_warning():
    request.headers.environ['HTTP_NGROK_SKIP_BROWSER_WARNING'] = 'true'

# Load and embed FAQs at startup
model = SentenceTransformer('all-MiniLM-L6-v2')
faq_file = 'PSG_chatbot.txt'
faq_data = []
if os.path.exists(faq_file):
    with open(faq_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split('?', 1)
                if len(parts) == 2:
                    question, answer = parts
                    faq_data.append({"question": question.strip() + '?', "answer": answer.strip()})
faq_questions = [entry['question'] for entry in faq_data]
faq_embeddings = model.encode(faq_questions, convert_to_tensor=False)
faq_embeddings = np.array(faq_embeddings)
dim = faq_embeddings.shape[1] if faq_embeddings.shape[0] > 0 else 384
faq_index = faiss.IndexFlatL2(dim)
if faq_embeddings.shape[0] > 0:
    faq_index.add(faq_embeddings)

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()

    # Display current users for debugging or admin view
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    print("\nCurrent Users Table:")
    print("+----+------------------------+------------------------+")
    print("| ID | Username               | Password               |")
    print("+----+------------------------+------------------------+")
    for row in rows:
        print(f"| {str(row[0]).ljust(2)} | {row[1].ljust(22)} | {row[2].ljust(22)} |")
    print("+----+------------------------+------------------------+\n")
    conn.close()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            session['just_logged_in'] = True
            return redirect('/chat')
        else:
            error = 'Invalid username or password!'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            return redirect('/login')
        except sqlite3.IntegrityError:
            error = 'Username already exists! Create a new one.'
        finally:
            conn.close()
    return render_template('register.html', error=error)

@app.route('/chat', methods=['GET'])
def chat():
    if 'username' in session:
        just_logged_in = session.pop('just_logged_in', False)
        return render_template('chat.html', username=session['username'], just_logged_in=just_logged_in)
    return redirect('/login')

@app.route('/chat', methods=['POST'])
def chat_reply():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"reply": "Please enter a message."}), 400

        query_embedding = model.encode(user_message, convert_to_tensor=False)
        query_embedding = np.array(query_embedding).reshape(1, -1)
        D, I = faq_index.search(query_embedding, k=1)

        best_match_idx = I[0][0]
        similarity_score = 1 - D[0][0]

        if similarity_score > 0.75:
            faq_entry = faq_data[best_match_idx]
            context = f"You are an AI assistant for PSG College of Technology. Use this information to answer naturally:\nQ: {faq_entry['question']}\nA: {faq_entry['answer']}"
        else:
            context = "You are an AI assistant for PSG College of Technology. Answer naturally based on your general knowledge."

        prompt = f"{context}\n\nUser: {user_message}\nAI:"
        response = ollama.chat(model='llama3', messages=[{"role": "user", "content": prompt}])
        bot_reply = response.get("message", {}).get("content", "").strip()

        if not bot_reply:
            return jsonify({"reply": "Sorry, I couldn't generate a response."}), 500

        return jsonify({"reply": bot_reply})

    except Exception as e:
        app.logger.error(f"Chat reply error: {e}", exc_info=True)
        return jsonify({"reply": "Server error. Please try again later."}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
