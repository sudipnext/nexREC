from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (ProfileViewSet, MovieViewSet, FavoriteViewSet,
                   RatingViewSet, CommentViewSet, WatchListViewSet, RecommendationViewset, UserPreferenceViewSet, MovieTasteViewSet)

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'movies', MovieViewSet)
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'ratings', RatingViewSet, basename='rating')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'watchlist', WatchListViewSet, basename='watchlist')
router.register(r'recommend', RecommendationViewset, basename='recommend')
router.register(r'preferences', UserPreferenceViewSet, basename='preferences')
router.register(r'movie-taste', MovieTasteViewSet, basename='movie-taste')

urlpatterns = [
    path('', include(router.urls)),
] 