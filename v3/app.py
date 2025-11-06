import functools
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, abort, flash, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
import os
import json
import pandas as pd
from io import StringIO

# ==========================================================
# 1. SIMULATED AI CORE COMPONENTS
# ==========================================================
try:
    from src.ai_matcher import AIMatcher
    from src.ranking_engine import RankingEngine
    from src.llm_advisor import LLMAdvisor
except ImportError:
    print("⚠️ Using local simulated AI components.")

    class AIMatcher:
        def __init__(self, data_service=None): pass
        def match_student_to_mentor(self, student_id): return "mnt_001"

    class RankingEngine:
        def __init__(self, data_service=None): pass
        def generate_performance_report(self): pass

    class LLMAdvisor:
        def __init__(self):
            print("LLM Advisor Initialized (Simulated)")
        def suggest_resources(self, query):
            return "<p>[AI RESPONSE - SIMULATED]</p><p>Disclaimer: This advice is for guidance only.</p>"
        def generate_session_tips(self, student_data, mentor_assessment):
            return "<p><b>AI-Generated Session Plan:</b></p><ul><li>Review Algebra</li><li>Practice Physics</li></ul>"
        def analyze_career_path(self, assessment_data):
            return "<p><strong>Top Careers:</strong> Data Scientist, Engineer</p>"

# ==========================================================
# 2. DATA SERVICE
# ==========================================================
INITIAL_DATA = {
    "students": {
        "std_001": {"id": "std_001", "name": "Alice Smith", "marks": [{"subject": "Math", "mark": 75}]},
        "std_002": {"id": "std_002", "name": "Bob Johnson", "marks": [{"subject": "Biology", "mark": 88}]}
    },
    "mentors": {"mnt_001": {"id": "mnt_001", "name": "Prof. John Doe", "expertise": "Physics"}},
    "approval_queue": {},
    "session_requests": {},
    "feedback_report": {},
    "career_reports": {},
    "anonymous_feedback": {}
}

class DataService:
    def __init__(self, data): self.data = data
    def get_all_students(self): return self.data["students"]
    def get_all_mentors(self): return self.data["mentors"]
    def get_student_data(self, sid): return self.data["students"].get(sid, {})
    def approve_mentor(self, mid):
        if mid in self.data["approval_queue"]:
            self.data["mentors"][mid] = self.data["approval_queue"].pop(mid)
            return True
        return False
    def update_marks_from_df(self, df):
        req = ["student_id", "subject", "mark"]
        if not all(c in df.columns for c in req):
            raise ValueError("CSV must contain columns: student_id, subject, mark.")
        updated = set()
        for _, row in df.iterrows():
            sid, subj, mark = str(row["student_id"]).strip(), str(row["subject"]).strip(), int(row["mark"])
            if sid in self.data["students"]:
                student = self.data["students"][sid]
                found = False
                for m in student.get("marks", []):
                    if m["subject"] == subj:
                        m["mark"] = mark
                        found = True
                        break
                if not found:
                    student["marks"].append({"subject": subj, "mark": mark})
                updated.add(sid)
        return len(updated)

# ==========================================================
# 3. FLASK APP SETUP
# ==========================================================
app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecret"
app.config["JWT_SECRET_KEY"] = "jwtsecret"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
jwt = JWTManager(app)
CORS(app)

DATA_SERVICE = DataService(INITIAL_DATA)
MATCHER = AIMatcher(DATA_SERVICE)
RANKER = RankingEngine(DATA_SERVICE)
ADVISOR = LLMAdvisor()

# ==========================================================
# 4. JWT AUTHENTICATION
# ==========================================================
users = {
    "admin": {"password": "admin123", "role": "Admin"},
    "mentor": {"password": "mentor123", "role": "Mentor"},
    "student": {"password": "student123", "role": "Student"},
}

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    username, password = data.get("username"), data.get("password")
    user = users.get(username)
    if user and user["password"] == password:
        token = create_access_token(identity={"username": username, "role": user["role"]})
        return jsonify({"token": token, "role": user["role"], "username": username}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/protected")
@jwt_required()
def protected_api():
    identity = get_jwt_identity()
    return jsonify({"message": f"Hello {identity['username']}, role: {identity['role']}"}), 200

# ==========================================================
# 5. SESSION LOGIN (For Templates)
# ==========================================================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role")
        if role in ["Admin", "Mentor", "Student"]:
            session["user_role"] = role
            session["user_id"] = f"{role[:3].lower()}_001"
            return redirect(url_for(f"{role.lower()}_dashboard" if role != "Student" else "student_portal"))
        flash("Invalid role selected.", "error")
    return render_template("login.html")

def role_required(role):
    def wrapper(fn):
        @functools.wraps(fn)
        def inner(*a, **kw):
            if session.get("user_role") != role:
                flash("Access denied. Wrong role.", "error")
                return redirect(url_for("login"))
            return fn(*a, **kw)
        return inner
    return wrapper

# ==========================================================
# 6. ADMIN ROUTES
# ==========================================================
@app.route("/admin/dashboard")
@role_required("Admin")
def admin_dashboard():
    mentors = DATA_SERVICE.get_all_mentors()
    queue = DATA_SERVICE.data["approval_queue"]
    return render_template("admin_dashboard.html", mentor_queue=queue, mentor_count=len(mentors))

@app.route("/admin/approve/<mid>", methods=["POST"])
@role_required("Admin")
def approve_mentor(mid):
    ok = DATA_SERVICE.approve_mentor(mid)
    flash("Mentor approved!" if ok else "Mentor not found.", "info")
    return redirect(url_for("admin_dashboard"))

# ==========================================================
# 7. MENTOR ROUTES
# ==========================================================
@app.route("/mentor/dashboard")
@role_required("Mentor")
def mentor_dashboard():
    students = DATA_SERVICE.get_all_students()
    return render_template("mentor_dashboard.html", my_students=students.values())

@app.route("/mentor/upload", methods=["POST"])
@role_required("Mentor")
def upload_marks():
    file = request.files.get("file")
    if not file or not file.filename.endswith(".csv"):
        flash("Invalid file. Please upload CSV.", "error")
        return redirect(url_for("mentor_dashboard"))
    try:
        df = pd.read_csv(StringIO(file.read().decode("utf-8")))
        count = DATA_SERVICE.update_marks_from_df(df)
        flash(f"✅ Updated marks for {count} students.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("mentor_dashboard"))

# ==========================================================
# 8. STUDENT ROUTES
# ==========================================================
@app.route("/student/portal")
@role_required("Student")
def student_portal():
    sid = session.get("user_id", "std_001")
    student = DATA_SERVICE.get_student_data(sid)
    mentor_id = MATCHER.match_student_to_mentor(sid)
    mentor = DATA_SERVICE.get_all_mentors().get(mentor_id, {"name": "None"})
    return render_template("student_portal.html", student=student, mentor=mentor)

@app.route("/student/query", methods=["POST"])
@role_required("Student")
def student_query():
    q = request.form.get("query")
    resp = ADVISOR.suggest_resources(q)
    session["last_response"] = resp
    flash("AI response generated.", "info")
    return redirect(url_for("student_portal"))

# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
