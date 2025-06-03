from flask import Flask, render_template, request, jsonify
import ollama

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Please enter a message."}), 400

        # Generate a response using Ollama
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

if __name__ == "__main__":
    app.run(debug=True)
