# utils.py
import torch
from torch_geometric.nn import SAGEConv, to_hetero
import pandas as pd

# Define model classes (same as in your script)
class GNNEncoder(torch.nn.Module):
    def __init__(self, hidden_channels, out_channels):
        super().__init__()
        self.conv1 = SAGEConv((-1, -1), hidden_channels, aggr="sum", normalize=True)
        self.conv2 = SAGEConv((-1, -1), out_channels, aggr="sum", normalize=True)
        self.batch_norm1 = torch.nn.BatchNorm1d(hidden_channels)
        self.batch_norm2 = torch.nn.BatchNorm1d(out_channels)
        self.dropout = torch.nn.Dropout(0.3)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = self.batch_norm1(x).relu()
        x = self.dropout(x)
        x = self.conv2(x, edge_index)
        x = self.batch_norm2(x)
        return x

class EdgeDecoder(torch.nn.Module):
    def __init__(self, hidden_channels):
        super().__init__()
        self.lin1 = torch.nn.Linear(2 * hidden_channels, hidden_channels)
        self.lin2 = torch.nn.Linear(hidden_channels, 1)
        self.dropout = torch.nn.Dropout(0.3)

    def forward(self, z_dict, edge_label_index):
        row, col = edge_label_index
        z = torch.cat([z_dict['user'][row], z_dict['movie'][col]], dim=-1)
        z = self.lin1(z).relu()
        z = self.dropout(z)
        z = self.lin2(z)
        return 5 * torch.sigmoid(z).view(-1)

class Model(torch.nn.Module):
    def __init__(self, hidden_channels, metadata):
        super().__init__()
        self.encoder = GNNEncoder(hidden_channels, hidden_channels)
        self.encoder = to_hetero(self.encoder, metadata, aggr='sum')
        self.decoder = EdgeDecoder(hidden_channels)

    def forward(self, x_dict, edge_index_dict, edge_label_index):
        z_dict = self.encoder(x_dict, edge_index_dict)
        return self.decoder(z_dict, edge_label_index)

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_model_and_data(model_path, graph_data_path, mappings_path):
    """Load model, graph data and mappings"""
    # Load graph data
    graph_data = torch.load(graph_data_path, map_location=device)
    x_dict = graph_data['x_dict']
    edge_index_dict = graph_data['edge_index_dict']
    metadata = graph_data['metadata']

    # Initialize and load model
    model = Model(hidden_channels=32, metadata=metadata).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    # Load mappings
    mappings = torch.load(mappings_path, map_location='cpu')
    unique_user_id = pd.DataFrame(mappings['unique_user_id'])
    unique_movie_id = pd.DataFrame(mappings['unique_movie_id'])

    return model, x_dict, edge_index_dict, metadata, unique_user_id, unique_movie_id

def get_top_movies_for_new_user(model, x_dict, edge_index_dict, new_user_features, unique_movie_id, num_movies=5):
    """Get top movie recommendations for a new user"""
    with torch.no_grad():
        original_num_users = x_dict['user'].size(0)
        x_dict_updated = {
            'user': torch.cat([x_dict['user'], new_user_features.to(device)], dim=0),
            'movie': x_dict['movie']
        }
        
        new_user_id = original_num_users
        z_dict = model.encoder(x_dict_updated, edge_index_dict)

        num_movies_total = x_dict['movie'].size(0)
        row = torch.zeros(num_movies_total, dtype=torch.long).fill_(new_user_id)
        col = torch.arange(num_movies_total, dtype=torch.long)
        edge_label_index = torch.stack([row, col], dim=0).to(device)

        predicted_ratings = model.decoder(z_dict, edge_label_index).cpu().numpy()
        movie_ratings = list(enumerate(predicted_ratings))
        top_movies = sorted(movie_ratings, key=lambda x: x[1], reverse=True)[:num_movies]

        # Convert mappedMovieId back to original movie_index
        top_movies_with_ids = [
            (unique_movie_id[unique_movie_id['mappedMovieId'] == movie_id]['movie_index'].values[0], rating)
            for movie_id, rating in top_movies
        ]
        return top_movies_with_ids