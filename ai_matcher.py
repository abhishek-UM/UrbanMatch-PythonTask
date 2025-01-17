from typing import List, Dict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class AIMatcher:
    def __init__(self):
        # Predefined weights for different matching criteria
        self.weights = {
            'interests': 0.4,
            'age': 0.3,
            'location': 0.3
        }
        
        # Interest categories for better matching
        self.interest_categories = {
            'outdoor': ['hiking', 'nature', 'travel', 'sports', 'fitness'],
            'creative': ['art', 'music', 'writing', 'photography', 'theater'],
            'intellectual': ['reading', 'science', 'history', 'technology', 'languages'],
            'lifestyle': ['cooking', 'fashion', 'food', 'meditation', 'yoga'],
            'entertainment': ['movies', 'gaming', 'dancing', 'music', 'theater']
        }

    def calculate_interest_similarity(self, user1_interests: List[str], user2_interests: List[str]) -> float:
        """Calculate similarity between two users' interests using cosine similarity"""
        # Convert interests to lowercase for comparison
        user1_interests = [i.lower() for i in user1_interests]
        user2_interests = [i.lower() for i in user2_interests]
        
        # Create interest vectors
        all_categories = list(self.interest_categories.keys())
        user1_vector = self._create_interest_vector(user1_interests, all_categories)
        user2_vector = self._create_interest_vector(user2_interests, all_categories)
        
        # Calculate cosine similarity
        similarity = cosine_similarity([user1_vector], [user2_vector])[0][0]
        return float(similarity)

    def _create_interest_vector(self, interests: List[str], categories: List[str]) -> List[float]:
        """Create a vector representation of interests based on categories"""
        vector = []
        for category in categories:
            category_interests = self.interest_categories[category]
            score = sum(1 for interest in interests if interest in category_interests)
            vector.append(score / len(category_interests))
        return vector

    def calculate_age_compatibility(self, age1: int, age2: int) -> float:
        """Calculate age compatibility score"""
        age_diff = abs(age1 - age2)
        if age_diff <= 5:
            return 1.0
        elif age_diff <= 10:
            return 0.7
        elif age_diff <= 15:
            return 0.4
        else:
            return 0.2

    def calculate_location_match(self, location1: str, location2: str) -> float:
        """Calculate location match score"""
        # Simple exact match for now, could be enhanced with geographic distance
        return 1.0 if location1.lower() == location2.lower() else 0.0

    def find_matches(self, user: Dict, potential_matches: List[Dict], limit: int = 10) -> List[Dict]:
        """Find and rank matches for a user"""
        matches = []
        
        for potential_match in potential_matches:
            try:
                # Calculate individual scores
                interest_score = self.calculate_interest_similarity(
                    user['interests'],
                    potential_match['interests']
                )
                
                age_score = self.calculate_age_compatibility(
                    user['age'],
                    potential_match['age']
                )
                
                location_score = self.calculate_location_match(
                    user['location'],
                    potential_match['location']
                )
                
                # Calculate weighted total score
                total_score = (
                    interest_score * self.weights['interests'] +
                    age_score * self.weights['age'] +
                    location_score * self.weights['location']
                )
                
                # Calculate match reasons
                reasons = []
                if interest_score > 0.6:
                    common_interests = set(user['interests']) & set(potential_match['interests'])
                    reasons.append(f"You share {len(common_interests)} interests")
                if age_score > 0.7:
                    reasons.append("You're close in age")
                if location_score == 1.0:
                    reasons.append("You're in the same location")
                
                matches.append({
                    'user': potential_match,
                    'compatibility_score': int(total_score * 100),
                    'common_interests': list(set(user['interests']) & set(potential_match['interests'])),
                    'match_reasons': reasons
                })
                
            except Exception as e:
                print(f"Error processing match: {str(e)}")
                continue
        
        # Sort matches by compatibility score
        matches.sort(key=lambda x: x['compatibility_score'], reverse=True)
        
        return matches[:limit] 