from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import (
    Profile, Movie, MovieCrew, MovieCast, ProductionCompany,
    ProductionCountry, Distributor, Favorite, Rating, Comment, WatchList
)

@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = ('user', 'full_name', 'phone_number', 'date_joined', 'login_type')
    search_fields = ('user__email', 'full_name', 'phone_number')
    list_filter = ('login_type', 'date_joined')
    readonly_fields = ('date_joined',)

@admin.register(Movie)
class MovieAdmin(ModelAdmin):
    list_display = ('title', 'release_date', 'vote_average', 'status', 'runtime')
    search_fields = ('title', 'original_title', 'imdb_id')
    list_filter = ('status', 'release_date')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'original_title', 'tmdb_id', 'imdb_id', 'ems_id')
        }),
        ('Content', {
            'fields': ('synopsis', 'overview')
        }),
        ('Scores', {
            'fields': ('audience_score', 'critics_score', 'vote_average', 'vote_count', 'imdb_rating', 'imdb_votes')
        }),
        ('Technical Details', {
            'fields': ('rating', 'runtime', 'original_language', 'spoken_languages', 'sound_mix')
        }),
        ('Release Information', {
            'fields': ('release_date', 'release_date_theaters', 'release_date_streaming', 'status')
        }),
        ('Financial', {
            'fields': ('box_office', 'revenue', 'budget')
        }),
        ('Media', {
            'fields': ('poster_path', 'media_url')
        })
    )

@admin.register(MovieCrew)
class MovieCrewAdmin(ModelAdmin):
    list_display = ('movie', 'director', 'screenwriter')
    search_fields = ('movie__title', 'director', 'screenwriter')
    autocomplete_fields = ['movie']

@admin.register(MovieCast)
class MovieCastAdmin(ModelAdmin):
    list_display = ('movie', 'name', 'order')
    search_fields = ('movie__title', 'name')
    list_filter = ('movie',)
    ordering = ('order',)

@admin.register(ProductionCompany)
class ProductionCompanyAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('movies',)

@admin.register(ProductionCountry)
class ProductionCountryAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('movies',)

@admin.register(Distributor)
class DistributorAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('movies',)

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

