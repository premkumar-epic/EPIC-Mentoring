import json
import os
import uuid
from datetime import datetime

class DataService:
    def __init__(self, data_dir='src/data'):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.files = {
            'students': os.path.join(data_dir, 'students.json'),
            'mentors': os.path.join(data_dir, 'mentors.json'),
            'approval_queue': os.path.join(data_dir, 'mentor_approval_queue.json'),
            'feedback': os.path.join(data_dir, 'anonymous_feedback.json') # New file for anonymous feedback
        }
        self._initialize_files()

    def _initialize_files(self):
        """Ensure all data files exist with an empty dictionary if they are missing."""
        for file_path in self.files.values():
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({}, f)

    def _load_data(self, key):
        """Loads data from a specified JSON file."""
        with open(self.files[key], 'r') as f:
            return json.load(f)

    def _save_data(self, key, data):
        """Saves data to a specified JSON file."""
        with open(self.files[key], 'w') as f:
            json.dump(data, f, indent=4)

    # --- Public Methods for Application Logic ---

    def get_all_mentors(self):
        return self._load_data('mentors')

    def get_all_students(self):
        return self._load_data('students')

    def get_mentor_approval_queue(self):
        return self._load_data('approval_queue')

    def approve_mentor(self, mentor_id):
        """Moves a mentor from the queue to the active mentors list."""
        queue = self._load_data('approval_queue')
        mentor_data = queue.pop(mentor_id, None)

        if mentor_data:
            mentors = self._load_data('mentors')
            mentors[mentor_id] = mentor_data
            self._save_data('mentors', mentors)
            self._save_data('approval_queue', queue)
            return True
        return False

    def save_anonymous_feedback(self, subject, rating, mentor_id):
        """Saves anonymous student feedback."""
        feedback = self._load_data('feedback')
        feedback_id = str(uuid.uuid4())

        feedback[feedback_id] = {
            'timestamp': datetime.now().isoformat(),
            'subject': subject,
            'rating': rating,
            'mentor_id': mentor_id,
            'status': 'new'
        }
        self._save_data('feedback', feedback)

    def get_student_data(self, student_id):
        return self._load_data('students').get(student_id)

    # NOTE: You would add methods here for updating student marks,
    # saving session reports, and updating career report status.
