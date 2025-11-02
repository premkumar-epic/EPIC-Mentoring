import json
import chromadb
from sentence_transformers import SentenceTransformer
import os

# --- Configuration ---
MODEL_NAME = 'all-MiniLM-L6-v2'
COLLECTION_NAME = "mentor_profiles"
DB_PATH = "./chroma_db"
DATA_PATH = "src/data/mentors.json"

class AIMatcher:
    """Handles mentor profile indexing (embedding) and semantic matching."""
    def __init__(self):
        # 1. Load the open-source Sentence Transformer Model
        self.model = SentenceTransformer(MODEL_NAME)

        # 2. Initialize Chroma Vector Database Client
        self.client = chromadb.PersistentClient(path=DB_PATH)
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)

        print(f"Matcher initialized. Model: {MODEL_NAME}")

    def index_mentors(self):
        """Loads data, generates embeddings, and indexes them in ChromaDB."""
        try:
            with open(DATA_PATH, 'r') as f:
                mentors = json.load(f)
        except Exception as e:
            print(f"Error loading mentors data: {e}")
            return

        # Prepare data for batch processing
        mentor_texts = []
        mentor_ids = []
        metadata_list = []

        for mentor in mentors:
            # Combine relevant fields into a single text for embedding
            full_text = f"Expertise: {mentor['expertise']}. Description: {mentor['description']}"

            mentor_texts.append(full_text)
            mentor_ids.append(mentor['id'])

            # Store original data as metadata
            metadata_list.append({
                "id": mentor['id'],
                "name": mentor['name'],
                "expertise": mentor['expertise'],
                "description": mentor['description']
            })

        # Generate embeddings in a single batch
        embeddings = self.model.encode(mentor_texts).tolist()

        # Add data to the Chroma collection (resets/overwrites if IDs exist)
        self.collection.upsert(
            embeddings=embeddings,
            documents=mentor_texts,
            metadatas=metadata_list,
            ids=mentor_ids
        )
        print(f"Successfully indexed {len(mentors)} mentors into ChromaDB.")

    def find_matches(self, mentee_profile: str, n_results: int = 5):
        """Finds the top N semantically closest mentors."""
        if not self.collection.count():
            print("ChromaDB is empty. Please run index_mentors first.")
            return []

        # Generate the mentee profile embedding
        query_embedding = self.model.encode([mentee_profile]).tolist()

        # Query the Vector Database
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=['metadatas', 'distances']
        )

        matches = []
        if results and results['ids']:
            for metadata, distance in zip(results['metadatas'][0], results['distances'][0]):
                match = {
                    "id": metadata['id'],
                    "name": metadata['name'],
                    "expertise": metadata['expertise'],
                    "description": metadata['description'],
                    "vector_distance": distance # The initial semantic score (lower is better)
                }
                matches.append(match)

        return matches

# Example usage (will be used by app.py)
if __name__ == '__main__':
    matcher = AIMatcher()
    matcher.index_mentors()

    mentee_query = "I need a mentor to help me with my startup's NLP product. Focus on production deployment of a custom transformer model."
    top_matches = matcher.find_matches(mentee_query, n_results=3)

    print("\n--- Initial Semantic Matches ---")
    for match in top_matches:
        print(f"Match: {match['name']}, Distance: {match['vector_distance']:.4f}")
