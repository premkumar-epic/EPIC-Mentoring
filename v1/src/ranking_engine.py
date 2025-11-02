import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import numpy as np
import os

FEEDBACK_FILE = "src/data/feedback_data.csv"

class RankingEngine:
    """Handles training and application of a custom Scikit-learn ranker."""
    def __init__(self):
        self.model = None
        self.feedback_data = self._load_data()

    def _load_data(self):
        """Loads or initializes the feedback DataFrame."""
        if os.path.exists(FEEDBACK_FILE):
            print("Loaded historical feedback data.")
            return pd.read_csv(FEEDBACK_FILE)
        else:
            print("No feedback data found. Initializing empty dataset.")
            # Define columns for the feedback loop
            return pd.DataFrame(columns=['mentor_id', 'mentee_query', 'vector_distance', 'success_rating'])

    def add_feedback(self, mentor_id, mentee_query, vector_distance, success_rating):
        """Adds a new feedback entry to the in-memory data and saves it."""
        new_entry = pd.DataFrame([{
            'mentor_id': mentor_id,
            'mentee_query': mentee_query,
            'vector_distance': vector_distance,
            'success_rating': success_rating
        }])

        # Success_rating > 3.0 is a binary 'success' (1)
        new_entry['success'] = np.where(new_entry['success_rating'] >= 4, 1, 0)

        self.feedback_data = pd.concat([self.feedback_data, new_entry], ignore_index=True)
        self.feedback_data.to_csv(FEEDBACK_FILE, index=False)
        print(f"Feedback added and saved. Total entries: {len(self.feedback_data)}")

    def train_ranker(self):
        """Trains a Logistic Regression model to predict match success."""

        # --- FIX: Force a reload of the saved data before checking the count ---
        self.feedback_data = self._load_data()
        # ---------------------------------------------------------------------

        if len(self.feedback_data) < 10:
            print("Not enough feedback data (need min 10) to train the ranker.")
            return False

        # Target variable: success (1 or 0)
        X = self.feedback_data[['vector_distance']]
        y = self.feedback_data['success']

        # Splitting data (simple for this example)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Use a simple classifier (Logistic Regression) as the ranker
        self.model = LogisticRegression()
        self.model.fit(X_train, y_train)

        score = self.model.score(X_test, y_test)
        print(f"Ranking Model Trained! Accuracy on test set: {score:.2f}")
        return True

    def apply_ranking(self, matches):
        """Applies the trained ranker to re-sort the initial matches."""
        if self.model is None:
            print("Ranker is not trained or data is insufficient. Returning initial matches.")
            return matches

        # Create a DataFrame from the initial matches
        df = pd.DataFrame(matches)

        # Get the new ranking score (probability of success)
        # We only use 'vector_distance' as the feature for simplicity
        ranking_scores = self.model.predict_proba(df[['vector_distance']])[:, 1]

        df['ranking_score'] = ranking_scores

        # Sort by the new score (highest probability of success first)
        df_ranked = df.sort_values(by='ranking_score', ascending=False)

        # Convert back to a list of dictionaries
        return df_ranked.to_dict('records')
