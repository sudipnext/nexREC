from .milvus_wrapper import MilvusAPI
from rest_framework.permissions import AllowAny
from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Profile, Movie, Favorite, Rating, Comment, WatchList, UserPreference, MovieTaste
from .serializers import (ProfileSerializer, MovieSerializer, FavoriteSerializer,
                          RatingSerializer, CommentSerializer, WatchListSerializer, UserPreferenceSerializer, UserPreferenceListSerializer, MovieTasteSerializer)
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from .pagination_custom import CustomPagination
from .services.popularity import PopularityCalculator
from django.db.models import F
from .models import MovieInteraction, UserPreference
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import MovieFilter
from django.db.models import Q
from django.contrib.postgres.search import SearchQuery, SearchRank, TrigramSimilarity
from django.db.models.functions import Greatest

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
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MovieFilter
    search_fields = ['title', 'overview', 'tagline', 'director', 'cast']
    ordering_fields = ['title', 'avg_rating', 'popularity_score', 'created_at']
    ordering = ['-popularity_score']  # default ordering

    @swagger_auto_schema(
        operation_description="Search movies by title, overview, or genres",
        manual_parameters=[
            openapi.Parameter(
                'title', openapi.IN_QUERY,
                description="Movie title to search for",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'genres', openapi.IN_QUERY,
                description="Comma-separated list of genres (e.g., Action,Comedy)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'min_rating', openapi.IN_QUERY,
                description="Minimum average rating",
                type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                'max_rating', openapi.IN_QUERY,
                description="Maximum average rating",
                type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                'language', openapi.IN_QUERY,
                description="Original language",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'search', openapi.IN_QUERY,
                description="Search in title, overview, tagline, director, and cast",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'ordering', openapi.IN_QUERY,
                description="Order by field (prefix with - for descending)",
                type=openapi.TYPE_STRING,
                enum=['title', '-title', 'avg_rating', '-avg_rating', 
                      'popularity_score', '-popularity_score']
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        queryset = self.get_queryset()
        search_query = request.query_params.get('search', '').strip()
        genres = request.query_params.get('genres', '').split(',')
        min_rating = request.query_params.get('min_rating')
        max_rating = request.query_params.get('max_rating')

        if search_query:
            # Create full-text search query
            search_vector = SearchQuery(search_query, config='english')
            
            # Combine different search methods
            queryset = queryset.annotate(
                rank=SearchRank('search_vector', search_vector),
                title_similarity=TrigramSimilarity('title', search_query),
                overview_similarity=TrigramSimilarity('overview', search_query),
                search_score=Greatest(
                    F('rank'),
                    F('title_similarity'),
                    F('overview_similarity')
                )
            ).filter(
                Q(search_vector=search_vector) |
                Q(title_similarity__gt=0.3) |
                Q(overview_similarity__gt=0.3)
            )

        # Apply filters
        if genres and genres[0]:
            queryset = queryset.filter(genres__overlap=genres)
        
        if min_rating:
            queryset = queryset.filter(avg_rating__gte=float(min_rating))
        
        if max_rating:
            queryset = queryset.filter(avg_rating__lte=float(max_rating))

        # Order by search relevance and popularity
        if search_query:
            queryset = queryset.order_by('-search_score', '-popularity_score')
        else:
            queryset = queryset.order_by('-popularity_score')

        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending movies based on popularity score"""
        queryset = Movie.objects.order_by('-popularity_score')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
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


class UserPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for handling user preferences"""
    serializer_class = UserPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserPreference.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Get user preferences",
        responses={200: UserPreferenceListSerializer}
    )
    def list(self, request):
        """Get user's preferences or return empty default if none exist"""
        preference = self.get_queryset().first()
        if not preference:
            return Response({
                "user": request.user.username,
                "age": None,
                "gender": None,
                "favorite_genres": [],
                "watch_frequency": None,
                "created_at": None,
                "updated_at": None
            }, status=status.HTTP_200_OK)
        
        serializer = UserPreferenceListSerializer(preference)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create or update user preferences",
        request_body=UserPreferenceSerializer,
        responses={
            201: UserPreferenceSerializer,
            200: UserPreferenceSerializer,
            400: "Bad Request - Invalid data"
        }
    )
    def create(self, request, *args, **kwargs):
        """Create or update user preferences"""
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Update specific preference fields",
        request_body=UserPreferenceSerializer,
        responses={
            200: UserPreferenceSerializer,
            400: "Bad Request",
            404: "Not Found"
        }
    )
    @action(detail=False, methods=['put'])
    def update_preferences(self, request):
        """Update specific preference fields"""
        try:
            preference = self.get_queryset().get()
            serializer = self.get_serializer(
                preference,
                data=request.data,
                context={'request': request},
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserPreference.DoesNotExist:
            return Response(
                {"error": "User preferences not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_description="Delete user preferences",
        responses={
            204: "No Content",
            404: "Not Found"
        }
    )
    def destroy(self, request, *args, **kwargs):
        try:
            preference = self.get_queryset().get()
            preference.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserPreference.DoesNotExist:
            return Response(
                {"error": "User preferences not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def perform_create(self, serializer):
        """Ensure user is set when creating preferences"""
        serializer.save(user=self.request.user)


class MovieTasteViewSet(viewsets.ModelViewSet):
    """ViewSet for handling movie taste preferences"""
    serializer_class = MovieTasteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MovieTaste.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Record user's taste for a movie",
        request_body=MovieTasteSerializer
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def my_tastes(self, request):
        """Get all movie tastes for the current user"""
        tastes = self.get_queryset()
        serializer = self.get_serializer(tastes, many=True)
        return Response(serializer.data)