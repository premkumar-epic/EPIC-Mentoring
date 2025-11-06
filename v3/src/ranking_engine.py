import pandas as pd
import numpy as np
import json
import os
from collections import defaultdict

class RankingEngine:
    """
    Analyzes anonymous student feedback to calculate mentor performance scores
    and generate the Admin's official Mentor Performance Report.
    """
    def __init__(self, data_service):
        self.data_service = data_service
        print("Ranking Engine Initialized. Ready to process feedback.")

    def _load_feedback_data(self):
        """Loads and prepares anonymous feedback data from the data service."""
        raw_feedback = self.data_service.data.get('anonymous_feedback', {})

        # Convert dictionary to a list of dictionaries for Pandas
        feedback_list = []
        for f_id, f_data in raw_feedback.items():
            feedback_list.append(f_data)

        if not feedback_list:
            # Return an empty DataFrame if no feedback exists
            return pd.DataFrame(columns=['mentor_id', 'rating', 'subject'])

        df = pd.DataFrame(feedback_list)
        # Ensure rating is treated as a numeric value
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        return df

    def generate_performance_report(self):
        """
        Calculates the weighted performance score for all mentors.

        The score is a simple average of feedback ratings, plus a bonus/penalty
        for volume/variance to simulate a real ML-based ranking.
        """
        df = self._load_feedback_data()

        if df.empty:
            return {"status": "No feedback yet to generate a report."}

        # 1. Calculate base average score per mentor
        mentor_stats = df.groupby('mentor_id').agg(
            average_rating=('rating', 'mean'),
            review_count=('rating', 'count'),
            rating_std=('rating', 'std')
        ).reset_index()

        # 2. Simulate a weighted ranking (Penalize low volume, reward high rating)
        MAX_REVIEWS = mentor_stats['review_count'].max()

        # Weighting factor: Scores with few reviews are pulled toward the mean (Bayesian average simulation)
        mentor_stats['weight'] = (mentor_stats['review_count'] / MAX_REVIEWS) * 0.2 + 0.8

        # Final Score: Base average adjusted by the number of reviews
        mentor_stats['final_score'] = (
            mentor_stats['average_rating'] * mentor_stats['weight']
        ).round(2)

        # 3. Compile the final report summary
        report = {}
        all_mentors = self.data_service.get_all_mentors()

        # Sort by final score to create the rank
        mentor_stats = mentor_stats.sort_values(by='final_score', ascending=False)
        mentor_stats['rank'] = np.arange(1, len(mentor_stats) + 1)

        for index, row in mentor_stats.iterrows():
            mentor_id = row['mentor_id']
            mentor_name = all_mentors.get(mentor_id, {}).get('name', f"Mentor {mentor_id}")

            report[mentor_name] = {
                "rank": int(row['rank']),
                "final_score": float(row['final_score']),
                "review_count": int(row['review_count']),
                "summary": f"Rank {int(row['rank'])}: Consistent performance across {int(row['review_count'])} reviews."
            }

        # 4. Update the DataService's in-memory report for the Admin Dashboard
        self.data_service.data['feedback_report'] = report

        return report
