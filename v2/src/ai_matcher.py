import json

class AIMatcher:
    """
    Implements a keyword-based matching system to pair students with the most
    relevant mentor based on student needs and mentor expertise.
    """
    def __init__(self, data_service):
        self.data_service = data_service
        print("AI Matcher Initialized. Ready to match students.")

    def match_student_to_mentor(self, student_id):
        """
        Calculates a compatibility score based on shared keywords.
        Uses student's 'weakness_areas' against mentor's 'expertise'.
        """
        student = self.data_service.get_student_data(student_id)
        mentors = self.data_service.get_all_mentors()

        if not student or not mentors:
            return None # Cannot match if data is missing

        # 1. Prepare student keywords (e.g., "physics, algebra")
        student_keywords = set(
            kw.strip().lower()
            for kw in student.get('weakness_areas', '').replace(',', ' ').split()
            if kw.strip() # Remove empty strings
        )

        best_match_id = None
        highest_score = -1

        for mentor_id, mentor_data in mentors.items():
            mentor_expertise = set(
                exp.strip().lower()
                for exp in mentor_data.get('expertise', '').replace(',', ' ').split()
                if exp.strip()
            )

            # 2. Calculate match score: count of intersecting keywords
            match_score = len(student_keywords.intersection(mentor_expertise))

            # 3. Select the mentor with the highest score
            if match_score > highest_score:
                highest_score = match_score
                best_match_id = mentor_id

        return best_match_id or list(mentors.keys())[0] # Fallback to first mentor if no match found
