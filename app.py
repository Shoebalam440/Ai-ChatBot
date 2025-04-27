import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_dance.contrib.google import make_google_blueprint, google
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersekrit")

# Set up Google OAuth
blueprint = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_to="index"
)
app.register_blueprint(blueprint, url_prefix="/login")

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

SYSTEM_PROMPT = (
    "You are Alam, an Islamic AI assistant. Only answer Islamic-related questions. "
    "If a question is not related to Islam, politely decline and explain that you only answer Islamic questions."
)

@app.route("/")
def index():
    if not google.authorized:
        return render_template("login.html")
    user_info = None
    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        user_info = resp.json()
    return render_template("index.html", user_info=user_info)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"response": "Please enter a question."})

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_message}"
        response = model.generate_content([full_prompt])
        answer = response.text.strip()
    except Exception as e:
        answer = f"Sorry, there was an error: {str(e)}"

    return jsonify({"response": answer})

if __name__ == "__main__":
    app.run(debug=True)
