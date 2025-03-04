import torch
import numpy as np
from pathlib import Path
from core.gnn import load_model_and_data, get_top_movies_for_new_user, device
from django.conf import settings

class EmbeddingPredictor:
    def __init__(self, base_path=None):
        base_path = Path(base_path)
        if base_path is None:
            base_path = settings.MODEL_DIR
        
        # Load model, data and mappings
        self.model, self.x_dict, self.edge_index_dict, self.metadata, \
        self.unique_user_id, self.unique_movie_id = load_model_and_data(
            model_path=base_path / 'model.pth',
            graph_data_path=base_path / 'graph_data.pth',
            mappings_path=base_path / 'mappings.pth'
        )
        
    def predict_for_embedding(self, user_embedding, num_recommendations=5):
        """
        Get movie recommendations for a user based on their embedding
        """
        if isinstance(user_embedding, np.ndarray):
            user_embedding = torch.from_numpy(user_embedding).float()
            
        if len(user_embedding.shape) == 1:
            user_embedding = user_embedding.unsqueeze(0)
            
        # Pass all required parameters
        recommendations = get_top_movies_for_new_user(
            model=self.model,
            x_dict=self.x_dict,
            edge_index_dict=self.edge_index_dict,
            new_user_features=user_embedding,
            unique_movie_id=self.unique_movie_id,
            num_movies=num_recommendations
        )
        
        return recommendations

    def get_movie_details(self, movie_id):
        """Get original movie ID from mapped ID"""
        return self.unique_movie_id[
            self.unique_movie_id['movie_index'] == movie_id
        ].iloc[0].to_dict()

# # Example usage
# if __name__ == "__main__":
#     # Create a random user embedding (replace with actual embedding)
#     user_embedding = np.random.randn(384)
#     print(user_embedding)
#     predictor = EmbeddingPredictor()
#     recommendations = predictor.predict_for_embedding(user_embedding)
    
#     print("Top 5 Movie Recommendations for New User Embedding:")
#     for movie_id, rating in recommendations:
#         movie_details = predictor.get_movie_details(movie_id)
#         print(f"Movie ID: {movie_id}, Mapped ID: {movie_details['mappedMovieId']}, "
#               f"Predicted Rating: {rating:.2f}")