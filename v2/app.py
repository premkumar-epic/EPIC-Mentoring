import functools
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, abort, flash # Added 'flash'
import os
import json
import pandas as pd
from io import StringIO

# --- 1. SIMULATED AI CORE COMPONENTS (Imports & Fallback) ---
try:
    # Ensure these are imported from the correct src/ files
    from src.ai_matcher import AIMatcher
    from src.ranking_engine import RankingEngine
    from src.llm_advisor import LLMAdvisor
except ImportError:
    # Fallback to local definitions for robust startup
    print("WARNING: Could not import AI components from src/. Using local placeholder definitions.")
    class AIMatcher:
        def __init__(self, data_service=None): pass
        # Updated to reflect new functional logic
        def match_student_to_mentor(self, student_id): return "mnt_001"
    class RankingEngine:
        def __init__(self, data_service=None): pass
        def generate_performance_report(self): pass
    class LLMAdvisor:
        def __init__(self):
            print("LLM Advisor Initialized (Simulated)")
        # Updated to reflect new response formatting and simulated error
        def suggest_resources(self, query):
            # Simulate a failure for demonstration if needed, otherwise give response
            return "<p>[AI RESPONSE - SIMULATED]</p><p>Disclaimer: This advice is for guidance only.</p>"
        def generate_session_tips(self, student_data, mentor_assessment):
            # Updated to reflect new formatted output
            return "<p class='font-bold text-lg text-mentor-green'>AI-Generated Session Plan:</p><ul class='list-disc list-inside space-y-2'><li>Probing Question: How do you feel about Complex Algebra?</li><li>Action Step: Review all formulas.</li><li>Next Session Focus: Applied Physics.</li></ul>"
        def analyze_career_path(self, assessment_data):
            return "<p><strong>Primary Driver:</strong> Logical Reasoning. <strong>Top Careers:</strong> Data Scientist, Actuarial Analyst. (SIMULATED)</p>"


# --- 2. DATA SERVICE (IN-MEMORY SIMULATION) ---
# Updated INITIAL_DATA as per instructions
INITIAL_DATA = {
    'students': {
        'std_001': {'id': 'std_001', 'name': 'Alice Smith', 'marks': [{'subject': 'Math', 'mark': 75}, {'subject': 'Physics', 'mark': 58}, {'subject': 'History', 'mark': 89}], 'weakness_areas': 'Applied Physics, Complex Algebra, Engineering', 'last_query': 'Help me understand Newton\'s laws of motion.'},
        'std_002': {'id': 'std_002', 'name': 'Bob Johnson', 'marks': [{'subject': 'Chemistry', 'mark': 92}, {'subject': 'Biology', 'mark': 88}], 'weakness_areas': 'Organic Synthesis, Biochemistry', 'last_query': 'What is the future of biochemistry?'},
    },
    'mentors': {
        'mnt_001': {'id': 'mnt_001', 'name': 'Prof. John Doe', 'expertise': 'Physics, Engineering, Calculus'},
    },
    'approval_queue': {
        'mnt_002': {'id': 'mnt_002', 'name': 'Dr. Jane Roe', 'expertise': 'Calculus, Economics', 'submitted_date': '2025-11-01'},
    },
    'session_requests': {
        'sess_001': {'id': 'sess_001', 'student_name': 'Alice Smith', 'student_id': 'std_001', 'query': 'I need help preparing for university entrance exams, specifically calculus.'}
    },
    'feedback_report': {}, # Starts empty, filled by RANKER
    'career_reports': {
        'std_001': {'status': 'pending_verification', 'content': None},
        'std_002': {'status': 'verified', 'content': '<p>The student has strong analytical skills suitable for research in applied sciences.</p>'},
    },
    'anonymous_feedback': {
         'f1': {'timestamp': '2025-11-01', 'subject': 'Math', 'rating': 5, 'mentor_id': 'mnt_001', 'status': 'new'},
         'f2': {'timestamp': '2025-11-02', 'subject': 'Physics', 'rating': 4, 'mentor_id': 'mnt_001', 'status': 'new'}
    }
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
            'rating': int(rating), # Ensure rating is int
            'mentor_id': mentor_id,
            'status': 'new'
        }

    def get_student_data(self, student_id):
        return self.data['students'].get(student_id, {})

    def get_session_request(self, session_id):
        return self.data['session_requests'].get(session_id, None)

    def get_career_report(self, student_id):
        return self.data['career_reports'].get(student_id, {'status': 'not_started', 'content': None})

    # --- NEW METHOD: Update marks from uploaded file data ---
    def update_marks_from_df(self, df):
        """Processes a Pandas DataFrame to update student marks."""
        # Ensure required columns exist
        required_cols = ['student_id', 'subject', 'mark']
        if not all(col in df.columns for col in required_cols):
            raise ValueError("CSV must contain columns: student_id, subject, mark.")

        updated_students = set()

        for index, row in df.iterrows():
            # Robust type conversion
            try:
                student_id = str(row['student_id']).strip()
                subject = str(row['subject']).strip()
                mark = int(row['mark'])
            except ValueError:
                 # Skip rows with invalid data
                 continue

            if student_id in self.data['students']:
                student_data = self.data['students'][student_id]

                # Logic: replace old mark for the subject, or add new mark
                found = False
                if 'marks' not in student_data:
                    student_data['marks'] = []

                for item in student_data['marks']:
                    if item['subject'] == subject:
                        item['mark'] = mark
                        found = True
                        break

                if not found:
                    student_data['marks'].append({'subject': subject, 'mark': mark})

                updated_students.add(student_id)

        return len(updated_students)
    # --- END NEW METHOD ---


# --- 3. FLASK APPLICATION SETUP ---

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_secure_random_key_for_testing')
app.config['ENV'] = 'development' # Ensure proper environment setting

# Initialize AI Systems and Data Service (CRITICAL FIX: Order is correct)
try:
    # 1. Initialize Data Service first
    DATA_SERVICE = DataService(INITIAL_DATA)

    # 2. Now initialize AI components, passing DATA_SERVICE where needed
    MATCHER = AIMatcher(DATA_SERVICE) # <--- Fix: Pass DATA_SERVICE
    RANKER = RankingEngine(DATA_SERVICE) # <--- Fix: Pass DATA_SERVICE
    ADVISOR = LLMAdvisor()

    # Optional: Run the report generation immediately upon startup to populate the dashboard
    RANKER.generate_performance_report()

except Exception as e:
    print(f"Failed to initialize core components: {e}")

# --- 4. CONTEXT PROCESSOR (CRITICAL FIX: Expose DATA_SERVICE to all templates) ---
@app.context_processor
def inject_global_vars():
    """Makes DATA_SERVICE and other essential globals available to all templates."""
    return {
        'DATA_SERVICE': DATA_SERVICE
    }

# --- 5. ACCESS CONTROL DECORATOR ---

def role_required(required_role):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if session.get('user_role') != required_role:
                # Use flash for a user-friendly message
                flash('Access denied. Please log in with the correct role.', 'error')
                return redirect(url_for('login'))
            return func(*args, **kwargs)
        return wrapper
    return decorator

# --- 6. APPLICATION ROUTES ---

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        if role in ['Admin', 'Mentor', 'Student']:
            session['user_role'] = role
            # Ensure the user_id is set correctly for the portal/dashboard
            session['user_id'] = 'std_001' if role == 'Student' else 'mnt_001' if role == 'Mentor' else 'adm_001'

            if role == 'Admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'Mentor':
                return redirect(url_for('mentor_dashboard'))
            elif role == 'Student':
                return redirect(url_for('student_portal'))
        else:
            flash("Invalid role selected.", 'error')
            return render_template('login.html')

    session.clear()
    return render_template('login.html')

# --- ADMIN ROUTES ---

@app.route('/admin/dashboard')
@role_required('Admin')
def admin_dashboard():
    mentor_queue = DATA_SERVICE.get_mentor_approval_queue()
    mentor_count = len(DATA_SERVICE.get_all_mentors())
    # The feedback_report is filled by the RANKER upon startup
    feedback_report = DATA_SERVICE.data.get('feedback_report', {})

    return render_template('admin_dashboard.html',
                           mentor_queue=mentor_queue,
                           mentor_count=mentor_count,
                           feedback_report=feedback_report,
                           # Note: The 'verify_career_report' endpoint is defined below
                           verify_career_report=url_for('verify_career_report')
                          )

@app.route('/admin/approve/<mentor_id>', methods=['POST'])
@role_required('Admin')
def approve_mentor(mentor_id):
    if DATA_SERVICE.approve_mentor(mentor_id):
        flash(f'Mentor {mentor_id} approved and moved to active list.', 'success')
    else:
        flash(f'Error: Mentor {mentor_id} not found in approval queue.', 'error')
    return redirect(url_for('admin_dashboard'))

# --- FIX: ADD MISSING ROUTE ---
@app.route('/admin/career/verify')
@role_required('Admin')
def verify_career_report():
    """
    Simulated route for the Admin to verify a career report.
    This route name ('verify_career_report') is required by the admin_dashboard.html template.
    """
    # In a real application, this would render a form to verify the report.
    # For now, we simulate success and redirect.
    flash("Career report verification simulated successfully.", 'success')
    return redirect(url_for('admin_dashboard'))
# --- END FIX ---


# --- MENTOR ROUTES ---

@app.route('/mentor/dashboard')
@role_required('Mentor')
def mentor_dashboard():
    mentor_id = session.get('user_id', 'mnt_001')
    all_students = DATA_SERVICE.get_all_students()

    # Simple simulation: all students are 'my students' for this basic app
    my_students = list(all_students.values())

    return render_template('mentor_dashboard.html',
                           my_students=my_students,
                           session_requests=DATA_SERVICE.data['session_requests'].values(),
                           upload_marks=url_for('upload_marks'),
                           mentor_session=url_for('mentor_session', session_id='sess_001')
                          )


@app.route('/mentor/upload-marks', methods=['GET', 'POST'])
@role_required('Mentor')
def upload_marks():
    if request.method == 'POST':
        file = request.files.get('file')

        if file and file.filename.endswith(('.csv', '.xlsx', '.xls')):
            try:
                # 1. Read the file into a Pandas DataFrame
                if file.filename.endswith('.csv'):
                    # Convert FileStorage object to a stream for Pandas to read
                    file_stream = StringIO(file.read().decode('utf-8'))
                    df = pd.read_csv(file_stream)
                elif file.filename.endswith(('.xlsx', '.xls')):
                    # Pandas read_excel handles both .xlsx and .xls
                    df = pd.read_excel(file)

                # 2. Process the data and update DataService
                # NOTE: Your CSV/Excel MUST have columns: student_id, subject, mark
                processed_count = DATA_SERVICE.update_marks_from_df(df)

                flash(f'Successfully updated marks for {processed_count} students.', 'success')
                return redirect(url_for('mentor_dashboard'))

            except ValueError as ve:
                flash(f'Error in file data: {str(ve)}', 'error')
                return redirect(request.url)
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
                return redirect(request.url)

        flash('Invalid file format. Please upload a CSV, XLSX, or XLS file.', 'error')
        return redirect(request.url)

    return render_template('mentor_upload.html')


@app.route('/mentor/session/<session_id>', methods=['GET', 'POST'])
@role_required('Mentor')
def mentor_session(session_id):
    session_request = DATA_SERVICE.get_session_request(session_id)
    if not session_request:
        abort(404)

    # Use the student_id from the session request data
    student_id = session_request.get('student_id', 'std_001')
    student_data = DATA_SERVICE.get_student_data(student_id)

    assessment_questions = [
        {'id': 1, 'text': 'What specific area of the student\'s marks is the highest priority for intervention?'},
        {'id': 2, 'text': 'Describe the student\'s primary motivation and learning style based on their history.'},
        {'id': 3, 'text': 'What is your proposed 3-step action plan for this session?'}
    ]

    ai_tips = None
    if request.method == 'POST':
        # Collect mentor's form data prefixed with 'mentor_assessment'
        mentor_assessment = {k: v for k, v in request.form.items() if k.startswith('mentor_assessment')}
        ai_tips = ADVISOR.generate_session_tips(student_data, mentor_assessment)

    return render_template('mentor_session.html',
                           student=student_data,
                           questions=assessment_questions,
                           ai_tips=ai_tips,
                           session_request=session_request)


# --- STUDENT ROUTES ---

@app.route('/student/portal')
@role_required('Student')
def student_portal():
    student_id = session.get('user_id', 'std_001')
    student = DATA_SERVICE.get_student_data(student_id)

    marks_data = student.get('marks', [])

    # Use the AI Matcher to find the best mentor recommendation
    # FIX: Implemented logic to call the MATCHER
    recommended_mentor_id = MATCHER.match_student_to_mentor(student_id)
    recommended_mentor = DATA_SERVICE.get_all_mentors().get(recommended_mentor_id, {'name': 'No Match Found', 'expertise': 'N/A'})

    # Check for latest AI response to display
    last_response = session.pop('last_response', None)

    return render_template('student_portal.html',
                           student=student,
                           marks_data=marks_data,
                           recommended_mentor=recommended_mentor, # Pass mentor recommendation
                           last_response=last_response)

@app.route('/student/query', methods=['POST'])
@role_required('Student')
def student_query():
    query = request.form.get('query')

    if not query or len(query.strip()) < 5:
        flash("Please enter a longer query to get a helpful AI response.", 'warning')
        return redirect(url_for('student_portal'))

    response_text = ADVISOR.suggest_resources(query)

    # Save the response to session to display on the next portal load
    session['last_response'] = response_text
    # Optionally update the student's last query in the data service
    DATA_SERVICE.data['students'][session.get('user_id', 'std_001')]['last_query'] = query

    return redirect(url_for('student_portal'))

@app.route('/student/submit-feedback', methods=['POST'])
@role_required('Student')
def submit_student_feedback():
    mentor_id = request.form.get('mentor_id')
    subject = request.form.get('subject')
    rating = request.form.get('rating')

    if mentor_id and subject and rating:
        try:
            DATA_SERVICE.save_anonymous_feedback(subject, rating, mentor_id)
            flash("Thank you! Your anonymous feedback has been submitted.", 'success')
        except Exception as e:
            print(f"Error saving feedback: {e}")
            flash("An error occurred while submitting feedback.", 'error')
    else:
        flash("All fields are required for feedback submission.", 'warning')

    return redirect(url_for('student_portal'))

@app.route('/student/career/assess', methods=['GET', 'POST'])
@role_required('Student')
def career_assess():
    assessment_questions = [
        {'id': 1, 'text': 'I enjoy breaking down complex problems into smaller, manageable tasks.'},
        {'id': 2, 'text': 'I prefer working independently over collaborating in a large group.'},
        {'id': 3, 'text': 'I find satisfaction in creating tangible products or visual designs.'},
        {'id': 4, 'text': 'I am comfortable with uncertainty and ambiguity in project outcomes.'},
        {'id': 5, 'text': 'My best subject is the one that involves critical analysis and reasoning.'},
    ]

    if request.method == 'POST':
        assessment_data = request.form

        # Simple check to ensure all questions were answered
        if len(assessment_data) != len(assessment_questions):
             flash("Please ensure you answer all assessment questions.", 'warning')
             return render_template('student_career.html', questions=assessment_questions)

        initial_report_content = ADVISOR.analyze_career_path(assessment_data)

        student_id = session.get('user_id', 'std_001')
        DATA_SERVICE.data['career_reports'][student_id] = {
            'status': 'pending_verification',
            'content': initial_report_content
        }
        flash("Career assessment submitted. Your report is pending mentor verification.", 'info')
        return redirect(url_for('career_report'))

    return render_template('student_career.html', questions=assessment_questions)

@app.route('/student/career/report')
@role_required('Student')
def career_report():
    student_id = session.get('user_id', 'std_001')

    report_data = DATA_SERVICE.get_career_report(student_id)
    status = report_data['status']

    is_verified = (status == 'verified')

    if status == 'not_started':
        message = "Career assessment not yet submitted. <a href='{}' class='underline'>Start assessment now</a>.".format(url_for('career_assess'))
    elif status == 'pending_verification':
        message = "Your AI report is ready and awaiting Mentor verification."
    elif status == 'verified':
        message = "Your **Verified Career Path Report** is ready!"
    else:
        message = "Report Status Unknown."

    content = report_data.get('content', 'Report content placeholder.')

    return render_template('student_career_report.html',
                           is_verified=is_verified,
                           message=message,
                           report_content=content)


if __name__ == '__main__':
    # Using host='0.0.0.0' for broader access if run in a container/VM
    app.run(debug=True, host='0.0.0.0')
