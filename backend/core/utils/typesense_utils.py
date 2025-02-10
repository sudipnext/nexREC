from typing import Dict, Any
import typesense
from django.conf import settings
from core.models import Movie
from core.typesense_schema import MOVIES_SCHEMA
def get_typesense_client():
    return typesense.Client({
        'nodes': [{
            'host': settings.TYPESENSE_HOST,
            'port': settings.TYPESENSE_PORT,
            'protocol': settings.TYPESENSE_PROTOCOL
        }],
        'api_key': settings.TYPESENSE_API_KEY,
        'connection_timeout_seconds': 2
    })

def prepare_movie_for_indexing(movie: Movie) -> Dict[str, Any]:
    """Prepare movie data for Typesense indexing"""
    # Get related data
    crew = movie.moviecrew_set.first()
    cast = movie.moviecast_set.all()
    countries = movie.production_countries.all()

    return {
        # Primary Search Fields
        "title": movie.title,
        "original_title": movie.original_title,
        "overview": movie.overview,
        
        # ID Fields
        "tmdb_id": movie.tmdb_id,
        "imdb_id": movie.imdb_id,
        
        # Filtering & Faceting Fields
        "release_date": str(movie.release_date),
        "status": movie.status,
        "rating": movie.rating,
        "original_language": movie.original_language,
        "production_countries": [country.name for country in countries],
        
        # Scoring Fields
        "vote_average": float(movie.vote_average),
        "vote_count": int(movie.vote_count),
        "critics_score": float(movie.critics_score),
        "audience_score": float(movie.audience_score),
        
        # Cast & Crew
        "director": crew.director if crew else "",
        "cast": [cast_member.name for cast_member in cast],
        
        # Additional Display Fields
        "poster_path": movie.poster_path,
        "runtime": movie.runtime,
    }

def index_movies():
    """Index all movies to Typesense"""
    client = get_typesense_client()
    
    # Delete existing collection if it exists
    try:
        client.collections['movies'].delete()
    except:
        pass

    # Create collection with schema
    client.collections.create(MOVIES_SCHEMA)

    # Prepare movies for indexing
    movies = Movie.objects.prefetch_related(
        'moviecrew_set',
        'moviecast_set',
        'production_countries'
    ).all()

    # Index movies in batches
    batch_size = 100
    documents = []
    
    for movie in movies:
        try:
            doc = prepare_movie_for_indexing(movie)
            documents.append(doc)
            
            if len(documents) >= batch_size:
                client.collections['movies'].documents.import_(documents)
                documents = []
                
        except Exception as e:
            print(f"Error indexing movie {movie.title}: {str(e)}")
    
    # Index remaining documents
    if documents:
        client.collections['movies'].documents.import_(documents) 