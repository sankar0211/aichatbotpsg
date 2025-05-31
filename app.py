from flask import Flask, render_template, request, jsonify
import ollama  # now it’s installed!

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    # Use ollama to generate a response
    response = ollama.chat(model="llama3", messages=[
        {"role": "user", "content": user_message}
    ])
    bot_reply = response["message"]["content"].strip()

    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
