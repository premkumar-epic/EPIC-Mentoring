from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from functools import wraps
import pandas as pd
import os

mentor_dashboard_bp = Blueprint('mentor_dashboard', __name__, template_folder='templates')

# --- Utility Decorator ---
def mentor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'mentor':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Helper Functions ---
def render_mentor_dashboard(data_service, user_id, message=None, error=None):
    """Renders the main mentor dashboard with student and session info."""

    # 1. Get assigned students and format for display
    assigned_students_data = data_service.get_mentor_students(user_id)

    if assigned_students_data is None:
        assigned_students = []
    else:
        # Convert list of dicts to DataFrame for easier manipulation
        assigned_students_df = pd.DataFrame(assigned_students_data)

        # Filter for relevant columns and format
        assigned_students = assigned_students_df[[
            'student_id',
            'name',
            'math_marks',
            'science_marks',
            'english_marks',
            'psychometric_score',
            'is_verified' # Include the new status flag
        ]].rename(columns={
            'student_id': 'ID',
            'name': 'Name',
            'math_marks': 'Math',
            'science_marks': 'Science',
            'english_marks': 'English',
            'psychometric_score': 'Psy Score',
            'is_verified': 'Verification Status'
        }).to_html(classes=['table-auto', 'w-full', 'text-left'], index=False)


    # 2. Get sessions (Mock data for display)
    sessions = [
        {'id': 'sess_001', 'student_name': 'Alice Smith', 'date': '2025-11-10', 'status': 'Pending'},
        {'id': 'sess_002', 'student_name': 'Bob Johnson', 'date': '2025-11-15', 'status': 'Scheduled'},
    ]

    # 3. Get feedback (Mock for display)
    feedback_count = len(data_service.get_feedback())

    # 4. Total students assigned (Mock)
    total_assigned = len(assigned_students_data)

    return render_template(
        'mentor_dashboard.html',
        message=message,
        error=error,
        assigned_students=assigned_students,
        sessions=sessions,
        feedback_count=feedback_count,
        total_assigned=total_assigned,
        # Pass data needed for the template to check student verification status
        students_for_verification=[
            {'id': s['student_id'], 'name': s['name'], 'is_verified': s.get('is_verified', False)}
            for s in assigned_students_data
        ]
    )

# --- Routes ---

@mentor_dashboard_bp.route('/mentor/dashboard')
@mentor_required
def dashboard():
    data_service = current_app.data_service
    user_id = session['user_id']
    return render_mentor_dashboard(data_service, user_id)

@mentor_dashboard_bp.route('/mentor/upload-marks', methods=['GET', 'POST'])
@mentor_required
def upload_marks():
    data_service = current_app.data_service
    user_id = session['user_id']

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_mentor_dashboard(data_service, user_id, error="No file part in the request.")

        file = request.files['file']

        if file.filename == '':
            return render_mentor_dashboard(data_service, user_id, error="No file selected.")

        if file:
            try:
                # The file is a FileStorage object, passed directly to the service
                num_records = data_service.load_data_from_upload(file)
                return redirect(url_for('mentor_dashboard.dashboard', message=f"Successfully uploaded and processed {num_records} student records."))
            except ValueError as e:
                return render_mentor_dashboard(data_service, user_id, error=str(e))
            except Exception as e:
                print(f"File processing error: {e}")
                return render_mentor_dashboard(data_service, user_id, error="An unexpected error occurred during file processing.")

    # GET request for the upload page
    return render_template('mentor_upload_marks.html', title="Upload Student Marks")

@mentor_dashboard_bp.route('/mentor/verify/<student_id>', methods=['POST'])
@mentor_required
def verify_student_report(student_id):
    """Route for mentor to verify an AI-generated student report."""
    data_service = current_app.data_service
    user_id = session['user_id']

    if data_service.verify_student_report(student_id):
        return redirect(url_for('mentor_dashboard.dashboard', message=f"Report for Student ID {student_id} verified successfully."))
    else:
        return redirect(url_for('mentor_dashboard.dashboard', error=f"Failed to verify report for Student ID {student_id}."))

@mentor_dashboard_bp.route('/mentor/session/<session_id>', methods=['GET', 'POST'])
@mentor_required
def mentoring_session(session_id):
    from src.pages.Mentoring_Session import render_mentoring_session

    data_service = current_app.data_service
    llm_advisor = current_app.llm_advisor

    return render_mentoring_session(data_service, llm_advisor, session_id)
