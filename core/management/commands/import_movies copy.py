from django.core.management.base import BaseCommand
import json
import os
from django.db import transaction
from core.models import (
    Movie, MovieCrew, MovieCast, 
    ProductionCompany, ProductionCountry, Distributor
)
from datetime import datetime
import uuid
from django.db.models import Q
from tqdm import tqdm

class Command(BaseCommand):
    help = 'Import movies data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='data/perfect_movies.json', 
                          help='Path to the JSON file')
        parser.add_argument('--clean', action='store_true', 
                          help='Clean existing data before import')
        parser.add_argument('--batch-size', type=int, default=500,
                          help='Batch size for bulk operations')

    def truncate_string(self, value, max_length):
        """Helper function to truncate strings to max_length"""
        if isinstance(value, (int, float)):
            value = str(value)
        if value and len(str(value)) > max_length:
            return str(value)[:max_length]
        return value

    def safe_get(self, data, *keys, default=''):
        """Safely get nested dictionary values"""
        try:
            value = data
            for key in keys:
                value = value[key]
            return value if value is not None else default
        except (KeyError, TypeError):
            return default

    def safe_decimal(self, value, default=0):
        """Convert value to decimal safely"""
        if value in (None, '', 'N/A'):
            return default
        try:
            # Remove currency symbols and commas
            if isinstance(value, str):
                value = value.replace('$', '').replace(',', '').strip()
            return float(value)
        except (ValueError, TypeError):
            return default

    def clean_database(self):
        """Clean existing data from the database"""
        self.stdout.write(self.style.WARNING('Cleaning existing data...'))
        
        try:
            with transaction.atomic():
                MovieCast.objects.all().delete()
                MovieCrew.objects.all().delete()
                Movie.objects.all().delete()
                ProductionCompany.objects.all().delete()
                ProductionCountry.objects.all().delete()
                Distributor.objects.all().delete()
                
            self.stdout.write(self.style.SUCCESS('Successfully cleaned existing data'))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error cleaning database: {str(e)}')
            )
            raise

    def handle(self, *args, **kwargs):
        json_file = kwargs.get('file')
        clean = kwargs.get('clean', False)
        batch_size = kwargs.get('batch_size')
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        json_file_path = os.path.join(base_dir, json_file)
        
        self.stdout.write(self.style.SUCCESS(f'Reading file: {json_file_path}'))
        
        if clean:
            self.clean_database()
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                movies_data = json.load(file)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading file: {str(e)}'))
            return

        total_movies = len(movies_data)
        self.stdout.write(self.style.SUCCESS(f'Found {total_movies} movies to process'))

        with transaction.atomic():
            movies_to_create = []
            seen_tmdb_ids = set()
            
            # First pass: Create movies, skip duplicates
            for data in tqdm(movies_data, desc="Processing movies", unit="movie"):
                try:
                    tmdb_id = self.safe_get(data, 'basic_info', 'id', default=0)
                    if tmdb_id in seen_tmdb_ids:
                        continue
                    
                    seen_tmdb_ids.add(tmdb_id)
                    movie = Movie(
                        # Basic Info
                        title=self.truncate_string(self.safe_get(data, 'basic_info', 'title'), 255),
                        original_title=self.truncate_string(self.safe_get(data, 'basic_info', 'original_title'), 255),
                        tmdb_id=tmdb_id,
                        imdb_id=self.safe_get(data, 'ids', 'imdb_id'),
                        ems_id=self.safe_get(data, 'basic_info', 'emsId'),
                        
                        # Content
                        synopsis=self.safe_get(data, 'content', 'synopsis'),
                        overview=self.safe_get(data, 'content', 'overview'),
                        
                        # Scores
                        audience_score=self.safe_decimal(self.safe_get(data, 'scores', 'audience_score')),
                        critics_score=self.safe_decimal(self.safe_get(data, 'scores', 'critics_score')),
                        vote_average=self.safe_decimal(self.safe_get(data, 'scores', 'vote_average')),
                        vote_count=int(self.safe_get(data, 'scores', 'vote_count', default=0) or 0),
                        imdb_rating=self.safe_decimal(self.safe_get(data, 'scores', 'imdb_rating')),
                        imdb_votes=self.safe_decimal(self.safe_get(data, 'scores', 'imdb_votes')),
                        
                        # Technical
                        rating=self.truncate_string(self.safe_get(data, 'technical', 'rating'), 50),
                        runtime=self.safe_get(data, 'technical', 'runtime'),
                        original_language=self.truncate_string(self.safe_get(data, 'technical', 'original_language'), 50),
                        spoken_languages=self.safe_get(data, 'technical', 'spoken_languages'),
                        sound_mix=self.safe_get(data, 'technical', 'sound_mix'),
                        
                        # Release
                        release_date=datetime.strptime(
                            self.safe_get(data, 'release', 'release_date', default='2000-01-01'),
                            '%Y-%m-%d'
                        ).date(),
                        release_date_theaters=self.safe_get(data, 'release', 'release_date_theaters'),
                        release_date_streaming=self.safe_get(data, 'release', 'release_date_streaming'),
                        status=self.truncate_string(self.safe_get(data, 'release', 'status'), 50),
                        
                        # Financial
                        box_office=self.safe_get(data, 'financial', 'box_office'),
                        revenue=self.safe_decimal(self.safe_get(data, 'financial', 'revenue')),
                        budget=self.safe_decimal(self.safe_get(data, 'financial', 'budget')),
                        
                        # Media
                        poster_path=self.truncate_string(self.safe_get(data, 'media', 'posterUri'), 500),
                        media_url=self.safe_get(data, 'media', 'mediaUrl'),
                    )
                    movies_to_create.append(movie)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Error preparing movie: {str(e)}'))
                    continue

            # Bulk create movies with progress bar
            self.stdout.write(self.style.SUCCESS(f'Creating {len(movies_to_create)} movies...'))
            for i in tqdm(range(0, len(movies_to_create), 1000), desc="Saving movies", unit="batch"):
                batch = movies_to_create[i:i + 1000]
                Movie.objects.bulk_create(batch, ignore_conflicts=True)

            # Create a mapping of tmdb_ids to movie objects
            self.stdout.write(self.style.SUCCESS('Creating movie mapping...'))
            movie_map = {movie.tmdb_id: movie for movie in Movie.objects.all()}
            
            # Prepare cast and crew data
            crews_to_create = []
            casts_to_create = []
            processed_movie_ids = set()
            
            self.stdout.write(self.style.SUCCESS('Processing crew and cast data...'))
            for data in tqdm(movies_data, desc="Processing crew/cast", unit="movie"):
                tmdb_id = self.safe_get(data, 'basic_info', 'id')
                movie = movie_map.get(tmdb_id)
                if not movie or movie.id in processed_movie_ids:
                    continue
                
                processed_movie_ids.add(movie.id)

                if 'crew' in data:
                    crews_to_create.append(MovieCrew(
                        movie=movie,
                        director=self.truncate_string(self.safe_get(data, 'crew', 'director'), 255),
                        writers=self.safe_get(data, 'crew', 'writers'),
                    ))

                    cast_str = self.safe_get(data, 'crew', 'cast')
                    if cast_str and isinstance(cast_str, str):
                        for i, actor in enumerate(cast_str.split(', ')):
                            if actor.strip():
                                casts_to_create.append(MovieCast(
                                    movie=movie,
                                    name=self.truncate_string(actor.strip(), 255),
                                    order=i
                                ))

            # Bulk create crews with progress bar
            if crews_to_create:
                self.stdout.write(self.style.SUCCESS(f'Creating {len(crews_to_create)} crew records...'))
                for i in tqdm(range(0, len(crews_to_create), 1000), desc="Saving crew", unit="batch"):
                    batch = crews_to_create[i:i + 1000]
                    MovieCrew.objects.bulk_create(batch, ignore_conflicts=True)

            # Bulk create casts with progress bar
            if casts_to_create:
                self.stdout.write(self.style.SUCCESS(f'Creating {len(casts_to_create)} cast records...'))
                for i in tqdm(range(0, len(casts_to_create), 1000), desc="Saving cast", unit="batch"):
                    batch = casts_to_create[i:i + 1000]
                    MovieCast.objects.bulk_create(batch, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS('Successfully imported all movies and related data')) 