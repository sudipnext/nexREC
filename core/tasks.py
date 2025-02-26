from core.services.popularity import PopularityCalculator
from core.utils import DatabaseLogger
from django.contrib.postgres.search import SearchVector
from django.db import transaction
from .models import Movie
import logging

logger = logging.getLogger(__name__)

def update_movie_popularity_scores():
    """Update popularity scores for all movies"""
    try:
        PopularityCalculator.update_all_popularity_scores()
        logger.info("Successfully updated movie popularity scores")
    except Exception as e:
        logger.error(f"Error updating movie popularity scores: {str(e)}")


def test_hello_every_minute():
    """Test cron job"""
    logger.log('INFO', 'Hello, every minute!', 'test_hello_every_minute')


def update_search_vectors():
    """Update search vectors for all movies"""
    try:
        with transaction.atomic():
            Movie.objects.update(search_vector=(
                SearchVector('title', weight='A') +
                SearchVector('overview', weight='B') +
                SearchVector('tagline', weight='B') +
                SearchVector('director', weight='C') +
                SearchVector('cast', weight='D')
            ))
            logger.info("Successfully updated search vectors for all movies")
    except Exception as e:
        logger.error(f"Failed to update search vectors: {str(e)}")