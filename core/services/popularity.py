from django.db.models import Count, F, ExpressionWrapper, FloatField
from django.db.models.functions import Now
from django.utils import timezone
from datetime import timedelta
from ..models import Movie, MovieInteraction

class PopularityCalculator:
    INTERACTION_WEIGHTS = {
        'SEARCH': 1,
        'VIEW': 2,
        'RECOMMEND': 3,
        'RATING': 4,
        'FAVORITE': 5,
        'SHARE': 3
    }
    
    TIME_DECAY_FACTOR = 0.5  # Higher means faster decay
    
    @classmethod
    def calculate_popularity(cls, movie_id: int) -> float:
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        
        # Get interactions for the movie
        interactions = MovieInteraction.objects.filter(
            movie_id=movie_id,
            timestamp__gte=week_ago
        )
        
        # Calculate weighted score
        score = 0
        for interaction in interactions:
            weight = cls.INTERACTION_WEIGHTS.get(interaction.interaction_type, 1)
            time_diff = (now - interaction.timestamp).total_seconds() / (7 * 24 * 3600)
            time_decay = 1 / (1 + cls.TIME_DECAY_FACTOR * time_diff)
            score += weight * time_decay
        
        return score

    @classmethod
    def update_all_popularity_scores(cls):
        """Update popularity scores for all movies"""
        movies = Movie.objects.all()
        for movie in movies:
            score = cls.calculate_popularity(movie.id)
            movie.popularity_score = score
            movie.save(update_fields=['popularity_score'])