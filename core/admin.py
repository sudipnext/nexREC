from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import (
    Profile, Movie, Favorite, Rating, Comment, WatchList
)

@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = ('user', 'full_name', 'phone_number', 'date_joined', 'login_type')
    search_fields = ('user__email', 'full_name', 'phone_number')
    list_filter = ('login_type', 'date_joined')
    readonly_fields = ('date_joined',)

@admin.register(Movie)
class MovieAdmin(ModelAdmin):
    list_display = ('title', 'avg_rating', 'created_at')
    search_fields = ('title', 'overview')
    list_filter = ('avg_rating', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
@admin.register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('user', 'movie', 'created_at')
    search_fields = ('user__email', 'movie__title')
    list_filter = ('created_at',)
    autocomplete_fields = ['user', 'movie']

@admin.register(Rating)
class RatingAdmin(ModelAdmin):
    list_display = ('user', 'movie', 'score', 'created_at')
    search_fields = ('user__email', 'movie__title')
    list_filter = ('score', 'created_at')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('user', 'movie', 'created_at', 'updated_at')
    search_fields = ('user__email', 'movie__title', 'content')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(WatchList)
class WatchListAdmin(ModelAdmin):
    list_display = ('user', 'movie', 'added_at', 'watched', 'watched_at')
    search_fields = ('user__email', 'movie__title')
    list_filter = ('watched', 'added_at', 'watched_at')
    readonly_fields = ('added_at',)

