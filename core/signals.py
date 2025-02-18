from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Profile, Movie, Rating, Comment
from authapp.models import UserAccount
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg
from .geolocationip import get_client_ip, get_location_from_ip


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


