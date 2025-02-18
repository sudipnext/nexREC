from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

UserAccount = get_user_model()


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    login_type = models.CharField(max_length=50, blank=True, null=True)  # e.g., 'email', 'google'
    dob = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    currency = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.full_name or "Anonymous User"

    class Meta:
        ordering = ['id']

class Movie(models.Model):
    # Basic Info
    title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255, blank=True)
    tmdb_id = models.IntegerField(default=0)
    imdb_id = models.CharField(max_length=20, blank=True)
    ems_id = models.CharField(max_length=50, blank=True)
    
    # Content
    synopsis = models.TextField(blank=True)
    overview = models.TextField(blank=True)
    
    # Scores
    audience_score = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    critics_score = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    vote_average = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    vote_count = models.IntegerField(default=0)
    imdb_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    imdb_votes = models.IntegerField(null=True, blank=True)
    
    # Technical
    rating = models.CharField(max_length=50, blank=True)  # e.g., "PG-13"
    runtime = models.CharField(max_length=20, blank=True)  # e.g., "1h 37m"
    original_language = models.CharField(max_length=50, blank=True)
    spoken_languages = models.CharField(max_length=255, blank=True)
    sound_mix = models.CharField(max_length=100, blank=True)
    
    # Release
    release_date = models.DateField(null=True, blank=True)
    release_date_theaters = models.CharField(max_length=100, blank=True)
    release_date_streaming = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=50, blank=True)
    
    # Financial
    box_office = models.CharField(max_length=50, blank=True)
    revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Media
    poster_path = models.URLField(max_length=500, blank=True)
    media_url = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-release_date']

    def __str__(self):
        return self.title

class MovieCrew(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='crew')
    director = models.CharField(max_length=255, blank=True)
    producer = models.TextField(blank=True)  # Combined producer credits
    screenwriter = models.CharField(max_length=255, blank=True)
    writers = models.TextField(blank=True)
    director_of_photography = models.CharField(max_length=255, blank=True)
    music_composer = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"Crew for {self.movie.title}"

class MovieCast(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='cast_members')
    name = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.name} in {self.movie.title}"

class ProductionCompany(models.Model):
    name = models.CharField(max_length=255, unique=True)
    movies = models.ManyToManyField(Movie, related_name='production_companies')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Production Companies"

class ProductionCountry(models.Model):
    name = models.CharField(max_length=255, unique=True)
    movies = models.ManyToManyField(Movie, related_name='production_countries')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Production Countries"

class Distributor(models.Model):
    name = models.CharField(max_length=255, unique=True)
    movies = models.ManyToManyField(Movie, related_name='distributors')
    
    def __str__(self):
        return self.name

class Favorite(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='favorites')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'movie']  # Prevents duplicate favorites
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.movie.title}"

class Rating(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(
        validators=[
            MinValueValidator(1, message="Rating must be at least 1"),
            MaxValueValidator(10, message="Rating cannot exceed 10")
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'movie']  # One rating per user per movie
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} rated {self.movie.title}: {self.score}"

class Comment(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='comments')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    likes = models.ManyToManyField(UserAccount, related_name='liked_comments', blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.email} on {self.movie.title}"

class WatchList(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='in_watchlists')
    added_at = models.DateTimeField(auto_now_add=True)
    watched = models.BooleanField(default=False)
    watched_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'movie']
        ordering = ['-added_at']
    
    def __str__(self):
        status = "watched" if self.watched else "pending"
        return f"{self.user.email} - {self.movie.title} ({status})"