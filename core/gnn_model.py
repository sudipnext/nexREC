import torch
import numpy as np
from core.gnn import Model, device, get_top_movies_for_new_user, load_model_and_data
from django.conf import settings
from pathlib import Path


class MovieRecommender:
    def __init__(self, model_path=None, metadata=None):
        self.device = device
        
        # Use settings.MODEL_DIR instead of MODEL_PATH
        if model_path is None:
            base_dir = Path(settings.MODEL_DIR)
            self.model_path = base_dir / 'model.pth'
            self.graph_data_path = base_dir / 'graph_data.pth'
            self.mappings_path = base_dir / 'mappings.pth'
        
        # Load everything using the common loader
        self.model, self.x_dict, self.edge_index_dict, self.metadata, \
        self.unique_user_id, self.unique_movie_id = load_model_and_data(
            model_path=self.model_path,
            graph_data_path=self.graph_data_path,
            mappings_path=self.mappings_path
        )

    def predict_for_user(self, user_features, num_recommendations=5):
        """
        Predict movie recommendations for a user
        
        Args:
            user_features (torch.Tensor): User embedding vector
            num_recommendations (int): Number of movies to recommend
            
        Returns:
            list: Top movie recommendations with predicted ratings
        """
        with torch.no_grad():
            user_features = torch.tensor(user_features, dtype=torch.float32).to(self.device)
            if len(user_features.shape) == 1:
                user_features = user_features.unsqueeze(0)
                
            recommendations = get_top_movies_for_new_user(
                model=self.model,
                x_dict=self.x_dict,
                edge_index_dict=self.edge_index_dict,
                new_user_features=user_features,
                unique_movie_id=self.unique_movie_id,
                num_movies=num_recommendations
            )
            
            return recommendations
            
    def predict_rating(self, user_id, movie_id, x_dict, edge_index_dict):
        """
        Predict rating for a specific user-movie pair
        
        Args:
            user_id (int): User ID
            movie_id (int): Movie ID
            x_dict (dict): Node features dictionary
            edge_index_dict (dict): Edge indices dictionary
            
        Returns:
            float: Predicted rating
        """
        with torch.no_grad():
            edge_label_index = torch.tensor([[user_id], [movie_id]], 
                                          dtype=torch.long).to(self.device)
            
            pred = self.model(x_dict, edge_index_dict, edge_label_index)
            return pred.item()