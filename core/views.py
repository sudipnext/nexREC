from .milvus_wrapper import MilvusAPI
from rest_framework.permissions import AllowAny
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
from .services.popularity import PopularityCalculator
from django.db.models import F
from .models import MovieInteraction

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
        page = self.paginate_queryset(movies)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(movies, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending movies based on popularity score"""
        limit = int(request.query_params.get('limit', 10))
        movies = Movie.objects.order_by('-popularity_score')[:limit]
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
        queryset = Comment.objects.filter(
            parent=None)  # Only get parent comments
        movie_id = self.request.query_params.get('movie_id', None)
        if (movie_id):
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


class RecommendationViewset(viewsets.GenericViewSet):
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.milvus_api = MilvusAPI(collection_name="movies_final")

    def get_queryset(self):
        return Movie.objects.none()


    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'movie_index', openapi.IN_QUERY,
                description="Index of the movie to get recommendations for",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'limit', openapi.IN_QUERY,
                description="Number of recommendations to return",
                type=openapi.TYPE_INTEGER
            )

        ],
        operation_description="Get movie recommendations for the current user",
        responses={200: MovieSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def get_recommendations_by_movie_idx(self, request):
        movie_index = int(request.query_params.get('movie_index', 0))
        limit = int(request.query_params.get('limit', 5))

        try:
            # Get similar movies from Milvus (only movie_index)
            similar_movies = self.milvus_api.recommend_by_movie_index(
                movie_index=movie_index,
                search_params={'metric_type': 'COSINE',
                               'params': {'nprobe': 16}},
                limit=limit
            )

            # Extract movie indices
            movie_indices = [hit.entity.get('movie_index')
                             for hit in similar_movies[0]]

            # Get full movie details from Django database
            movies = Movie.objects.filter(movie_index__in=movie_indices)

            serializer = self.get_serializer(movies, many=True)
            return Response(serializer.data)

        except Exception as e:
            print(f"Recommendation failed: {str(e)}")
            return Response(
                {"error": "Failed to get recommendations"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'interaction_type', openapi.IN_QUERY,
                description="Type of interaction with the movie",
                type=openapi.TYPE_STRING,
                enum=['VIEW', 'RECOMMEND','FAVORITE', 'WATCHLIST', 'WATCHED']
            ),
            openapi.Parameter(
                'search_query', openapi.IN_QUERY,
                description="Search query used to find the movie",
                type=openapi.TYPE_STRING

            )
        ],
        operation_description="Get movie recommendations for the current user",
        responses={200: "OK"}
    )
    @action(detail=True, methods=['get'])
    def track_interaction(self, request, pk=None):
        """Track user interaction with a movie"""
        movie = get_object_or_404(Movie, id=pk)
        interaction_type = request.query_params.get('interaction_type', 'VIEW')
        search_query = request.query_params.get('search_query', "")
        print(movie, interaction_type, search_query)
        MovieInteraction.objects.create(
            movie=movie,
            interaction_type=interaction_type,
            user=request.user if request.user.is_authenticated else None,
            search_query=search_query
        )

        # Update movie's popularity score
        movie.popularity_score = PopularityCalculator.calculate_popularity(
            movie.id)
        movie.total_interactions = F('total_interactions') + 1
        movie.last_interaction = timezone.now()
        movie.save()

        return Response({'status': 'success'})
