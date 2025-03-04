import torch
import numpy as np
from pathlib import Path
from core.gnn import load_model_and_data, get_top_movies_for_new_user, device
from django.conf import settings
import os

class EmbeddingPredictor:
    def __init__(self, base_path=None):
        try:
            # First try settings.MODEL_DIR
            if base_path is None:
                base_path = getattr(settings, 'MODEL_DIR', None)
                if base_path is None:
                    # Fallback to default path relative to Django project
                    base_path = os.path.join(settings.BASE_DIR, 'models', 'gnn')
            
            # Convert to Path object
            base_path = Path(base_path)
            
            # Verify paths exist
            model_path = base_path / 'model.pth'
            graph_data_path = base_path / 'graph_data.pth'
            mappings_path = base_path / 'mappings.pth'
            
            # Check if files exist
            if not all(p.exists() for p in [model_path, graph_data_path, mappings_path]):
                raise FileNotFoundError(
                    f"Missing required files in {base_path}. "
                    f"Required: model.pth, graph_data.pth, mappings.pth"
                )
            
            # Load model, data and mappings
            self.model, self.x_dict, self.edge_index_dict, self.metadata, \
            self.unique_user_id, self.unique_movie_id = load_model_and_data(
                model_path=model_path,
                graph_data_path=graph_data_path,
                mappings_path=mappings_path
            )
            
            print("Successfully loaded model and data")
            
        except Exception as e:
            print(f"Failed to initialize EmbeddingPredictor: {str(e)}")
            raise
        
    def predict_for_embedding(self, user_embedding, num_recommendations=5):
        """
        Get movie recommendations for a user based on their embedding
        
        Args:
            user_embedding (list or np.ndarray): User embedding vector
            num_recommendations (int): Number of movies to recommend
        Returns:
            list: List of (movie_id, rating) tuples
        """
        try:
            # Convert list to numpy array if needed
            if isinstance(user_embedding, list):
                user_embedding = np.array(user_embedding, dtype=np.float32)
                
            # Convert numpy array to tensor
            if isinstance(user_embedding, np.ndarray):
                user_embedding = torch.from_numpy(user_embedding).float()
            
            # Ensure tensor is on the correct device
            user_embedding = user_embedding.to(device)
            
            # Add batch dimension if needed
            if len(user_embedding.shape) == 1:
                user_embedding = user_embedding.unsqueeze(0)
                
            print(f"User embedding shape: {user_embedding.shape}")
            
            # Get recommendations
            recommendations = get_top_movies_for_new_user(
                model=self.model,
                x_dict=self.x_dict,
                edge_index_dict=self.edge_index_dict,
                new_user_features=user_embedding,
                unique_movie_id=self.unique_movie_id,
                num_movies=num_recommendations
            )
            
            return recommendations
            
        except Exception as e:
            print(f"Prediction failed: {str(e)}")
            raise

    def get_movie_details(self, movie_id):
        """Get original movie ID from mapped ID"""
        return self.unique_movie_id[
            self.unique_movie_id['movie_index'] == movie_id
        ].iloc[0].to_dict()
