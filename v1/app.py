import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import numpy as np
# Import logic modules from the src directory
from src.ai_matcher import AIMatcher
from src.ranking_engine import RankingEngine
from src.llm_advisor import LLMAdvisor

app = Flask(__name__)
# Use a secret key for session management (required for role persistence)
app.secret_key = 'super_secret_mentoring_key'

# --- Initialize Systems ---
# Initialization is done once when the app starts
try:
    MATCHER = AIMatcher()
    MATCHER.index_mentors()
    RANKER = RankingEngine()
    RANKER.train_ranker()
    ADVISOR = LLMAdvisor()
except Exception as e:
    print(f"Failed to initialize core components: {e}")
    # Exit or handle gracefully in a production environment

# Helper to load student data
def load_students():
    path = os.path.join('src', 'data', 'students.json')
    if os.path.exists(path):
        with open(path, 'r') as f:
            return {s['id']: s for s in json.load(f)}
    return {}

# --- ROUTES ---

@app.route('/')
def index():
    """Renders the main dashboard (Admin view)."""

    # --- Data for Dashboard ---
    mentors_path = os.path.join('src', 'data', 'mentors.json')
    students = load_students()

    mentor_count = 0
    if os.path.exists(mentors_path):
        with open(mentors_path, 'r') as f:
            mentor_count = len(json.load(f))

    # --- Role and Weights for display/forms ---
    role = session.get('role', 'Admin')

    # Store weights in session/database if you need long-term persistence,
    # but for simplicity, we'll store them in a simple dictionary.
    weights = {
        'vector_distance': session.get('vector_distance_weight', 1.0),
        'historical_success': session.get('historical_success_weight', 1.0)
    }

    # Decide which template to render based on the role selected
    if role == 'Student':
        # Redirect student role to their dedicated page
        return redirect(url_for('student_advisor'))

    # Admin Dashboard context
    return render_template(
        'index.html',
        role=role,
        mentor_count=mentor_count,
        student_count=len(students),
        feedback_count=len(RANKER.feedback_data),
        weights=weights
    )

@app.route('/set_role', methods=['POST'])
def set_role():
    """Handles role switching."""
    session['role'] = request.form.get('role', 'Admin')
    return redirect(url_for('index'))

@app.route('/update_weights', methods=['POST'])
def update_weights():
    """Handles setting the admin weighting sliders."""
    try:
        session['vector_distance_weight'] = float(request.form['vector_distance'])
        session['historical_success_weight'] = float(request.form['historical_success'])
    except ValueError:
        pass # Handle error gracefully
    return redirect(url_for('index'))

@app.route('/retrain', methods=['POST'])
def retrain_model():
    """Handles manual model retraining."""
    if RANKER.train_ranker():
        # You'd typically log success here
        pass
    return redirect(url_for('index'))

@app.route('/session_analysis', methods=['GET', 'POST'])
def session_analysis():
    """Handles mentor assignment and AI-generated advice (Teacher/Admin view)."""

    students = load_students()
    student_id = None
    final_plan_html = None
    final_match = None

    weights = {
        'vector_distance': session.get('vector_distance_weight', 1.0),
        'historical_success': session.get('historical_success_weight', 1.0)
    }

    if request.method == 'POST':
        student_id = request.form['student_id']
        student = students.get(student_id)

        if student:
            mentee_query = f"I need a mentor for my weaknesses: {student['weakness_areas']}. My goal is to {student['goal']}."

            # 1. Find Matches
            initial_matches = MATCHER.find_matches(mentee_query, n_results=3)

            if initial_matches:
                # 2. Re-rank using feedback and admin weights
                df_matches = pd.DataFrame(initial_matches)
                if RANKER.model is not None:
                    df_matches['success_score'] = RANKER.model.predict_proba(df_matches[['vector_distance']])[:, 1]
                else:
                    df_matches['success_score'] = 0.5

                distance_w = weights['vector_distance']
                success_w = weights['historical_success']
                df_matches['final_score'] = (1 - df_matches['vector_distance']) * distance_w + df_matches['success_score'] * success_w

                final_match = df_matches.sort_values(by='final_score', ascending=False).iloc[0].to_dict()

                # 3. Generate AI Plan
                final_plan_html = ADVISOR.analyze_weakness_and_suggest_plan(student, final_match)

    return render_template(
        'session.html',
        students=students,
        selected_student_id=student_id,
        final_match=final_match,
        final_plan_html=final_plan_html
    )

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    """Stores session feedback."""
    try:
        mentor_id = request.form['mentor_id']
        session_rating = int(request.form['session_rating'])
        mentee_query = request.form['mentee_query']
        vector_distance = float(request.form['vector_distance'])

        RANKER.add_feedback(mentor_id, mentee_query, vector_distance, session_rating)
    except Exception as e:
        # Log or handle the error
        pass

    return redirect(url_for('session_analysis'))

@app.route('/student_advisor', methods=['GET', 'POST'])
def student_advisor():
    """Handles the Student self-service advisor page."""

    resources_html = None
    query = ""

    if request.method == 'POST':
        query = request.form['query']
        resources_html = ADVISOR.suggest_resources(query)

    return render_template('student_self_service.html', resources_html=resources_html, query=query)

if __name__ == '__main__':
    # You need to ensure the src/data files are present for this to run
    if not os.path.exists('src/data/students.json'):
         print("Warning: Missing src/data/students.json. Create it with dummy data.")
    if not os.path.exists('src/data/mentors.json'):
         print("Warning: Missing src/data/mentors.json. Create it with dummy data.")

    # Run the Flask app
    app.run(debug=True)
