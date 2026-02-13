import time
from unittest.mock import patch

import pytest
from django.core.management import call_command

from reviews.models import Review, TaskControl
from reviews.parsers import IndieWireParser, RogerEbertParser


@pytest.mark.django_db
class TestCollectReviewsCommand:
    @patch(
        "reviews.parsers.collect_parsers",
        return_value=[("https://www.rogerebert.com/reviews/feed/", RogerEbertParser)],
    )
    def test_20_new_reviews_in_database_after_command_is_executed(
        self, mocked_function, mocked_rss_feed
    ):
        assert Review.objects.count() == 0
        call_command("collect_reviews")
        assert Review.objects.count() == 20

    @patch(
        "reviews.parsers.collect_parsers",
        return_value=[
            (
                "https://www.rogerebert.com/reviews/feed_with_old_entries/",
                RogerEbertParser,
            )
        ],
    )
    def test_will_ignore_cutoff_date_if_init_is_passed(
        self, mocked_function, mocked_rss_feed
    ):
        assert Review.objects.count() == 0
        call_command("collect_reviews", "--init")
        assert Review.objects.count() == 3

    @patch(
        "reviews.parsers.collect_parsers",
        return_value=[
            ("https://www.rogerebert.com/reviews/feed/", RogerEbertParser),
            ("https://www.indiewire.com/c/criticism/movies/feed/", IndieWireParser),
        ],
    )
    def test_parse_multiple_feeds(self, mocked_function, mocked_rss_feed):
        assert Review.objects.count() == 0
        call_command("collect_reviews")
        assert Review.objects.count() == 32


@pytest.mark.django_db
class TestTaskControlCommands:
    @pytest.fixture(autouse=True)
    def setup_db(self):
        TaskControl.objects.all().delete()
        yield
        TaskControl.objects.all().delete()

    def test_enable_tasks_creates_record(self):
        assert TaskControl.objects.count() == 0

        call_command("start")

        assert TaskControl.objects.count() == 1
        control = TaskControl.objects.get(pk=1)
        assert control.is_enabled is True

    def test_disable_tasks_updates_record(self):
        TaskControl.objects.create(pk=1, is_enabled=True)

        call_command("stop")

        control = TaskControl.objects.get(pk=1)
        assert control.is_enabled is False
        assert control.disabled_at is not None

    def test_enable_tasks_when_already_enabled(self):
        TaskControl.objects.create(pk=1, is_enabled=False)
        TaskControl.enable_tasks()
        enabled_at = TaskControl.objects.get(pk=1).enabled_at
        time.sleep(0.01)

        call_command("start")

        assert TaskControl.objects.get(pk=1).enabled_at == enabled_at

    def test_disable_tasks_when_already_disabled(self):
        TaskControl.objects.create(pk=1, is_enabled=True)
        TaskControl.disable_tasks()
        disabled_at = TaskControl.objects.get(pk=1).disabled_at
        time.sleep(0.01)

        call_command("stop")

        assert TaskControl.objects.get(pk=1).disabled_at == disabled_at

    def test_concurrent_calls(self):
        assert TaskControl.objects.count() == 0

        for i in range(3):
            call_command("start")
            time.sleep(0.1)

        # Should still have only one record
        assert TaskControl.objects.count() == 1
        assert TaskControl.objects.get(pk=1).is_enabled is True
