from rest_framework import serializers
from .models import (Profile, Movie, MovieCrew, MovieCast, ProductionCompany, 
                    ProductionCountry, Distributor, Favorite, Rating, Comment, WatchList)

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'profile_picture', 'login_type', 'dob', 'phone_number', 
                 'full_name', 'date_joined', 'currency']
        read_only_fields = ['user', 'user_ip']

class MovieCastSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieCast
        fields = ['id', 'name', 'order']

class MovieCrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieCrew
        fields = ['director', 'producer', 'screenwriter', 'writers',
                 'director_of_photography', 'music_composer']

class ProductionCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionCompany
        fields = ['id', 'name']

class ProductionCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionCountry
        fields = ['id', 'name']

class DistributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distributor
        fields = ['id', 'name']

class MovieSerializer(serializers.ModelSerializer):
    crew = MovieCrewSerializer(read_only=True)
    cast_members = MovieCastSerializer(many=True, read_only=True)
    production_companies = ProductionCompanySerializer(many=True, read_only=True)
    production_countries = ProductionCountrySerializer(many=True, read_only=True)
    distributors = DistributorSerializer(many=True, read_only=True)
    
    class Meta:
        model = Movie
        fields = [
            # Basic Info
            'id', 'title', 'original_title', 'tmdb_id', 'imdb_id', 'ems_id',
            
            # Content
            'synopsis', 'overview',
            
            # Scores
            'audience_score', 'critics_score', 'vote_average', 'vote_count',
            'imdb_rating', 'imdb_votes',
            
            # Technical
            'rating', 'runtime', 'original_language', 'spoken_languages',
            'sound_mix',
            
            # Release
            'release_date', 'release_date_theaters', 'release_date_streaming',
            'status',
            
            # Financial
            'box_office', 'revenue', 'budget',
            
            # Media
            'poster_path', 'media_url',
            
            # Related Data
            'crew', 'cast_members', 'production_companies',
            'production_countries', 'distributors',
            
            # Timestamps
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class MovieListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'poster_path', 'release_date',
            'vote_average', 'overview'
        ]

class FavoriteSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(),
        source='movie',
        write_only=True
    )

    class Meta:
        model = Favorite
        fields = ['id', 'movie', 'movie_id', 'created_at']
        read_only_fields = ['user', 'created_at']

class RatingSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(),
        source='movie',
        write_only=True
    )

    class Meta:
        model = Rating
        fields = ['id', 'movie', 'movie_id', 'score', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(),
        source='movie',
        write_only=True
    )

    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'movie', 'movie_id', 'content', 
            'created_at', 'updated_at', 'parent', 
            'likes_count', 'replies'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'email': obj.user.email,
            'full_name': obj.user.profile.full_name if hasattr(obj.user, 'profile') else None
        }

    def get_replies(self, obj):
        if obj.parent is None:  # Only get replies for parent comments
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

    def get_likes_count(self, obj):
        return obj.likes.count()

class WatchListSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(),
        source='movie',
        write_only=True
    )

    class Meta:
        model = WatchList
        fields = ['id', 'movie', 'movie_id', 'added_at', 'watched', 'watched_at']
        read_only_fields = ['user', 'added_at'] 