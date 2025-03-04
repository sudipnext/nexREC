from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Profile, Movie, Rating, UserPreference
from authapp.models import UserAccount
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg
from .geolocationip import get_client_ip, get_location_from_ip
from core.services.sentence_transformer_embeddings_generator import SentenceTransformerEmbeddingsGenerator
from core.milvus_wrapper import MilvusAPI
from django.db.models import Avg, Count
from .models import (
    UserPreference, Rating, Favorite, WatchList, 
    MovieInteraction, MovieTaste, Comment, UserEmbeddings
)
from core.utils import DatabaseLogger

logger = DatabaseLogger()

@receiver(post_save, sender=UserAccount)
def create_profile(sender, instance, created, **kwargs):
    """Create a profile when a new user account is created"""
    if created:
        Profile.objects.create(
            user=instance,
        )


def update_avg_rating(instance):
    """Helper function to update average rating"""
    content_type = instance.content_type
    object_id = instance.object_id
    
    # Get the model class (Hotel or Activity)
    model_class = content_type.model_class()
    
    # Get the object instance
    obj = model_class.objects.get(id=object_id)
    
    # Calculate new average
    new_avg = Rating.objects.filter(
        content_type=content_type,
        object_id=object_id
    ).aggregate(Avg('score'))['score__avg'] or 0
    
    # Update the object's avg_rating
    obj.avg_rating = round(new_avg, 2)
    obj.save()

@receiver(post_save, sender=Rating)
def update_movie_rating(sender, instance, **kwargs):
    """Update movie's average rating when a rating is created or modified"""
    movie = instance.movie
    avg_rating = Rating.objects.filter(movie=movie).aggregate(Avg('score'))['score__avg']
    
    # Add avg_rating field to Movie model if you want to store it
    if hasattr(movie, 'avg_rating'):
        movie.avg_rating = round(avg_rating, 2) if avg_rating else 0
        movie.save(update_fields=['avg_rating'])

@receiver(post_delete, sender=Rating)
def update_movie_rating_on_delete(sender, instance, **kwargs):
    """Update movie's average rating when a rating is deleted"""
    movie = instance.movie
    avg_rating = Rating.objects.filter(movie=movie).aggregate(Avg('score'))['score__avg']
    
    if hasattr(movie, 'avg_rating'):
        movie.avg_rating = round(avg_rating, 2) if avg_rating else 0
        movie.save(update_fields=['avg_rating'])


def collect_user_interactions(user):
    """Collect all interactions for a user and return a structured dictionary"""
    interactions = {
        'ratings': list(Rating.objects.filter(user=user).values(
            'movie_id', 'score', 'created_at'
        )),
        'favorites': list(Favorite.objects.filter(user=user).values(
            'movie_id', 'created_at'
        )),
        'watchlist': list(WatchList.objects.filter(user=user).values(
            'movie_id', 'watched', 'watched_at', 'added_at'
        )),
        'movie_tastes': list(MovieTaste.objects.filter(user=user).values(
            'movie_id', 'taste', 'created_at'
        )),
        'comments': list(Comment.objects.filter(user=user).values(
            'movie_id', 'content', 'created_at'
        )),
        'interactions': list(MovieInteraction.objects.filter(user=user).values(
            'movie_id', 'interaction_type', 'timestamp'
        )),
        'preferences': UserPreference.objects.filter(user=user).values(
            'age', 'gender', 'favorite_genres', 'watch_frequency'
        ).first()
    }
    
    # Aggregate statistics
    interactions['stats'] = {
        'total_ratings': len(interactions['ratings']),
        'avg_rating': Rating.objects.filter(user=user).aggregate(Avg('score'))['score__avg'] or 0,
        'total_favorites': len(interactions['favorites']),
        'total_watchlist': len(interactions['watchlist']),
        'watched_movies': WatchList.objects.filter(user=user, watched=True).count(),
    }
    
    return interactions

from django.utils import timezone


@receiver(post_save, sender=UserPreference)
def update_user_preference(sender, instance, created, **kwargs):
    """Update user preference and generate embeddings based on all user interactions"""
    user = instance.user
    
    # Get or create user embeddings
    user_embeddings, created_embedding = UserEmbeddings.objects.get_or_create(user=user)
    
    # Check if update is needed (e.g., if it's been more than an hour since last update)
    if not created and not created_embedding:
        time_since_update = timezone.now() - user_embeddings.last_updated
        if time_since_update.total_seconds() < 3600:  # 1 hour in seconds
            return  # Skip update if embeddings are recent
    
    # Collect all user interactions
    user_data = collect_user_interactions(user)
    
    # Get interaction counts for comparison
    current_interaction_count = (
        user_data['stats']['total_ratings'] +
        user_data['stats']['total_favorites'] +
        user_data['stats']['total_watchlist']
    )
    
    # Skip update if no new interactions and not a new preference
    if not created and current_interaction_count == user_embeddings.interaction_count:
        logger.log('INFO', f"No new interactions for user {user.id}", 'update_user_preference')
        return
    
    # Initialize your embedding generators
    embeddings_generator = SentenceTransformerEmbeddingsGenerator()
    interaction_text = []
    
    # Add user preferences
    if user_data['preferences']:
        interaction_text.append(f"Age: {user_data['preferences']['age']}")
        interaction_text.append(f"Gender: {user_data['preferences']['gender']}")
        interaction_text.append(f"Favorite Genres: {', '.join(user_data['preferences']['favorite_genres'])}")
        interaction_text.append(f"Watch Frequency: {user_data['preferences']['watch_frequency']}")
    
    # Add ratings information
    for rating in user_data['ratings']:
        interaction_text.append(f"Rated movie {rating['movie_id']} with score {rating['score']}")
    
    # Add movie tastes
    for taste in user_data['movie_tastes']:
        interaction_text.append(f"Found movie {taste['movie_id']} {taste['taste'].lower()}")
    
    # Add watchlist information
    for watch in user_data['watchlist']:
        status = "watched" if watch['watched'] else "wants to watch"
        interaction_text.append(f"{status} movie {watch['movie_id']}")
    
    # Create embedding from the complete interaction text
    combined_text = " ".join(interaction_text)
    embeddings = embeddings_generator.generate_embeddings([combined_text])
    embeddings = embeddings[0].tolist()

    # Update user embeddings with new data
    user_embeddings.embeddings = embeddings
    user_embeddings.interaction_count = current_interaction_count
    user_embeddings.last_updated = timezone.now()
    user_embeddings.save()

    # Log the update
    logger.log('INFO', f"Updated user embeddings for user {user.id}", 'update_user_preference')


