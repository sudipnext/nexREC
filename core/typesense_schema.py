MOVIES_SCHEMA = {
    "name": "movies",
    "fields": [
        # Primary Search Fields
        {"name": "title", "type": "string", "sort": True, "facet": False},
        {"name": "original_title", "type": "string", "sort": True, "facet": False},
        {"name": "overview", "type": "string", "sort": False, "facet": False},
        
        # ID Fields
        {"name": "tmdb_id", "type": "int32", "sort": True, "facet": False},
        {"name": "imdb_id", "type": "string", "sort": False, "facet": False},
        
        # Filtering & Faceting Fields
        {"name": "release_date", "type": "string", "sort": True, "facet": True},
        {"name": "status", "type": "string", "sort": False, "facet": True},
        {"name": "rating", "type": "string", "sort": False, "facet": True},
        {"name": "original_language", "type": "string", "sort": False, "facet": True},
        {"name": "production_countries", "type": "string[]", "sort": False, "facet": True},
        
        # Scoring Fields
        {"name": "vote_average", "type": "float", "sort": True, "facet": False},
        {"name": "vote_count", "type": "int32", "sort": True, "facet": False},
        {"name": "critics_score", "type": "float", "sort": True, "facet": False},
        {"name": "audience_score", "type": "float", "sort": True, "facet": False},
        
        # Cast & Crew (for searching by people)
        {"name": "director", "type": "string", "sort": False, "facet": True},
        {"name": "cast", "type": "string[]", "sort": False, "facet": True},
        
        # Additional Display Fields
        {"name": "poster_path", "type": "string", "sort": False, "facet": False},
        {"name": "runtime", "type": "string", "sort": False, "facet": False},
    ],
    "default_sorting_field": "vote_average"
} 