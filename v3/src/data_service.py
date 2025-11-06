import pandas as pd
import json
import os
import io

class DataService:
    def __init__(self, data_dir='src/data'):
        self.data_dir = data_dir
        self.students_file = os.path.join(data_dir, 'students.json')
        self.mentors_file = os.path.join(data_dir, 'mentors.json')
        self.feedback_file = os.path.join(data_dir, 'feedback_data.csv')
        self.students_df = self._load_students()
        self.mentors_df = self._load_mentors()
        self.feedback_df = self._load_feedback()

        # Initialize student data with all necessary columns
        if 'student_id' not in self.students_df.columns:
            self.students_df['student_id'] = [f'std_{i+1:03}' for i in range(len(self.students_df))]

        # KEY CHANGE: New field to track human verification status for Career Path
        if 'is_verified' not in self.students_df.columns:
            self.students_df['is_verified'] = False

        # Ensure is_verified is boolean type
        self.students_df['is_verified'] = self.students_df['is_verified'].astype(bool)

        self.users = self._load_users()

    def _load_students(self):
        try:
            with open(self.students_file, 'r') as f:
                data = json.load(f)
            return pd.DataFrame(data)
        except (FileNotFoundError, json.JSONDecodeError):
            return pd.DataFrame()

    def _load_mentors(self):
        try:
            with open(self.mentors_file, 'r') as f:
                data = json.load(f)
            return pd.DataFrame(data)
        except FileNotFoundError:
            # Create mock data if file not found
            data = [
                {"mentor_id": "men_001", "name": "Dr. Aris Thorne", "email": "aris@mentor.edu", "password": "mentor_pass"},
                {"mentor_id": "men_002", "name": "Prof. Lena Vaziri", "email": "lena@mentor.edu", "password": "mentor_pass"},
                {"mentor_id": "men_003", "name": "Ms. Chloe O'Brien", "email": "chloe@mentor.edu", "password": "mentor_pass"},
            ]
            return pd.DataFrame(data)

    def _load_feedback(self):
        try:
            return pd.read_csv(self.feedback_file)
        except FileNotFoundError:
            return pd.DataFrame(columns=['session_id', 'student_id', 'mentor_id', 'date', 'score'])

    def _load_users(self):
        # Admin is hardcoded
        users = {
            'admin': {'password': 'admin_pass', 'role': 'admin', 'id': 'adm_001'}
        }

        # Load mentors
        for _, row in self.mentors_df.iterrows():
            users[row['email']] = {
                'password': row['password'],
                'role': 'mentor',
                'id': row['mentor_id']
            }

        # Load students
        for _, row in self.students_df.iterrows():
            users[row['student_id']] = {
                'password': row['student_id'] + '_pass', # Mock password based on ID
                'role': 'student',
                'id': row['student_id']
            }
        return users

    def get_user(self, username):
        return self.users.get(username)

    def get_all_students(self):
        return self.students_df.to_dict('records')

    def get_student_by_id(self, student_id):
        student_data = self.students_df[self.students_df['student_id'] == student_id]
        if not student_data.empty:
            return student_data.iloc[0].to_dict()
        return None

    def update_student_data(self, updated_df):
        # Ensure 'is_verified' is carried over if not present in the new data
        if 'is_verified' not in updated_df.columns and 'is_verified' in self.students_df.columns:
             updated_df = pd.merge(updated_df, self.students_df[['student_id', 'is_verified']], on='student_id', how='left')

        self.students_df = updated_df
        self.students_df['is_verified'] = self.students_df['is_verified'].fillna(False).astype(bool)
        # Save the updated DataFrame back to students.json
        self._save_students()
        # Reload users to update any potentially changed student info
        self.users = self._load_users()

    def _save_students(self):
        # Save DataFrame to JSON file with the 'is_verified' flag
        self.students_df.to_json(self.students_file, orient='records', indent=4)

    def update_feedback(self, new_feedback):
        self.feedback_df = pd.concat([self.feedback_df, pd.DataFrame([new_feedback])], ignore_index=True)
        self.feedback_df.to_csv(self.feedback_file, index=False)

    def get_feedback(self):
        return self.feedback_df

    def get_mentor_students(self, mentor_id):
        # This is a mock function, assuming a mentor has a list of student IDs
        if mentor_id == 'men_001':
            assigned_ids = self.students_df['student_id'].head(5).tolist()
        elif mentor_id == 'men_002':
            assigned_ids = self.students_df['student_id'].tail(5).tolist()
        else:
            assigned_ids = []

        return self.students_df[self.students_df['student_id'].isin(assigned_ids)].to_dict('records')

    # KEY CHANGE: New method to set verification status
    def verify_student_report(self, student_id):
        """Sets the is_verified flag for a student to True."""
        try:
            self.students_df.loc[self.students_df['student_id'] == student_id, 'is_verified'] = True
            self._save_students()
            print(f"Report for {student_id} verified successfully.")
            return True
        except Exception as e:
            print(f"Error verifying report for {student_id}: {e}")
            return False

    def get_all_mentors(self):
        return self.mentors_df.to_dict('records')

    def load_data_from_upload(self, file_storage):
        # Read the file data into a Pandas DataFrame
        if file_storage.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(file_storage.stream.read().decode("UTF8")))
        elif file_storage.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_storage.stream)
        else:
            raise ValueError("Unsupported file type.")

        # Ensure the uploaded DataFrame has the expected columns for merging
        expected_columns = ['student_id', 'math_marks', 'science_marks', 'english_marks', 'psychometric_score']
        if not all(col in df.columns for col in expected_columns):
            missing = [col for col in expected_columns if col not in df.columns]
            raise ValueError(f"Missing required columns in upload file: {', '.join(missing)}")

        # Merge the uploaded data with the existing student data
        cols_to_drop = [col for col in self.students_df.columns if col in expected_columns[1:]]
        temp_df = self.students_df.drop(columns=cols_to_drop, errors='ignore')

        merged_df = pd.merge(temp_df, df, on='student_id', how='left', suffixes=('_old', '_new'))

        self.update_student_data(merged_df)

        return len(df)
