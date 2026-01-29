import time
from unittest.mock import patch

import pytest
from django.core.management import call_command

from reviews.models import Review, TaskControl


@pytest.mark.django_db
class TestCollectReviewsCommand:
    @patch("reviews.management.commands.collect_reviews.read_feeds_from_json_file")
    def test_20_new_reviews_in_database_after_command_is_executed(
        self, mock_function, mocked_rss_feed
    ):
        assert Review.objects.count() == 0
        mock_function.return_value = ["https://www.rogerebert.com/reviews/feed/"]
        call_command("collect_reviews")
        assert Review.objects.count() == 20

    @patch("reviews.management.commands.collect_reviews.read_feeds_from_json_file")
    def test_will_ignore_cutoff_date_if_init_is_passed(
        self, mock_function, mocked_rss_feed
    ):
        assert Review.objects.count() == 0
        mock_function.return_value = [
            "https://www.rogerebert.com/reviews/feed_with_old_entries/"
        ]
        call_command("collect_reviews", "--init")
        assert Review.objects.count() == 3

    @patch("reviews.management.commands.collect_reviews.read_feeds_from_json_file")
    def test_parse_multiple_feeds(self, mock_function, mocked_rss_feed):
        assert Review.objects.count() == 0
        mock_function.return_value = [
            "https://www.rogerebert.com/reviews/feed/",
            "https://www.indiewire.com/c/criticism/movies/feed/",
        ]
        call_command("collect_reviews")
        assert Review.objects.count() == 32


class TestTaskControlCommands:
    @pytest.fixture(autouse=True)
    def setup_db(self, db):
        TaskControl.objects.all().delete()
        yield
        TaskControl.objects.all().delete()

    def test_enable_tasks_creates_record(self, db):
        assert TaskControl.objects.count() == 0

        call_command("start")

        assert TaskControl.objects.count() == 1
        control = TaskControl.objects.get(pk=1)
        assert control.is_enabled is True

    def test_disable_tasks_updates_record(self, db):
        TaskControl.objects.create(pk=1, is_enabled=True)

        call_command("stop")

        control = TaskControl.objects.get(pk=1)
        assert control.is_enabled is False
        assert control.disabled_at is not None

    def test_enable_tasks_when_already_enabled(self, db):
        TaskControl.objects.create(pk=1, is_enabled=False)
        TaskControl.enable_tasks()
        enabled_at = TaskControl.objects.get(pk=1).enabled_at
        time.sleep(0.01)

        call_command("start")

        assert TaskControl.objects.get(pk=1).enabled_at == enabled_at

    def test_disable_tasks_when_already_disabled(self, db):
        TaskControl.objects.create(pk=1, is_enabled=True)
        TaskControl.disable_tasks()
        disabled_at = TaskControl.objects.get(pk=1).disabled_at
        time.sleep(0.01)

        call_command("stop")

        assert TaskControl.objects.get(pk=1).disabled_at == disabled_at

    def test_concurrent_calls(self, db):
        assert TaskControl.objects.count() == 0

        for i in range(3):
            call_command("start")
            time.sleep(0.1)

        # Should still have only one record
        assert TaskControl.objects.count() == 1
        assert TaskControl.objects.get(pk=1).is_enabled is True
