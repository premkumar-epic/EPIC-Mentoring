"""
Data Service Layer - Centralized in-memory data management
"""
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import csv
import io
import random
from collections import defaultdict

class DataService:
    """Manages all in-memory data structures"""

    def __init__(self):
        self.users = {}
        self.students = {}
        self.mentors = {}
        self.admins = {}
        self.sessions = {}
        self.marks = defaultdict(list)
        self.assessments = {}
        self.feedback = []
        self.recommendations = defaultdict(list)
        self._next_id = 1

        # Initialize with sample data
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Initialize with sample users for testing"""
        # Create admins
        admin_id = self.create_user('Admin User', 'admin@example.com', 'admin123', 'admin')
        if admin_id:
            self.admins[admin_id] = {'id': admin_id, 'user_id': admin_id}

        admin2_id = self.create_user('Super Admin', 'superadmin@example.com', 'admin456', 'admin')
        if admin2_id:
            self.admins[admin2_id] = {'id': admin2_id, 'user_id': admin2_id}

        # Create sample mentors
        mentor_id = self.create_user('Dr. Sarah Johnson', 'sarah@example.com', 'mentor123', 'mentor')
        if mentor_id:
            self.mentors[mentor_id] = {
                'id': mentor_id,
                'user_id': mentor_id,
                'expertise': ['Mathematics', 'Physics', 'Computer Science'],
                'status': 'approved',
                'rating': 4.5
            }

        mentor2_id = self.create_user('Prof. Michael Chen', 'michael@example.com', 'mentor456', 'mentor')
        if mentor2_id:
            self.mentors[mentor2_id] = {
                'id': mentor2_id,
                'user_id': mentor2_id,
                'expertise': ['Chemistry', 'Biology', 'Engineering'],
                'status': 'approved',
                'rating': 4.8
            }

        mentor3_id = self.create_user('Dr. Emily Rodriguez', 'emily@example.com', 'mentor789', 'mentor')
        if mentor3_id:
            self.mentors[mentor3_id] = {
                'id': mentor3_id,
                'user_id': mentor3_id,
                'expertise': ['Psychology', 'Sociology', 'Education'],
                'status': 'pending',
                'rating': 0.0
            }

        mentor4_id = self.create_user('Dr. Robert Williams', 'robert@example.com', 'mentor101', 'mentor')
        if mentor4_id:
            self.mentors[mentor4_id] = {
                'id': mentor4_id,
                'user_id': mentor4_id,
                'expertise': ['English', 'Literature', 'History'],
                'status': 'approved',
                'rating': 4.7
            }

        mentor5_id = self.create_user('Prof. Lisa Anderson', 'lisa@example.com', 'mentor202', 'mentor')
        if mentor5_id:
            self.mentors[mentor5_id] = {
                'id': mentor5_id,
                'user_id': mentor5_id,
                'expertise': ['Business', 'Economics', 'Finance'],
                'status': 'approved',
                'rating': 4.6
            }

        # Store mentor IDs for assignment
        approved_mentors = [mentor_id, mentor2_id, mentor4_id, mentor5_id]

        # Create 50 students with diverse data
        student_names = [
            'John Doe', 'Jane Smith', 'Alex Johnson', 'Emily Brown', 'Michael Davis',
            'Sarah Wilson', 'David Martinez', 'Jessica Taylor', 'Christopher Lee', 'Amanda White',
            'James Anderson', 'Ashley Thomas', 'Daniel Jackson', 'Nicole Harris', 'Matthew Clark',
            'Samantha Lewis', 'Joshua Walker', 'Olivia Hall', 'Andrew Young', 'Sophia Allen',
            'Ryan King', 'Isabella Wright', 'Kevin Lopez', 'Emma Hill', 'Brandon Scott',
            'Ava Green', 'Justin Adams', 'Mia Baker', 'Tyler Nelson', 'Chloe Carter',
            'Jacob Mitchell', 'Lily Perez', 'Nathan Roberts', 'Grace Turner', 'Ethan Phillips',
            'Ella Campbell', 'Noah Parker', 'Zoe Evans', 'Caleb Edwards', 'Layla Collins',
            'Logan Stewart', 'Aria Sanchez', 'Mason Morris', 'Hannah Rogers', 'Lucas Reed',
            'Aubrey Cook', 'Jackson Morgan', 'Scarlett Bell', 'Aiden Murphy', 'Victoria Bailey'
        ]

        subjects = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'English',
                   'History', 'Computer Science', 'Engineering', 'Literature', 'Economics']

        # Track which mentor to assign next
        mentor_index = 0

        # Create students
        for i, name in enumerate(student_names):
            email = f'student{i+1:03d}@example.com'
            password = f'student{i+1:03d}'

            # Create user
            student_id = self.create_user(name, email, password, 'student')

            if student_id:
                # Determine weaknesses and strengths (vary for diversity)
                random.seed(i)  # Use index for reproducible results
                all_subjects = subjects.copy()
                random.shuffle(all_subjects)

                weakness_count = 2 if i % 3 == 0 else (1 if i % 2 == 0 else 3)
                strength_count = 2 if i % 2 == 0 else 3

                weakness_areas = all_subjects[:weakness_count]
                strengths = all_subjects[weakness_count:weakness_count+strength_count]

                # Assign mentor (some students get mentors, some don't)
                assigned_mentor = None
                if i < 35 and approved_mentors:  # 35 students get mentors
                    assigned_mentor = approved_mentors[mentor_index % len(approved_mentors)]
                    mentor_index += 1

                self.students[student_id] = {
                    'id': student_id,
                    'user_id': student_id,
                    'weakness_areas': weakness_areas,
                    'strengths': strengths,
                    'mentor_id': assigned_mentor
                }

                # Add sample marks (3-5 subjects per student)
                num_marks = 3 + (i % 3)  # 3, 4, or 5 marks
                student_marks = []
                mark_date_base = datetime(2024, 9, 10)

                for j in range(num_marks):
                    subject_idx = (i + j) % len(subjects)
                    subject = subjects[subject_idx]

                    # Vary marks based on whether it's a strength or weakness
                    if subject in weakness_areas:
                        marks = 45 + (i % 25)  # 45-69 for weaknesses
                    elif subject in strengths:
                        marks = 75 + (i % 20)  # 75-94 for strengths
                    else:
                        marks = 60 + (i % 25)  # 60-84 for average

                    mark_date = (mark_date_base + timedelta(days=j*5)).strftime('%Y-%m-%d')
                    student_marks.append({
                        'subject': subject,
                        'marks': marks,
                        'semester': 'Fall 2024',
                        'date': mark_date
                    })

                self.marks[student_id] = student_marks

    def _get_next_id(self):
        """Generate next unique ID"""
        current = self._next_id
        self._next_id += 1
        return current

    def create_user(self, name, email, password, role):
        """Create a new user"""
        # Check if email exists
        for user in self.users.values():
            if user['email'] == email:
                return None

        user_id = self._get_next_id()
        self.users[user_id] = {
            'id': user_id,
            'name': name,
            'email': email,
            'password': generate_password_hash(password),
            'role': role,
            'created_at': datetime.now().isoformat()
        }

        if role == 'student':
            self.students[user_id] = {
                'id': user_id,
                'user_id': user_id,
                'weakness_areas': [],
                'strengths': [],
                'mentor_id': None
            }
        elif role == 'mentor':
            self.mentors[user_id] = {
                'id': user_id,
                'user_id': user_id,
                'expertise': [],
                'status': 'pending',
                'rating': 0.0
            }
        elif role == 'admin':
            self.admins[user_id] = {'id': user_id, 'user_id': user_id}

        return user_id

    def authenticate_user(self, email, password):
        """Authenticate user"""
        for user in self.users.values():
            if user['email'] == email and check_password_hash(user['password'], password):
                return user
        return None

    def get_student(self, student_id):
        """Get student data"""
        student = self.students.get(student_id, {})
        user = self.users.get(student_id, {})
        return {**student, **user}

    def get_mentor(self, mentor_id):
        """Get mentor data"""
        mentor = self.mentors.get(mentor_id, {})
        user = self.users.get(mentor_id, {})
        return {**mentor, **user}

    def get_student_performance(self, student_id):
        """Get student performance data"""
        marks_data = self.marks.get(student_id, [])

        # Calculate statistics
        total_marks = sum(m['marks'] for m in marks_data)
        avg_marks = total_marks / len(marks_data) if marks_data else 0

        subject_wise = defaultdict(list)
        for mark in marks_data:
            subject_wise[mark['subject']].append(mark)

        return {
            'marks': marks_data,
            'average': round(avg_marks, 2),
            'subject_wise': dict(subject_wise),
            'total_subjects': len(subject_wise)
        }

    def get_student_recommendations(self, student_id):
        """Get learning recommendations for student"""
        return self.recommendations.get(student_id, [])

    def save_assessment(self, student_id, assessment_data):
        """Save career assessment"""
        assessment_id = self._get_next_id()
        assessment_data['id'] = assessment_id
        assessment_data['student_id'] = student_id
        assessment_data['status'] = 'pending_verification'
        assessment_data['created_at'] = datetime.now().isoformat()
        self.assessments[assessment_id] = assessment_data
        return assessment_id

    def get_assessment(self, student_id, assessment_id):
        """Get assessment by ID"""
        assessment = self.assessments.get(int(assessment_id))
        if assessment and assessment['student_id'] == student_id:
            return assessment
        return None

    def get_mentor_students(self, mentor_id):
        """Get all students assigned to a mentor"""
        students = []
        for student_id, student in self.students.items():
            if student.get('mentor_id') == mentor_id:
                user = self.users.get(student_id, {})
                students.append({**student, **user})
        return students

    def get_upcoming_sessions(self, mentor_id):
        """Get upcoming sessions for mentor"""
        upcoming = []
        for session in self.sessions.values():
            if session['mentor_id'] == mentor_id:
                session_date = datetime.fromisoformat(session['date'])
                if session_date >= datetime.now():
                    student = self.get_student(session['student_id'])
                    upcoming.append({**session, 'student': student})
        return sorted(upcoming, key=lambda x: x['date'])

    def create_session(self, mentor_id, student_id, date, notes):
        """Create a mentoring session"""
        session_id = self._get_next_id()
        self.sessions[session_id] = {
            'id': session_id,
            'mentor_id': mentor_id,
            'student_id': int(student_id),
            'date': date,
            'notes': notes,
            'status': 'scheduled',
            'created_at': datetime.now().isoformat()
        }
        return session_id

    def get_mentor_sessions(self, mentor_id):
        """Get all sessions for a mentor"""
        sessions = []
        for session in self.sessions.values():
            if session['mentor_id'] == mentor_id:
                student = self.get_student(session['student_id'])
                sessions.append({**session, 'student': student})
        return sorted(sessions, key=lambda x: x['date'], reverse=True)

    def upload_marks_file(self, file):
        """Upload and process marks file (CSV)"""
        try:
            content = file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content))

            count = 0
            for row in csv_reader:
                student_id = int(row.get('student_id', 0))
                if student_id and student_id in self.students:
                    mark_entry = {
                        'subject': row.get('subject', ''),
                        'marks': int(row.get('marks', 0)),
                        'semester': row.get('semester', ''),
                        'date': row.get('date', datetime.now().strftime('%Y-%m-%d'))
                    }
                    self.marks[student_id].append(mark_entry)
                    count += 1

            return {'success': True, 'count': count}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_mentor_feedback(self, mentor_id):
        """Get feedback for a mentor"""
        feedback_list = []
        for feedback in self.feedback:
            if feedback.get('mentor_id') == mentor_id:
                feedback_list.append(feedback)
        return feedback_list

    def get_pending_mentors(self):
        """Get all pending mentor applications"""
        pending = []
        for mentor_id, mentor in self.mentors.items():
            if mentor.get('status') == 'pending':
                user = self.users.get(mentor_id, {})
                pending.append({**mentor, **user})
        return pending

    def approve_mentor(self, mentor_id):
        """Approve mentor application"""
        mentor_id = int(mentor_id)
        if mentor_id in self.mentors:
            self.mentors[mentor_id]['status'] = 'approved'

    def reject_mentor(self, mentor_id):
        """Reject mentor application"""
        mentor_id = int(mentor_id)
        if mentor_id in self.mentors:
            self.mentors[mentor_id]['status'] = 'rejected'

    def get_unmatched_students(self):
        """Get students without assigned mentors"""
        unmatched = []
        for student_id, student in self.students.items():
            if not student.get('mentor_id'):
                user = self.users.get(student_id, {})
                unmatched.append({**student, **user})
        return unmatched

    def get_available_mentors(self):
        """Get all approved mentors"""
        available = []
        for mentor_id, mentor in self.mentors.items():
            if mentor.get('status') == 'approved':
                user = self.users.get(mentor_id, {})
                available.append({**mentor, **user})
        return available

    def assign_mentor(self, student_id, mentor_id):
        """Assign mentor to student"""
        student_id = int(student_id)
        mentor_id = int(mentor_id)
        if student_id in self.students and mentor_id in self.mentors:
            self.students[student_id]['mentor_id'] = mentor_id

    def get_system_analytics(self):
        """Get system-wide analytics"""
        total_students = len(self.students)
        total_mentors = len([m for m in self.mentors.values() if m.get('status') == 'approved'])
        total_sessions = len(self.sessions)
        total_assessments = len(self.assessments)

        return {
            'total_students': total_students,
            'total_mentors': total_mentors,
            'total_sessions': total_sessions,
            'total_assessments': total_assessments,
            'active_mentorships': len([s for s in self.students.values() if s.get('mentor_id')]),
            'pending_mentors': len(self.get_pending_mentors())
        }

    def get_all_users(self):
        """Get all users"""
        return list(self.users.values())

