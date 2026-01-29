from unittest.mock import patch

import pytest

from reviews.models import Review, TaskControl
from reviews.tasks import collect_new_reviews


@pytest.mark.django_db(transaction=True)
class TestCollectNewReviews:
    @pytest.fixture(autouse=True)
    def clear_task_control(self):
        TaskControl.objects.all().delete()
        yield
        TaskControl.objects.all().delete()

    @patch(
        "reviews.tasks.read_feeds_from_json_file",
        return_value=["https://www.rogerebert.com/reviews/feed/"],
    )
    def test_20_new_reviews_in_database_after_task_is_executed(
        self, mocked_function, mocked_rss_feed
    ):
        assert Review.objects.count() == 0
        TaskControl.objects.create(pk=1, is_enabled=True)
        collect_new_reviews()
        assert Review.objects.count() == 20

    @patch(
        "reviews.tasks.read_feeds_from_json_file",
        return_value=[
            "https://www.rogerebert.com/reviews/feed/",
            "https://www.indiewire.com/c/criticism/movies/feed/",
        ],
    )
    def test_task_does_not_add_more_reviews_on_second_run(
        self, mocked_function, mocked_rss_feed
    ):
        assert Review.objects.count() == 0
        TaskControl.objects.create(pk=1, is_enabled=True)
        collect_new_reviews()
        assert Review.objects.count() == 32
        collect_new_reviews()
        assert Review.objects.count() == 32

    @patch(
        "reviews.tasks.read_feeds_from_json_file",
        return_value=["https://www.rogerebert.com/reviews/feed/"],
    )
    def test_task_does_nothing_if_task_control_is_disabled(
        self, mocked_function, mocked_rss_feed
    ):
        assert Review.objects.count() == 0
        TaskControl.objects.create(pk=1, is_enabled=False)
        collect_new_reviews()
        assert Review.objects.count() == 0
