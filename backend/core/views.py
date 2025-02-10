from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Profile, Movie, Favorite, Rating, Comment, WatchList
from .serializers import (ProfileSerializer, MovieSerializer, FavoriteSerializer,
                         RatingSerializer, CommentSerializer, WatchListSerializer)
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from .pagination_custom import CustomPagination

# Create your views here.

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get or update user profile",
        responses={200: ProfileSerializer()}
    )
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Profile.objects.none()
        return Profile.objects.filter(user=self.request.user)

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    @swagger_auto_schema(
        operation_description="Search movies by title",
        manual_parameters=[
            openapi.Parameter(
                'title', openapi.IN_QUERY,
                description="Movie title to search for",
                type=openapi.TYPE_STRING
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        title = request.query_params.get('title', '')
        movies = Movie.objects.filter(title__icontains=title)
        serializer = self.get_serializer(movies, many=True)
        return Response(serializer.data)

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    @swagger_auto_schema(
        operation_description="List user's favorite movies",
        responses={200: FavoriteSerializer(many=True)}
    )
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Favorite.objects.none()
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    @swagger_auto_schema(
        operation_description="List user's movie ratings",
        responses={200: RatingSerializer(many=True)}
    )
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Rating.objects.none()
        return Rating.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination

    @swagger_auto_schema(
        operation_description="List comments for a movie",
        manual_parameters=[
            openapi.Parameter(
                'movie_id', openapi.IN_QUERY,
                description="Filter comments by movie ID",
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def get_queryset(self):
        queryset = Comment.objects.filter(parent=None)  # Only get parent comments
        movie_id = self.request.query_params.get('movie_id', None)
        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)
        return queryset

    @swagger_auto_schema(
        operation_description="Toggle like on a comment",
        responses={200: openapi.Response(
            description="Like toggled successfully",
            examples={"application/json": {"liked": True}}
        )}
    )
    @action(detail=True, methods=['post'])
    def toggle_like(self, request, pk=None):
        comment = self.get_object()
        user = request.user
        if comment.likes.filter(id=user.id).exists():
            comment.likes.remove(user)
            liked = False
        else:
            comment.likes.add(user)
            liked = True
        return Response({'liked': liked})

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WatchListViewSet(viewsets.ModelViewSet):
    serializer_class = WatchListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    @swagger_auto_schema(
        operation_description="List user's watchlist",
        responses={200: WatchListSerializer(many=True)}
    )
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return WatchList.objects.none()
        return WatchList.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Mark movie as watched",
        responses={200: WatchListSerializer()}
    )
    @action(detail=True, methods=['post'])
    def mark_watched(self, request, pk=None):
        watchlist_item = self.get_object()
        watchlist_item.watched = True
        watchlist_item.watched_at = timezone.now()
        watchlist_item.save()
        serializer = self.get_serializer(watchlist_item)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
