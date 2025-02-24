from django.core.management.base import BaseCommand
import csv
import os
from django.db import transaction
from core.models import Movie
from tqdm import tqdm
from decimal import Decimal
import json

class Command(BaseCommand):
    help = 'Import movies data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='data/dump_for_insertion.csv', 
                          help='Path to the CSV file')
        parser.add_argument('--clean', action='store_true', 
                          help='Clean existing data before import')
        parser.add_argument('--batch-size', type=int, default=1000,
                          help='Batch size for bulk operations')

    def clean_database(self):
        """Clean existing data from the database"""
        self.stdout.write(self.style.WARNING('Cleaning existing data...'))
        try:
            with transaction.atomic():
                Movie.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Successfully cleaned existing data'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error cleaning database: {str(e)}'))
            raise

    def parse_json_field(self, value, default=None):
        """Safely parse JSON string to list/dict"""
        if not value:
            return default or []
        
        # If value is already a list, return it
        if isinstance(value, list):
            return value
            
        # If value is a string, try parsing as JSON first
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # If JSON parsing fails, try handling as comma-separated string
                try:
                    items = [item.strip() for item in value.split(',') if item.strip()]
                    return items
                except:
                    return default or []
        
        return default or []

    def safe_decimal(self, value, default=0):
        """Convert value to decimal safely"""
        if not value or value in ('', 'N/A'):
            return default
        try:
            return Decimal(str(value))
        except:
            return default

    def safe_int(self, value, default=None):
        """Safely convert value to integer, handling float strings"""
        if not value:
            return default
        try:
            # First convert to float, then to int
            return int(float(str(value)))
        except (ValueError, TypeError):
            return default

    def handle(self, *args, **kwargs):
        file_path = kwargs['file']
        clean = kwargs.get('clean', False)
        batch_size = kwargs.get('batch-size', 100)

        if clean:
            self.clean_database()

        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                # Read first line to get column names
                reader = csv.DictReader(csvfile)
                # Get total rows for progress bar
                total_rows = sum(1 for line in csvfile)
                csvfile.seek(0)
                next(reader)  # Skip header

                movies_to_create = []
                processed = 0
                failed = 0

                # Process rows with progress bar
                for row in tqdm(reader, total=total_rows-1, desc="Processing movies"):
                    try:
                        # Map CSV fields to model fields
                        movie = Movie(
                            ems_id=row.get('emsId', ''),  # Changed from ems_id to emsId
                            title=row.get('title', ''),
                            synopsis=row.get('synopsis', ''),
                            director=row.get('director', ''),
                            producer=row.get('producer', ''),
                            screenwriter=row.get('screenwriter', ''),
                            distributor=row.get('distributor', ''),
                            rating=row.get('rating', ''),
                            original_language=row.get('original_language', ''),
                            movie_index=self.safe_int(row.get('movie_index')),
                            overview=row.get('overview', ''),
                            tagline=row.get('tagline', ''),
                            genres=self.parse_json_field(row.get('genres')),
                            production_companies=self.parse_json_field(row.get('production_companies')),
                            production_countries=self.parse_json_field(row.get('production_countries')),
                            spoken_languages=self.parse_json_field(row.get('spoken_languages')),
                            cast=self.parse_json_field(row.get('cast')),
                            director_of_photography=row.get('director_of_photography', ''),
                            writers=row.get('writers', ''),
                            producers=row.get('producers', ''),
                            music_composer=row.get('music_composer', ''),
                            avg_rating=self.safe_decimal(row.get('avg_rating')),
                            combined_text=row.get('combined_text', ''),
                            posterUri=row.get('posterUri', ''),
                            # Add new fields from your CSV
                            audienceScore=row.get('audienceScore'),
                            criticsScore=row.get('criticsScore'),
                            mediaUrl=row.get('mediaUrl', '')
                        )
                        movies_to_create.append(movie)

                        # Bulk create when batch size is reached
                        if len(movies_to_create) >= batch_size:
                            created = Movie.objects.bulk_create(
                                movies_to_create,
                                batch_size=batch_size,
                                ignore_conflicts=True
                            )
                            processed += len(created)
                            movies_to_create = []
                            # Log progress
                            self.stdout.write(self.style.SUCCESS(f'Processed {processed} movies'))

                    except Exception as e:
                        failed += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f'Error processing movie {row.get("title")}: {str(e)}'
                            )
                        )

                # Create remaining movies
                if movies_to_create:
                    try:
                        created = Movie.objects.bulk_create(
                            movies_to_create,
                            batch_size=batch_size,
                            ignore_conflicts=True
                        )
                        processed += len(created)
                    except Exception as e:
                        failed += len(movies_to_create)
                        self.stdout.write(
                            self.style.ERROR(f'Error in final batch: {str(e)}')
                        )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Import completed. Processed: {processed}, Failed: {failed}'
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading file: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Successfully imported all movies'))