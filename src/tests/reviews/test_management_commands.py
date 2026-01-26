import pytest
from django.core.management import call_command

from reviews.models import Review


@pytest.mark.django_db
class TestCollectReviewsCommand:
    def test_20_new_reviews_in_database_after_command_is_executed(
        self, mocked_rss_feed
    ):
        assert Review.objects.count() == 0
        call_command(
            "collect_reviews", "--feeds", "https://www.rogerebert.com/reviews/feed/"
        )
        assert Review.objects.count() == 20
