"""
AI-Powered Mentoring System - Main Application Entry Point
"""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

from services.data_service import DataService
from services.ai_service import AIService
from utils.auth import require_role, login_required

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize services
data_service = DataService()
ai_service = AIService()

# Routes
@app.route('/')
def index():
    """Home page - redirects to login if not authenticated"""
    if 'user_id' in session:
        role = session.get('role')
        if role == 'student':
            return redirect(url_for('student_dashboard'))
        elif role == 'mentor':
            return redirect(url_for('mentor_dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = data_service.authenticate_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        if data_service.create_user(name, email, password, role):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email already exists', 'error')

    return render_template('register.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# Student Routes
@app.route('/student/dashboard')
@login_required
@require_role('student')
def student_dashboard():
    """Student dashboard"""
    user_id = session['user_id']
    student = data_service.get_student(user_id)
    performance = data_service.get_student_performance(user_id)
    recommendations = data_service.get_student_recommendations(user_id)

    return render_template('student/dashboard.html',
                         student=student,
                         performance=performance,
                         recommendations=recommendations)

@app.route('/student/ai-advisor', methods=['GET', 'POST'])
@login_required
@require_role('student')
def ai_advisor():
    """AI Academic Advisor"""
    if request.method == 'POST':
        query = request.form.get('query')
        user_id = session['user_id']
        student = data_service.get_student(user_id)

        response = ai_service.get_academic_advice(query, student)
        return jsonify({'response': response})

    return render_template('student/ai_advisor.html')

@app.route('/student/career-assessment', methods=['GET', 'POST'])
@login_required
@require_role('student')
def career_assessment():
    """Career Path Assessment"""
    user_id = session['user_id']

    if request.method == 'POST':
        answers = request.form.to_dict()
        assessment_result = ai_service.generate_career_assessment(user_id, answers)
        data_service.save_assessment(user_id, assessment_result)
        flash('Assessment completed! Report pending mentor verification.', 'success')
        return redirect(url_for('career_assessment_result', assessment_id=assessment_result['id']))

    questions = ai_service.get_assessment_questions()
    return render_template('student/career_assessment.html', questions=questions)

@app.route('/student/career-assessment/<assessment_id>')
@login_required
@require_role('student')
def career_assessment_result(assessment_id):
    """View career assessment result"""
    user_id = session['user_id']
    assessment = data_service.get_assessment(user_id, assessment_id)
    return render_template('student/assessment_result.html', assessment=assessment)

@app.route('/student/performance')
@login_required
@require_role('student')
def student_performance():
    """Performance Dashboard"""
    user_id = session['user_id']
    performance = data_service.get_student_performance(user_id)
    return render_template('student/performance.html', performance=performance)

@app.route('/student/resources')
@login_required
@require_role('student')
def student_resources():
    """AI Resource Suggestions"""
    user_id = session['user_id']
    student = data_service.get_student(user_id)
    resources = ai_service.suggest_resources(student)
    return render_template('student/resources.html', resources=resources)

# Mentor Routes
@app.route('/mentor/dashboard')
@login_required
@require_role('mentor')
def mentor_dashboard():
    """Mentor dashboard"""
    mentor_id = session['user_id']
    mentor = data_service.get_mentor(mentor_id)
    students = data_service.get_mentor_students(mentor_id)
    upcoming_sessions = data_service.get_upcoming_sessions(mentor_id)

    return render_template('mentor/dashboard.html',
                       mentor=mentor,
                       students=students,
                       upcoming_sessions=upcoming_sessions)

@app.route('/mentor/students')
@login_required
@require_role('mentor')
def mentor_students():
    """View all assigned students"""
    mentor_id = session['user_id']
    students = data_service.get_mentor_students(mentor_id)
    return render_template('mentor/students.html', students=students)

@app.route('/mentor/student/<student_id>')
@login_required
@require_role('mentor')
def mentor_student_detail(student_id):
    """View student detail and get AI preparation tips"""
    mentor_id = session['user_id']
    student = data_service.get_student(student_id)
    performance = data_service.get_student_performance(student_id)
    preparation_tips = ai_service.get_session_preparation_tips(mentor_id, student_id)

    return render_template('mentor/student_detail.html',
                         student=student,
                         performance=performance,
                         preparation_tips=preparation_tips)

@app.route('/mentor/upload-marks', methods=['GET', 'POST'])
@login_required
@require_role('mentor')
def upload_marks():
    """Upload student marks via CSV/Excel"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('upload_marks'))

        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('upload_marks'))

        result = data_service.upload_marks_file(file)
        if result['success']:
            flash(f'Successfully uploaded marks for {result["count"]} students', 'success')
        else:
            flash(result['error'], 'error')

        return redirect(url_for('upload_marks'))

    return render_template('mentor/upload_marks.html')

@app.route('/mentor/sessions', methods=['GET', 'POST'])
@login_required
@require_role('mentor')
def mentor_sessions():
    """Manage mentoring sessions"""
    mentor_id = session['user_id']

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        date = request.form.get('date')
        notes = request.form.get('notes', '')

        session_id = data_service.create_session(mentor_id, student_id, date, notes)
        flash('Session scheduled successfully', 'success')
        return redirect(url_for('mentor_sessions'))

    sessions = data_service.get_mentor_sessions(mentor_id)
    students = data_service.get_mentor_students(mentor_id)
    return render_template('mentor/sessions.html', sessions=sessions, students=students)

@app.route('/mentor/feedback')
@login_required
@require_role('mentor')
def mentor_feedback():
    """View student feedback"""
    mentor_id = session['user_id']
    feedback = data_service.get_mentor_feedback(mentor_id)
    return render_template('mentor/feedback.html', feedback=feedback)

# Admin Routes
@app.route('/admin/dashboard')
@login_required
@require_role('admin')
def admin_dashboard():
    """Admin dashboard with analytics"""
    analytics = data_service.get_system_analytics()
    pending_mentors = data_service.get_pending_mentors()
    mentor_rankings = ai_service.get_mentor_rankings()

    return render_template('admin/dashboard.html',
                         analytics=analytics,
                         pending_mentors=pending_mentors,
                         mentor_rankings=mentor_rankings)

@app.route('/admin/mentors/pending')
@login_required
@require_role('admin')
def pending_mentors():
    """View pending mentor applications"""
    pending = data_service.get_pending_mentors()
    return render_template('admin/pending_mentors.html', mentors=pending)

@app.route('/admin/mentors/approve/<mentor_id>', methods=['POST'])
@login_required
@require_role('admin')
def approve_mentor(mentor_id):
    """Approve mentor application"""
    data_service.approve_mentor(mentor_id)
    flash('Mentor approved successfully', 'success')
    return redirect(url_for('pending_mentors'))

@app.route('/admin/mentors/reject/<mentor_id>', methods=['POST'])
@login_required
@require_role('admin')
def reject_mentor(mentor_id):
    """Reject mentor application"""
    data_service.reject_mentor(mentor_id)
    flash('Mentor application rejected', 'info')
    return redirect(url_for('pending_mentors'))

@app.route('/admin/matching')
@login_required
@require_role('admin')
def mentor_matching():
    """AI Mentor Matching"""
    students = data_service.get_unmatched_students()
    mentors = data_service.get_available_mentors()

    matches = []
    for student in students:
        recommendations = ai_service.match_mentor(student, mentors)
        matches.append({
            'student': student,
            'recommendations': recommendations
        })

    return render_template('admin/matching.html', matches=matches)

@app.route('/admin/assign-mentor', methods=['POST'])
@login_required
@require_role('admin')
def assign_mentor():
    """Assign mentor to student"""
    student_id = request.form.get('student_id')
    mentor_id = request.form.get('mentor_id')
    data_service.assign_mentor(student_id, mentor_id)
    flash('Mentor assigned successfully', 'success')
    return redirect(url_for('mentor_matching'))

@app.route('/admin/analytics')
@login_required
@require_role('admin')
def admin_analytics():
    """System analytics dashboard"""
    analytics = data_service.get_system_analytics()
    return render_template('admin/analytics.html', analytics=analytics)

@app.route('/admin/users')
@login_required
@require_role('admin')
def admin_users():
    """View all users"""
    users = data_service.get_all_users()
    return render_template('admin/users.html', users=users)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

