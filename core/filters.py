from django_filters import rest_framework as filters
from .models import Movie

class MovieFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    genres = filters.CharFilter(method='filter_genres')
    min_rating = filters.NumberFilter(field_name='avg_rating', lookup_expr='gte')
    max_rating = filters.NumberFilter(field_name='avg_rating', lookup_expr='lte')
    language = filters.CharFilter(field_name='original_language', lookup_expr='iexact')

    def filter_genres(self, queryset, name, value):
        # Split comma-separated genres
        genres = [genre.strip() for genre in value.split(',')]
        # Filter movies that contain ANY of the specified genres
        return queryset.filter(genres__overlap=genres)

    class Meta:
        model = Movie
        fields = ['title', 'genres', 'original_language', 'avg_rating']