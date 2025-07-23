from flask import Flask, render_template, request, redirect, session, flash, jsonify
import pickle
import pandas as pd
import numpy as np
import uuid
from supabase import create_client, Client
import google.generativeai as genai



app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# ✅ Supabase setup
SUPABASE_URL = "https://ldavbvqueimeawfjbmjb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxkYXZidnF1ZWltZWF3ZmpibWpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc5MTk1MDMsImV4cCI6MjA2MzQ5NTUwM30.gMvPoLqKkGN2hYgROBG4GBNN_tOJ9xukN5zJ-HUbq7U"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ Gemini setup
genai.configure(api_key= "AIzaSyAlt1Bw7ItewjK3DoaR77Tm4mTofE9TeCU")  
gemini_model = genai.GenerativeModel("models/gemini-2.0-flash")


@app.route("/", methods=["GET"])
def home():
    return render_template("login_signup.html")

@app.route("/signup", methods=["POST"])
def signup():
    email = request.form["email"]
    password = request.form["password"]
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        flash("Signup successful! ✅ Please login.", "success") if response.user else flash("Signup failed ❌", "error")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            session["email"] = email
            flash("Login successful ✅", "success")
            return redirect("/predict")
        flash("Login failed ❌", "error")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect("/")

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "email" not in session:
        flash("Please login first ❌", "error")
        return redirect("/")

    result = None
    if request.method == "POST":
        try:
            email = session["email"]
            exam_type = request.form.get("exam_type").lower()
            seat_type = request.form.get("category")
            gender = request.form.get("gender")
            quota = request.form.get("quota")

            main_rank = request.form.get("main_rank")
            adv_rank = request.form.get("advanced_rank")
            rank = int(main_rank if exam_type == "main" else adv_rank)

            # ✅ Suggest exams if rank is very high
            if rank > 100000:
                result = {
                    "input_rank": rank,
                    "exam_type": exam_type.title(),
                    "seat_type": seat_type,
                    "gender": gender,
                    "quota": quota,
                    "top_suggestions": [
                        {"institute": "BITSAT", "program": "BITS Pilani/Goa/Hyderabad", "admission_probability": "-"},
                        {"institute": "COMEDK", "program": "RVCE, BMSCE", "admission_probability": "-"},
                        {"institute": "VITEEE", "program": "VIT Vellore/Chennai", "admission_probability": "-"},
                        {"institute": "WBJEE", "program": "Jadavpur University", "admission_probability": "-"},
                        {"institute": "MHCET", "program": "COEP, VJTI", "admission_probability": "-"}
                    ]
                }
                return render_template("index.html", result=result)

            # ✅ Load dataset
            dataset = "jee_main_data.csv" if exam_type == "main" else "jee_advanced_data.csv"
            data = pd.read_csv(dataset)

            # ✅ Apply filters
            filtered = data[
    (data["Seat Type"].str.upper().str.strip() == seat_type.upper().strip()) &
    (data["Gender"].str.upper().str.strip() == gender.upper().strip()) &
    (data["Quota"].str.upper().str.strip() == quota.upper().strip()) &
    (pd.to_numeric(data["Opening Rank"], errors="coerce") <= rank) &
    (pd.to_numeric(data["Closing Rank"], errors="coerce") >= rank)
]


            if filtered.empty:
                flash("No matching data found for the provided filters ❌", "error")
                return render_template("index.html", result=None)

            suggestions = []
            for _, row in filtered.iterrows():
                try:
                    closing = float(row["Closing Rank"])
                    chance = round(max(0, min(100, (closing - rank) / closing * 100)), 2)
                    suggestions.append({
                        "institute": row["Institute"],
                        "program": row["Academic Program Name"],
                        "admission_probability": chance
                    })
                except:
                    continue

            top_suggestions = sorted(suggestions, key=lambda x: -x["admission_probability"])[:5]

            result = {
                "input_rank": rank,
                "exam_type": exam_type.title(),
                "seat_type": seat_type,
                "gender": gender,
                "quota": quota,
                "top_suggestions": top_suggestions
            }

            supabase.table("predictions").insert({
                "id": str(uuid.uuid4()),
                "user_email": email,
                "exam_type": exam_type,
                "rank": rank,
                "seat_type": seat_type,
                "gender": gender,
                "quota": quota
            }).execute()

        except Exception as e:
            flash(f"Error during prediction: {str(e)}", "error")

    return render_template("index.html", result=result)

@app.route("/gemini", methods=["POST"])
def gemini_chat():
    try:
        prompt = request.json.get("prompt")
        if not prompt:
            return jsonify({"reply": "Please enter a question."}), 400
        response = gemini_model.generate_content(prompt)
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out!", "info")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
