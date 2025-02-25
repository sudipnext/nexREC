from core.services.popularity import PopularityCalculator
from core.utils import DatabaseLogger

logger = DatabaseLogger()


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