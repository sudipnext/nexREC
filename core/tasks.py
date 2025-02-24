from core.services.popularity import PopularityCalculator
from core.utils import DatabaseLogger
import logging

db_logger = DatabaseLogger()

# Setup logging
logger = logging.getLogger(__name__)


def update_movie_popularity_scores():
    """Update popularity scores for all movies"""
    try:
        PopularityCalculator.update_all_popularity_scores()
        logger.info("Successfully updated movie popularity scores")
    except Exception as e:
        logger.error(f"Error updating movie popularity scores: {str(e)}")