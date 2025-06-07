from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import sqlite3
import ollama

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.before_request
def skip_ngrok_warning():
    request.headers.environ['HTTP_NGROK_SKIP_BROWSER_WARNING'] = 'true'

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
            return redirect('/chat')
        else:
            error = 'Invalid username or password!'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
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
            return 'Username already exists. <a href="/register">Try another</a>.'
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/chat', methods=['GET'])
def chat():
    if 'username' in session:
        return render_template('chat.html')
    return redirect('/login')

@app.route('/chat', methods=['POST'])
def chat_reply():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Please enter a message."}), 400

        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": user_message}]
        )
        bot_reply = response.get("message", {}).get("content", "").strip()

        if not bot_reply:
            return jsonify({"reply": "No response generated."}), 500

        return jsonify({"reply": bot_reply})

    except Exception as e:
        print("Error:", e)
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
