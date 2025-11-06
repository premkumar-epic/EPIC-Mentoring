import functools
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, abort, flash, jsonify
from flask_cors import CORS
import os
import pandas as pd
from io import StringIO
# --- (AIMatcher, RankingEngine, LLMAdvisor, DataService remain unchanged) ---

# --------------------------
# Simulated AI components (placeholders)
# --------------------------
# (Existing AIMatcher, RankingEngine, LLMAdvisor classes here...)
class AIMatcher:
    def __init__(self, data_service=None): self.ds = data_service
    def match_student_to_mentor(self, student_id): return "mnt_001"

class RankingEngine:
    def __init__(self, data_service=None): self.ds = data_service
    def generate_performance_report(self): return {}

class LLMAdvisor:
    def __init__(self): pass
    def suggest_resources(self, query):
        return "<p>[SIMULATED ADVICE] Read chapters 1-3 and practice problems.</p>"
    def generate_session_tips(self, student_data, mentor_assessment):
        return "<p>Session tips: focus on core concepts and exercises.</p>"
    def analyze_career_path(self, assessment_data):
        return "<p>Suggested careers: Data Science, Engineering.</p>"

# --------------------------
# Data service (in-memory)
# --------------------------
INITIAL_DATA = {
    "students": {
        "std_001": {"id": "std_001", "name": "Alice Smith", "marks": [{"subject":"Math","mark":75},{"subject":"Physics","mark":58}], "weakness_areas":"Physics,Algebra","last_query":""},
        "std_002": {"id": "std_002", "name": "Bob Johnson", "marks": [{"subject":"Chemistry","mark":92}], "weakness_areas":"Organic Chemistry","last_query":""}
    },
    "mentors": {
        "mnt_001": {"id":"mnt_001","name":"Prof. John Doe","expertise":"Physics,Calculus"}
    },
    "approval_queue": {
        "mnt_002": {"id":"mnt_002","name":"Dr. Jane Roe","expertise":"Calculus,Economics","submitted_date":"2025-11-01"}
    },
    "session_requests": {
        "sess_001": {"id":"sess_001","student_name":"Alice Smith","student_id":"std_001","query":"Need help with calculus."}
    },
    "feedback_report": {},
    "career_reports": {},
    "anonymous_feedback": {}
}

# (Existing DataService class here...)
class DataService:
    def __init__(self, data): self.data = data
    def get_all_students(self): return self.data["students"]
    def get_all_mentors(self): return self.data["mentors"]
    def get_mentor_approval_queue(self): return self.data["approval_queue"]
    def approve_mentor(self, mid):
        item = self.data["approval_queue"].pop(mid, None)
        if item: self.data["mentors"][mid] = item; return True
        return False
    def save_anonymous_feedback(self, subject, rating, mentor_id):
        fid = str(uuid.uuid4())
        self.data["anonymous_feedback"][fid] = {"timestamp": datetime.now().isoformat(), "subject":subject, "rating": int(rating), "mentor_id":mentor_id, "status":"new"}
    def get_student_data(self, sid): return self.data["students"].get(sid, {})
    def get_session_request(self, sessid): return self.data["session_requests"].get(sessid)
    def get_career_report(self, sid): return self.data["career_reports"].get(sid, {"status":"not_started","content":None})
    def update_marks_from_df(self, df):
        req = ['student_id','subject','mark']
        if not all(c in df.columns for c in req):
            raise ValueError("CSV must contain columns: student_id, subject, mark.")
        updated = set()
        for _, row in df.iterrows():
            sid = str(row['student_id']).strip()
            subj = str(row['subject']).strip()
            try:
                mark = int(row['mark'])
            except:
                continue
            if sid in self.data['students']:
                student = self.data['students'][sid]
                found=False
                if 'marks' not in student: student['marks']=[]
                for m in student['marks']:
                    if m['subject']==subj:
                        m['mark']=mark; found=True; break
                if not found: student['marks'].append({'subject':subj,'mark':mark})
                updated.add(sid)
        return len(updated)


# --------------------------
# Flask app setup
# --------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','devsecret')
# app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY','jwtdevsecret') # REMOVE JWT Config
# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2) # REMOVE JWT Config
CORS(app)

# Init services
DATA_SERVICE = DataService(INITIAL_DATA)
MATCHER = AIMatcher(DATA_SERVICE)
RANKER = RankingEngine(DATA_SERVICE)
ADVISOR = LLMAdvisor()

# Simple user store for session
USERS = {"admin":{"password":"admin123","role":"Admin","id":"adm_001"},
         "mentor":{"password":"mentor123","role":"Mentor","id":"mnt_001"},
         "student":{"password":"student123","role":"Student","id":"std_001"}}

# --------------------------
# Session-based login for templates (form)
# --------------------------
# REMOVE api_login route

@app.route('/')
def home():
    # If logged in, redirect to their dashboard
    if 'user_role' in session:
        role = session['user_role']
        if role == 'Admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'Mentor':
            return redirect(url_for('mentor_dashboard'))
        elif role == 'Student':
            return redirect(url_for('student_dashboard'))
    # If not logged in, go to login page
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear() # Clear session on GET, or before setting new session on POST
    if request.method == 'POST':
        username = request.form.get('username')
        role = request.form.get('role')

        # Simple check: If username is in USERS and role matches, log in.
        # This replaces the complex login in the previous app.py.
        user = USERS.get(username)
        if user and user['role'] == role:
            session['username'] = username
            session['user_role'] = role
            # The user_id is crucial for data lookups
            session['user_id'] = user['id']

            if role == 'Admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'Mentor':
                return redirect(url_for('mentor_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))

        flash('Invalid username or role selected. Use student/mentor/admin for username.','error')
        # Re-render the login page on failure
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def role_required(role):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # Updated simple role check
            if session.get('user_role')!=role:
                flash('Access denied. Please login with correct role.','error')
                return redirect(url_for('login'))
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# --------------------------
# Admin routes (Updated to match new route: /admin)
# --------------------------
@app.route('/admin') # Changed route
@role_required('Admin')
def admin_dashboard():
    queue = DATA_SERVICE.get_mentor_approval_queue()
    mentors = DATA_SERVICE.get_all_mentors()
    feedback = DATA_SERVICE.data.get('feedback_report', {})
    # Pass username for the new template
    return render_template('admin_dashboard.html', username=session.get('username'), mentor_queue=queue, mentor_count=len(mentors), feedback_report=feedback)

@app.route('/admin/approve/<mentor_id>', methods=['POST'])
@role_required('Admin')
def admin_approve(mentor_id):
    ok = DATA_SERVICE.approve_mentor(mentor_id)
    flash('Mentor approved.' if ok else 'Mentor not found.','info')
    return redirect(url_for('admin_dashboard'))

# --------------------------
# Mentor routes (Updated to match new route: /mentor)
# --------------------------
@app.route('/mentor') # Changed route
@role_required('Mentor')
def mentor_dashboard():
    students = DATA_SERVICE.get_all_students()
    sessions = DATA_SERVICE.data.get('session_requests',{}).values()
    # Pass username for the new template
    return render_template('mentor_dashboard.html', username=session.get('username'), my_students=students.values(), session_requests=sessions)

@app.route('/mentor/upload-marks', methods=['GET','POST'])
@role_required('Mentor')
def mentor_upload_marks():
    if request.method=='POST':
        file = request.files.get('file')
        if not file:
            flash('No file uploaded','error'); return redirect(request.url)
        fname = file.filename.lower()
        try:
            if fname.endswith('.csv'):
                stream = StringIO(file.read().decode('utf-8'))
                df = pd.read_csv(stream)
            else:
                df = pd.read_excel(file)
            count = DATA_SERVICE.update_marks_from_df(df)
            flash(f'Successfully updated marks for {count} students','success')
            return redirect(url_for('mentor_dashboard'))
        except ValueError as ve:
            flash(str(ve),'error'); return redirect(request.url)
        except Exception as e:
            flash('Error processing file: '+str(e),'error'); return redirect(request.url)
    return render_template('mentor_upload.html')

@app.route('/mentor/session/<session_id>', methods=['GET','POST'])
@role_required('Mentor')
def mentor_session(session_id):
    sess = DATA_SERVICE.get_session_request(session_id)
    if not sess: abort(404)
    # The user_id is pulled from the session, not hardcoded 'std_001'
    student = DATA_SERVICE.get_student_data(sess.get('student_id',session.get('user_id','std_001')))
    ai_tips = None
    if request.method=='POST':
        mentor_assessment = {k:v for k,v in request.form.items() if k.startswith('mentor_assessment')}
        ai_tips = ADVISOR.generate_session_tips(student, mentor_assessment)
    return render_template('mentor_session.html', student=student, questions=[], ai_tips=ai_tips, session_request=sess)

# --------------------------
# Student routes (Updated to match new route: /student)
# --------------------------
@app.route('/student') # Changed route and function name
@role_required('Student')
def student_dashboard():
    sid = session.get('user_id','std_001')
    student = DATA_SERVICE.get_student_data(sid)
    recommended_id = MATCHER.match_student_to_mentor(sid)
    recommended = DATA_SERVICE.get_all_mentors().get(recommended_id, {'name':'No Match'})
    last = session.pop('last_response', None)
    # The new template is student_dashboard.html, not student_portal.html
    return render_template('student_dashboard.html', username=session.get('username'), student=student, marks=student.get('marks',[]), recommended_mentor=recommended, last_response=last)


@app.route('/student/query', methods=['POST'])
@role_required('Student')
def student_query():
    q = request.form.get('query','').strip()
    if not q or len(q)<5:
        flash('Please enter a longer query','warning'); return redirect(url_for('student_dashboard')) # Updated redirect
    resp = ADVISOR.suggest_resources(q)
    session['last_response'] = resp
    DATA_SERVICE.data['students'][session.get('user_id','std_001')]['last_query']=q
    return redirect(url_for('student_dashboard')) # Updated redirect

@app.route('/student/submit-feedback', methods=['POST'])
@role_required('Student')
def student_feedback():
    mentor_id = request.form.get('mentor_id'); subject = request.form.get('subject'); rating = request.form.get('rating')
    if not (mentor_id and subject and rating):
        flash('All fields required','warning'); return redirect(url_for('student_dashboard')) # Updated redirect
    try:
        DATA_SERVICE.save_anonymous_feedback(subject, rating, mentor_id)
        flash('Feedback submitted','success')
    except Exception as e:
        flash('Error saving feedback','error')
    return redirect(url_for('student_dashboard')) # Updated redirect

@app.route('/student/career/assess', methods=['GET','POST'])
@role_required('Student')
def career_assess():
    questions = [
        'I enjoy breaking down complex problems into smaller tasks.',
        'I prefer working independently.',
        'I like creating tangible products.',
        'I am comfortable with ambiguity.',
        'My best subject involves critical analysis.'
    ]
    if request.method=='POST':
        data = request.form
        if len(data)!=len(questions):
            flash('Please answer all questions','warning'); return render_template('student_career.html', questions=questions)
        report = ADVISOR.analyze_career_path(data)
        sid = session.get('user_id','std_001')
        DATA_SERVICE.data['career_reports'][sid]={'status':'pending_verification','content':report}
        flash('Assessment submitted, pending verification','info'); return redirect(url_for('career_report'))
    return render_template('student_career.html', questions=questions)

@app.route('/student/career/report')
@role_required('Student')
def career_report():
    sid = session.get('user_id','std_001')
    report = DATA_SERVICE.get_career_report(sid)
    status = report.get('status','not_started')
    content = report.get('content','No content yet.')
    return render_template('student_career_report.html', status=status, content=content)

# --------------------------
# Health
# --------------------------
@app.route('/health')
def health(): return jsonify({'status':'ok'}), 200

# The home route is already correct and redirects to the new dashboards

if __name__=='__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
