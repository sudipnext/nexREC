import requests
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class FlaskAPIWrapper:
    def __init__(self, base_url: str = "https://sudipnext-movie-recommender.hf.space"):
        self.base_url = base_url.rstrip('/')
        
    def get_recommendations(
        self, 
        user_embedding: List[float],
        num_recommendations: int = 5
    ) -> Dict:
        """
        Get movie recommendations from Flask API
        
        Args:
            user_embedding: List of float values representing user embedding
            num_recommendations: Number of recommendations to return
            
        Returns:
            Dictionary containing recommendations
        """
        try:
            url = f"{self.base_url}/api/recommend"
            
            payload = {
                "user_embedding": user_embedding,
                "num_recommendations": num_recommendations
            }
            
            response = requests.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get recommendations from Flask API: {str(e)}")
            raise

