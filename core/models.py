from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
UserAccount = get_user_model()


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', null=True, blank=True)
    login_type = models.CharField(
        max_length=50, blank=True, null=True)  # e.g., 'email', 'google'
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
    ems_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=500)
    synopsis = models.TextField(blank=True)
    director = models.CharField(max_length=500, blank=True)
    producer = models.TextField(blank=True)
    screenwriter = models.CharField(max_length=500, blank=True)
    distributor = models.CharField(max_length=500, blank=True)
    rating = models.CharField(max_length=500, blank=True)
    original_language = models.CharField(max_length=500, blank=True)
    movie_index = models.IntegerField(null=True, blank=True)
    overview = models.TextField(blank=True)
    tagline = models.CharField(max_length=500, blank=True)
    genres = models.JSONField(default=list, blank=True)
    production_companies = models.JSONField(default=list, blank=True)
    production_countries = models.JSONField(default=list, blank=True)
    spoken_languages = models.JSONField(default=list, blank=True)
    cast = models.JSONField(default=list, blank=True)
    director_of_photography = models.CharField(max_length=500, blank=True)
    writers = models.TextField(blank=True)
    producers = models.TextField(blank=True)
    music_composer = models.CharField(max_length=500, blank=True)
    avg_rating = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True)
    posterUri = models.CharField(null=True, blank=True)
    audienceScore = models.JSONField(default=list, null=True, blank=True)
    criticsScore = models.JSONField(default=list, null=True, blank=True)
    mediaUrl = models.URLField(max_length=500, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    popularity_score = models.FloatField(default=0)
    total_interactions = models.IntegerField(default=0)
    weekly_views = models.IntegerField(default=0)
    last_interaction = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class Favorite(models.Model):
    user = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name='favorites')
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'movie']  # Prevents duplicate favorites
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.movie.title}"


class Rating(models.Model):
    user = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name='ratings')
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
    user = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name='comments')
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    likes = models.ManyToManyField(
        UserAccount, related_name='liked_comments', blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.email} on {self.movie.title}"


class WatchList(models.Model):
    user = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name='in_watchlists')
    added_at = models.DateTimeField(auto_now_add=True)
    watched = models.BooleanField(default=False)
    watched_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'movie']
        ordering = ['-added_at']

    def __str__(self):
        status = "watched" if self.watched else "pending"
        return f"{self.user.email} - {self.movie.title} ({status})"


class MovieInteraction(models.Model):
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=50, choices=[
        ('VIEW', 'Movie View'),
        ('RECOMMEND', 'Recommendation Click'),
        ('FAVORITE', 'Added to Favorites'),
        ('WATCHLIST', 'Added to Watchlist'),
        ('WATCHED', 'Watched already'),
    ])
    user = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    search_query = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['movie', 'interaction_type', 'timestamp']),
            models.Index(fields=['timestamp'])
        ]


class Logs(models.Model):
    LEVEL_CHOICES = [
        ('INFO', 'Info'),
        ('ERROR', 'Error'),
        ('WARNING', 'Warning'),
        ('SUCCESS', 'Success'),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    message = models.TextField()
    task_name = models.CharField(max_length=100)
    traceback = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Log'
        verbose_name_plural = 'Logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp} - {self.level} - {self.task_name}"


class UserPreference(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    )
    GENRES = [
        ('Action', 'Action'),
        ('Adventure', 'Adventure'),
        ('Animation', 'Animation'),
        ('Biography', 'Biography'),
        ('Comedy', 'Comedy'),
        ('Crime', 'Crime'),
        ('Documentary', 'Documentary'),
        ('Drama', 'Drama'),
        ('Family', 'Family'),
        ('Fantasy', 'Fantasy'),
        ('History', 'History'),
        ('Horror', 'Horror'),
        ('Music', 'Music'),
        ('Musical', 'Musical'),
        ('Mystery', 'Mystery'),
        ('Romance', 'Romance'),
        ('Sci-Fi', 'Sci-Fi'),
        ('Sport', 'Sport'),
        ('Thriller', 'Thriller'),
        ('War', 'War'),
        ('Western', 'Western'),
    ]
    MOVIE_WATCH_FREQUENCY = (
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('OCCASIONALLY', 'Occasionally'),
        ('FEW TIMES A MONTH', 'Few times a month'),
        ('MONTHLY', 'Monthly'),
        ('FEW TIMES A MONTH', 'Few times a month'),
        ('YEARLY', 'Yearly'),
    )
    MOVIE_TASTE = (
        ('AWFUL', 'Awful'),
        ('MEH', 'Meh'),
        ('GOOD', 'Good'),
        ('AMAZING', 'Amazing'),
        ('HAVENT SEEN', 'Havent seen'),
    )

    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    favorite_genres = models.JSONField(default=list)
    watch_frequency = models.CharField(
        max_length=50, choices=MOVIE_WATCH_FREQUENCY)
    taste = models.CharField(max_length=50, choices=MOVIE_TASTE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

