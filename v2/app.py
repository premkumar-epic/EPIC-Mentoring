import functools
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, abort
import os # Necessary for LLMAdvisor setup
import json # Necessary for LLMAdvisor setup
# Note: The actual google-genai integration from the previous step is now assumed to be in LLMAdvisor

# --- 1. SIMULATED AI CORE COMPONENTS (PLACEHOLDERS) ---
# Assuming the user has moved the placeholder classes into their respective src/ files
try:
    from src.ai_matcher import AIMatcher
    from src.ranking_engine import RankingEngine
    from src.llm_advisor import LLMAdvisor
except ImportError:
    # Fallback to local definitions if files were not created (allows app.py to run stand-alone)
    print("WARNING: Could not import AI components from src/. Using local placeholder definitions.")
    class AIMatcher:
        def match(self, student_profile): return "mnt_001"
    class RankingEngine:
        def train(self, data): return {"accuracy": 0.85}
    class LLMAdvisor:
        def __init__(self):
            # Simplified init for this block
            print("LLM Advisor Initialized (Simulated)")
        def suggest_resources(self, query):
            return "<p>[AI RESPONSE - SIMULATED]</p><p>Disclaimer: This advice is for guidance only.</p>"
        def generate_session_tips(self, student_data, mentor_assessment):
            return "<p class='font-bold text-lg text-mentor-green'>AI-Generated Session Plan: (SIMULATED)</p><ul><li>Probing Question: How do you feel?</li></ul>"
        def analyze_career_path(self, assessment_data):
            return "<p><strong>Primary Driver:</strong> Logical Reasoning. <strong>Top Careers:</strong> Data Scientist, Actuarial Analyst. (SIMULATED)</p>"


# --- 2. DATA SERVICE (IN-MEMORY SIMULATION) ---
# Initial data structure for the in-memory store
INITIAL_DATA = {
    'students': {
        'std_001': {'id': 'std_001', 'name': 'Alice Smith', 'marks': [{'subject': 'Math', 'mark': 75}, {'subject': 'Physics', 'mark': 58}, {'subject': 'History', 'mark': 89}], 'weakness_areas': 'Applied Physics, Complex Algebra', 'last_query': 'Help me understand Newton\'s laws of motion.'},
        'std_002': {'id': 'std_002', 'name': 'Bob Johnson', 'marks': [{'subject': 'Chemistry', 'mark': 92}, {'subject': 'Biology', 'mark': 88}], 'weakness_areas': 'Organic Synthesis', 'last_query': 'What is the future of biochemistry?'},
    },
    'mentors': {
        'mnt_001': {'id': 'mnt_001', 'name': 'Prof. John Doe', 'expertise': 'Physics, Engineering'},
    },
    'approval_queue': {
        'mnt_002': {'id': 'mnt_002', 'name': 'Dr. Jane Roe', 'expertise': 'Calculus, Economics', 'submitted_date': '2025-11-01'},
        'mnt_003': {'id': 'mnt_003', 'name': 'Mr. Ken Adams', 'expertise': 'History, Literature', 'submitted_date': '2025-11-02'},
    },
    'session_requests': {
        'sess_001': {'id': 'sess_001', 'student_name': 'Alice Smith', 'query': 'I need help preparing for university entrance exams, specifically calculus.'}
    },
    'feedback_report': {
        'Prof. John Doe': 'Needs to improve communication speed and provide more direct career advice.'
    },
    'career_reports': {
        'std_001': {'status': 'pending_verification', 'content': None},
        'std_002': {'status': 'verified', 'content': '<p>The student has strong analytical skills suitable for research in applied sciences.</p>'},
    },
    'anonymous_feedback': {}
}

class DataService:
    """Handles all data access, simulating database operations."""
    def __init__(self, initial_data):
        self.data = initial_data

    def get_all_mentors(self):
        return self.data['mentors']

    def get_all_students(self):
        return self.data['students']

    def get_mentor_approval_queue(self):
        return self.data['approval_queue']

    def approve_mentor(self, mentor_id):
        mentor_data = self.data['approval_queue'].pop(mentor_id, None)
        if mentor_data:
            self.data['mentors'][mentor_id] = mentor_data
            return True
        return False

    def save_anonymous_feedback(self, subject, rating, mentor_id):
        feedback_id = str(uuid.uuid4())
        self.data['anonymous_feedback'][feedback_id] = {
            'timestamp': datetime.now().isoformat(),
            'subject': subject,
            'rating': rating,
            'mentor_id': mentor_id,
            'status': 'new'
        }

    def get_student_data(self, student_id):
        return self.data['students'].get(student_id, {})

    def get_session_request(self, session_id):
        return self.data['session_requests'].get(session_id, None)

    def get_career_report(self, student_id):
        return self.data['career_reports'].get(student_id, {'status': 'not_started', 'content': None})

# --- 3. FLASK APPLICATION SETUP ---

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_secure_random_key_for_testing'

# Initialize AI Systems and Data Service
try:
    # 1. Initialize Data Service first
    DATA_SERVICE = DataService(INITIAL_DATA)

    # 2. Now initialize AI components, passing DATA_SERVICE where needed
    MATCHER = AIMatcher(DATA_SERVICE)
    # Pass the DATA_SERVICE to the RankingEngine
    RANKER = RankingEngine(DATA_SERVICE)
    ADVISOR = LLMAdvisor()

    # Optional: Run the report generation immediately upon startup to populate the dashboard
    RANKER.generate_performance_report()

except Exception as e:
    print(f"Failed to initialize core components: {e}")
# --- 4. ACCESS CONTROL DECORATOR ---

def role_required(required_role):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if session.get('user_role') != required_role:
                return redirect(url_for('login'))
            return func(*args, **kwargs)
        return wrapper
    return decorator

# --- 5. APPLICATION ROUTES ---

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        if role in ['Admin', 'Mentor', 'Student']:
            session['user_role'] = role
            session['user_id'] = 'std_001' if role == 'Student' else 'mnt_001' if role == 'Mentor' else 'adm_001'

            if role == 'Admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'Mentor':
                return redirect(url_for('mentor_dashboard'))
            elif role == 'Student':
                return redirect(url_for('student_portal'))
        else:
            return render_template('login.html', error="Invalid role selected.")

    session.clear()
    return render_template('login.html')

# --- ADMIN ROUTES ---

@app.route('/admin/dashboard')
def admin_dashboard():
    role_required('Admin')
    mentor_queue = DATA_SERVICE.get_mentor_approval_queue()
    mentor_count = len(DATA_SERVICE.get_all_mentors())
    feedback_report = DATA_SERVICE.data['feedback_report']

    return render_template('admin_dashboard.html',
                           mentor_queue=mentor_queue,
                           mentor_count=mentor_count,
                           feedback_report=feedback_report,
                           # Note: The 'verify_career_report' endpoint is defined below
                           verify_career_report=url_for('verify_career_report')
                          )

@app.route('/admin/approve/<mentor_id>', methods=['POST'])
def approve_mentor(mentor_id):
    role_required('Admin')
    if DATA_SERVICE.approve_mentor(mentor_id):
        pass
    return redirect(url_for('admin_dashboard'))

# --- FIX: ADD MISSING ROUTE ---
@app.route('/admin/career/verify')
def verify_career_report():
    """
    Simulated route for the Admin to verify a career report.
    This route name ('verify_career_report') is required by the admin_dashboard.html template.
    """
    role_required('Admin')
    # In a real application, this would render a form to verify the report.
    # For now, we simulate success and redirect.
    return redirect(url_for('admin_dashboard'))
# --- END FIX ---


# --- MENTOR ROUTES ---

@app.route('/mentor/dashboard')
def mentor_dashboard():
    role_required('Mentor')
    mentor_id = session.get('user_id', 'mnt_001')
    all_students = DATA_SERVICE.get_all_students()

    my_students = list(all_students.values())

    return render_template('mentor_dashboard.html',
                           my_students=my_students,
                           session_requests=DATA_SERVICE.data['session_requests'].values(),
                           upload_marks=url_for('upload_marks'),
                           mentor_session=url_for('mentor_session', session_id='sess_001')
                          )
@app.context_processor
def inject_global_vars():
    """Makes DATA_SERVICE and other essential globals available to all templates."""
    return {
        'DATA_SERVICE': DATA_SERVICE
    }

@app.route('/mentor/upload-marks', methods=['GET', 'POST'])
def upload_marks():
    role_required('Mentor')
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith(('.csv', '.xlsx', '.xls')):
            # In a real app, use pandas to parse file and update DATA_SERVICE
            print(f"File received: {file.filename}")
            return redirect(url_for('mentor_dashboard'))

    return render_template('mentor_upload.html')

@app.route('/mentor/session/<session_id>', methods=['GET', 'POST'])
def mentor_session(session_id):
    role_required('Mentor')
    session_request = DATA_SERVICE.get_session_request(session_id)
    if not session_request:
        abort(404)

    student_id = 'std_001'
    student_data = DATA_SERVICE.get_student_data(student_id)

    assessment_questions = [
        {'id': 1, 'text': 'What specific area of the student\'s marks is the highest priority for intervention?'},
        {'id': 2, 'text': 'Describe the student\'s primary motivation and learning style based on their history.'},
        {'id': 3, 'text': 'What is your proposed 3-step action plan for this session?'}
    ]

    ai_tips = None
    if request.method == 'POST':
        mentor_assessment = {k: v for k, v in request.form.items() if k.startswith('mentor_assessment')}
        ai_tips = ADVISOR.generate_session_tips(student_data, mentor_assessment)

    return render_template('mentor_session.html',
                           student=student_data,
                           questions=assessment_questions,
                           ai_tips=ai_tips)


# --- STUDENT ROUTES ---

@app.route('/student/portal')
def student_portal():
    role_required('Student')
    student_id = session.get('user_id', 'std_001')
    student = DATA_SERVICE.get_student_data(student_id)

    marks_data = student.get('marks', [])

    return render_template('student_portal.html',
                           student=student,
                           marks_data=marks_data)

@app.route('/student/query', methods=['POST'])
def student_query():
    role_required('Student')
    query = request.form.get('query')

    response_text = ADVISOR.suggest_resources(query)

    session['last_query'] = query
    session['last_response'] = response_text

    return redirect(url_for('student_portal'))

@app.route('/student/submit-feedback', methods=['POST'])
def submit_student_feedback():
    role_required('Student')
    mentor_id = request.form.get('mentor_id')
    subject = request.form.get('subject')
    rating = request.form.get('rating')

    DATA_SERVICE.save_anonymous_feedback(subject, rating, mentor_id)

    return redirect(url_for('student_portal'))

@app.route('/student/career/assess', methods=['GET', 'POST'])
def career_assess():
    role_required('Student')

    assessment_questions = [
        {'id': 1, 'text': 'I enjoy breaking down complex problems into smaller, manageable tasks.'},
        {'id': 2, 'text': 'I prefer working independently over collaborating in a large group.'},
        {'id': 3, 'text': 'I find satisfaction in creating tangible products or visual designs.'},
        {'id': 4, 'text': 'I am comfortable with uncertainty and ambiguity in project outcomes.'},
        {'id': 5, 'text': 'My best subject is the one that involves critical analysis and reasoning.'},
    ]

    if request.method == 'POST':
        assessment_data = request.form
        initial_report_content = ADVISOR.analyze_career_path(assessment_data)

        student_id = session.get('user_id', 'std_001')
        DATA_SERVICE.data['career_reports'][student_id] = {
            'status': 'pending_verification',
            'content': initial_report_content
        }
        return redirect(url_for('career_report'))

    return render_template('student_career.html', questions=assessment_questions)

@app.route('/student/career/report')
def career_report():
    role_required('Student')
    student_id = session.get('user_id', 'std_001')

    report_data = DATA_SERVICE.get_career_report(student_id)
    status = report_data['status']

    is_verified = (status == 'verified')

    if status == 'not_started':
        message = "Career assessment not yet submitted."
    elif status == 'pending_verification':
        message = "Your AI report is ready and awaiting Mentor verification."
    elif status == 'verified':
        message = "Your Verified Career Path Report is ready!"
    else:
        message = "Report Status Unknown."

    content = report_data.get('content', 'Report content placeholder.')

    return render_template('student_career_report.html',
                           is_verified=is_verified,
                           message=message,
                           report_content=content)


if __name__ == '__main__':
    app.run(debug=True)
