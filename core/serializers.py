from rest_framework import serializers
from .models import (Profile, Movie,  Favorite, Rating, Comment, WatchList, UserPreference, MovieTaste)

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'profile_picture', 'login_type', 'dob', 'phone_number', 
                 'full_name', 'date_joined', 'currency']
        read_only_fields = ['user', 'user_ip']

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

class MovieListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    class Meta:
        model = Movie
        fields = ['id', 'ems_id', 'title', 'synopsis', 'director', 'rating', 
                 'original_language', 'movie_index', 'tagline', 'genres', 
                 'cast', 'avg_rating']

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

class MovieTasteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieTaste
        fields = ['movie', 'taste', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user
        taste, created = MovieTaste.objects.update_or_create(
            user=user,
            movie=validated_data['movie'],
            defaults={'taste': validated_data['taste']}
        )
        return taste

class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['age', 'gender', 'favorite_genres', 'watch_frequency', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        
    def validate_favorite_genres(self, value):
        valid_genres = [genre[0] for genre in UserPreference.GENRES]
        if not all(genre in valid_genres for genre in value):
            raise serializers.ValidationError(f"Invalid genre(s). Valid genres are: {valid_genres}")
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        preference, created = UserPreference.objects.update_or_create(
            user=user,
            defaults=validated_data
        )
        return preference

    

class UserPreferenceListSerializer(UserPreferenceSerializer):
    user = serializers.StringRelatedField()
    
    class Meta(UserPreferenceSerializer.Meta):
        fields = UserPreferenceSerializer.Meta.fields + ['user']