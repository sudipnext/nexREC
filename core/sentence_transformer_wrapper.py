import requests
import json
from typing import Union, List

class SentenceTransformerWrapper:
    def __init__(self):
        self.endpoint = "https://baasu-sentence-transformer.hf.space/embed"

    def get_embedding(self, text: Union[str, List[str]]) -> List[float]:
        """
        Get embeddings for a given text using the sentence transformer API
        
        Args:
            text: Single string or list of strings to get embeddings for
            
        Returns:
            List of embedding values
        """
        try:
            payload = {"sentence": text}
            response = requests.post(self.endpoint, json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding response: {e}")
            return None

# Example usage:
# transformer = SentenceTransformerWrapper()
# embeddings = transformer.get_embedding("This is a test sentence")