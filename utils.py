from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Initialize SentenceTransformer model
model = SentenceTransformer('bert-base-nli-mean-tokens')

def calculate_interest_similarity(user_interests, match_interests):
    # Encode user and match interests
    user_vectors = model.encode(user_interests)
    match_vectors = model.encode(match_interests)
    
    # Calculate cosine similarity between user and match interests
    similarity_matrix = cosine_similarity(user_vectors, match_vectors)
    
    # Return average similarity score
    return similarity_matrix.mean()
