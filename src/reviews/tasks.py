import logging

from celery import shared_task
from django.utils import timezone

from reviews.models import TaskControl
from tools.parse_rss import parse_full_rss_feed, read_feeds_from_json_file

logger = logging.getLogger(__name__)


@shared_task
def collect_new_reviews():
    if not TaskControl.is_task_enabled():
        logger.info("Task skipped - execution disabled")
        return {
            "status": "skipped",
            "reason": "tasks_disabled",
            "timestamp": str(timezone.now()),
        }

    try:
        logger.info("Starting task execution")

        feeds = read_feeds_from_json_file()
        for feed in feeds:
            new_reviews = parse_full_rss_feed(feed)

        logger.info(
            f"Task completed successfully. New reviews created: {len(new_reviews)}"
        )
        return {
            "status": "success",
            "result": str(len(new_reviews)),
            "timestamp": str(timezone.now()),
        }

    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        return {"status": "error", "error": str(e), "timestamp": str(timezone.now())}
