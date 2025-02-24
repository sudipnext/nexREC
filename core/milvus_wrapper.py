from typing import List, Optional, Dict, Any
from pymilvus import connections, utility, Collection
from django.conf import settings
from logging import getLogger

logger = getLogger(__name__)

def connect_milvus():
    """Establish connection to Milvus server"""
    try:
        connections.connect(
            "default", 
            host=settings.MILVUS_HOST, 
            port=settings.MILVUS_PORT
        )
        collections = utility.list_collections()
        logger.info(f"Connected to Milvus. Available collections: {collections}")
    except Exception as e:
        logger.error(f"Failed to connect to Milvus: {str(e)}")
        raise

class MilvusAPI:
    def __init__(self, collection_name: str):
        """Initialize Milvus wrapper with collection name"""
        try:
            self.collection_name = collection_name
            # Changed from get_connection to get_connection_addr
            self.collection = Collection(collection_name)
            if not self.collection:
                raise ValueError(f"Collection {collection_name} not found")
            # Load the collection
            self.collection.load()
        except Exception as e:
            logger.error(f"Failed to initialize collection {collection_name}: {str(e)}")
            raise

    def search(
        self, 
        query_vector: List[float], 
        search_params: Dict[str, Any],
        limit: int = 5,
        output_fields: Optional[List[str]] = None
    ) -> List[Dict]:
        """Search for similar vectors"""
        try:
            results = self.collection.search(
                data=[query_vector],
                anns_field="embeddings",
                param=search_params,
                limit=limit,
                output_fields=output_fields
            )
            return results
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise

    def get_by_id(self, movie_index: int) -> Dict:
        """Get entity by ID"""
        try:
            # Use query instead of get_entity_by_id
            results = self.collection.query(
                expr=f"movie_index == {movie_index}",
                output_fields=["embeddings", "movie_index"]
            )
            if not results or len(results) == 0:
                raise ValueError(f"No movie found with index {movie_index}")
            return results[0]  # Return first match
        except Exception as e:
            logger.error(f"Failed to get movie {movie_index}: {str(e)}")
            raise

    def text_search(
        self, 
        query: str,
        limit: int = 5,
        output_fields: Optional[List[str]] = None
    ) -> List[Dict]:
        """Search by text"""
        try:
            results = self.collection.search(
                data=[query],
                anns_field="combined_text",
                limit=limit,
                output_fields=output_fields
            )
            return results
        except Exception as e:
            logger.error(f"Text search failed: {str(e)}")
            raise

    def recommend_by_movie_index(
        self,
        movie_index: int,
        search_params: Dict[str, Any],
        limit: int = 5,
        output_fields: Optional[List[str]] = None
    ) -> List[Dict]:
        """Search for similar movies using a movie index"""
        try:
            # First get the movie's embedding vector
            movie = self.get_by_id(movie_index)
            if not movie or 'embeddings' not in movie:
                raise ValueError(f"No embeddings found for movie index {movie_index}")
            
            # Only request fields that exist in Milvus
            safe_output_fields = ['movie_index']
            
            # Use the embedding to search for similar movies
            results = self.search(
                query_vector=movie['embeddings'],
                search_params=search_params,
                limit=limit + 1,  # Add 1 to account for the query movie itself
                output_fields=safe_output_fields
            )
            
            # Process search results
            processed_results = []
            for hits in results:
                for hit in hits:
                    if hit.entity.get('movie_index') != movie_index:
                        processed_results.append(hit)
                    if len(processed_results) >= limit:
                        break
            
            return [processed_results]
        except Exception as e:
            logger.error(f"Search by movie index failed: {str(e)}")
            raise

# Initialize connection when module is imported
connect_milvus()



