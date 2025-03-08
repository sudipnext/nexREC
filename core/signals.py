from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Profile, Movie, Rating, UserPreference
from authapp.models import UserAccount
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg
from .geolocationip import get_client_ip, get_location_from_ip
from core.sentence_transformer_wrapper import SentenceTransformerWrapper
from core.milvus_wrapper import MilvusAPI
from django.db.models import Avg, Count
from .models import (
    UserPreference, Rating, Favorite, WatchList, 
    MovieInteraction, MovieTaste, Comment, UserEmbeddings
)
from core.utils import DatabaseLogger
from .sentence_transformer_wrapper import SentenceTransformerWrapper
from django.db import models
from django.db.models import Avg


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
    new_avg = movie.update_average_rating()
    
    logger.log(
        'INFO', 
        f"Updated average rating for movie {movie.id} to {new_avg}",
        'update_movie_rating'
    )

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
    """Update user preference and generate embeddings instantly when preferences change"""
    user = instance.user
    
    try:
        # Collect user interactions
        user_data = collect_user_interactions(user)
        
        # Build interaction text
        interaction_text = []
        
        # Add user preferences
        if user_data['preferences']:
            interaction_text.append(f"Age: {user_data['preferences']['age']}")
            interaction_text.append(f"Gender: {user_data['preferences']['gender']}")
            interaction_text.append(f"Favorite Genres: {', '.join(user_data['preferences']['favorite_genres'])}")
            interaction_text.append(f"Watch Frequency: {user_data['preferences']['watch_frequency']}")
        
        # Add ratings
        for rating in user_data['ratings']:
            interaction_text.append(f"Rated movie {rating['movie_id']} with score {rating['score']}")
        
        # Add movie tastes
        for taste in user_data['movie_tastes']:
            interaction_text.append(f"Found movie {taste['movie_id']} {taste['taste'].lower()}")
        
        # Add watchlist
        for watch in user_data['watchlist']:
            status = "watched" if watch['watched'] else "wants to watch"
            interaction_text.append(f"{status} movie {watch['movie_id']}")
        
        # Create combined text and get embeddings
        combined_text = " ".join(interaction_text)
        transformer = SentenceTransformerWrapper()
        embeddings = transformer.get_embedding(combined_text)
        
        if embeddings is not None:
            # Try to get existing embeddings, create if doesn't exist
            user_embeddings, created = UserEmbeddings.objects.get_or_create(
                user=user,
                defaults={
                    'embeddings': embeddings["embedding"],
                    'last_updated': timezone.now()
                }
            )
            
            if not created:
                # Update existing embeddings
                user_embeddings.embeddings = embeddings["embedding"]
                user_embeddings.last_updated = timezone.now()
                user_embeddings.save()
            
            logger.log('INFO', f"{'Created' if created else 'Updated'} embeddings for user {user.id}", 'update_user_preference')
        else:
            logger.log('ERROR', f"Failed to generate embeddings for user {user.id}", 'update_user_preference')
            
    except Exception as e:
        logger.log('ERROR', f"Error updating user embeddings: {str(e)}", 'update_user_preference')

