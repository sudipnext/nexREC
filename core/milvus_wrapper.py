from typing import List, Optional, Dict, Any
from pymilvus import connections, utility, Collection, FieldSchema, DataType, CollectionSchema
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

    def create_movie_collection(self):
        """Create a new collection in Milvus"""
        fields = [
            FieldSchema(name="movie_index", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="genres", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="cast", dtype=DataType.VARCHAR, max_length=5000),
            FieldSchema(name="director", dtype=DataType.VARCHAR, max_length=2000),
            FieldSchema(name="synopsis", dtype=DataType.VARCHAR, max_length=5000),
            FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=384),
            FieldSchema(name="rating", dtype=DataType.VARCHAR, max_length=255)
        ]
        
        schema = CollectionSchema(fields=fields, description="Movie Collection with embeddings")
        collection = Collection(name=self.collection_name, schema=schema)
        
        # Create indexes for vector and text search
        index_params = {
            "index_type": "HNSW",
            "metric_type": "COSINE",
            "params": {"M": 8, "efConstruction": 64}
        }
        
        collection.create_index(
            field_name="embeddings",
            index_params=index_params
        )
        
        return f"Collection {self.collection_name} created successfully"

    def create_user_collection(self):
        """Create a new collection in Milvus"""
        fields = [
            FieldSchema(name="user_index", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=384)  # Main vector for similarity search
        ]
        schema = CollectionSchema(fields=fields, description="User embeddings collection")
        collection = Collection(name=self.collection_name, schema=schema)
        return f"Collection {self.collection_name} created successfully"

    def drop_collection(self):
        """Drop the collection from Milvus"""
        return utility.drop_collection(self.collection_name)
    
    def create_collection_index(self, index_params: Dict[str, Any]):
        """
        Create index for the collection
        index_params={
        "index_type": "HNSW",  # Or use "HNSW" for fast similarity search
        "metric_type": "COSINE",  # Change to "COSINE" if needed
        "params": {"nlist": 128}
        }
        
        """
        try:
            self.collection.create_index(field_name="embeddings", index_params=index_params)
            return f"Index created for collection {self.collection_name}"
        except Exception as e:
            logger.error(f"Index creation failed: {str(e)}")
            raise

    def load_collection_into_memory(self):
        """Load the collection into memory for faster search"""
        return self.collection.load()


    def insert_data_into_collection(self, data: List[Dict]):
        """Insert data into Milvus collection"""
        self.collection(name=self.collection_name).insert(data)
        return f"Data inserted successfully into collection {self.collection_name}"

    def upsert_data_into_collection(self, data: List[Dict]):
        """Upsert data into Milvus collection"""
        self.collection(name=self.collection_name).upsert(data)
        return f"Data upserted successfully into collection {self.collection_name}"

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
        output_fields: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        min_similarity: float = 0.3  # Minimum similarity threshold
    ) -> List[Dict]:
        """
        Search by text with filtering options and similarity scoring
        
        Args:
            query (str): Text to search for
            output_fields (List[str]): Fields to return
            filters (Dict): Filtering conditions like {"rating": "PG-13", "genres": "Action"}
        """
        try:
            if output_fields is None:
                output_fields = ["movie_index", "title", "genres", "cast", "director", "synopsis", "rating"]
            
            # Build expression for filtering
            expr = None
            if filters:
                conditions = []
                if "rating" in filters:
                    conditions.append(f'rating == "{filters["rating"]}"')
                if "genres" in filters:
                    conditions.append(f'genres LIKE "%{filters["genres"]}%"')
                if conditions:
                    expr = " && ".join(conditions)
            
            # Build text search condition
            text_conditions = []
            search_fields = ["title", "synopsis", "cast", "director"]
            for field in search_fields:
                text_conditions.append(f'{field} LIKE "%{query}%"')
            
            if expr:
                expr = f"({' || '.join(text_conditions)}) && ({expr})"
            else:
                expr = f"({' || '.join(text_conditions)})"
            
            # Execute search
            results = self.collection.query(
                expr=expr,
                output_fields=output_fields,
                limit=limit
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



