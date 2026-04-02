from unittest import mock
from unittest.mock import patch

import pytest
from django.test import override_settings

from reviews.models import Review, TaskControl
from reviews.parsers import IndieWireParser, RogerEbertParser
from reviews.tasks import collect_new_reviews


@pytest.mark.django_db(transaction=True)
class TestCollectNewReviews:
    @pytest.fixture(autouse=True)
    def clear_task_control(self):
        TaskControl.objects.all().delete()
        yield
        TaskControl.objects.all().delete()

    @patch(
        "reviews.parsers.collect_parsers",
        return_value=[("https://www.rogerebert.com/reviews/feed/", RogerEbertParser)],
    )
    def test_20_new_reviews_in_database_after_task_is_executed(
        self, mocked_function, mocked_rss_feed
    ):
        assert Review.objects.count() == 0
        TaskControl.objects.create(pk=1, is_enabled=True)
        collect_new_reviews()
        assert Review.objects.count() == 20

    @patch(
        "reviews.parsers.collect_parsers",
        return_value=[
            ("https://www.rogerebert.com/reviews/feed/", RogerEbertParser),
            ("https://www.indiewire.com/c/criticism/movies/feed/", IndieWireParser),
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
        "reviews.parsers.collect_parsers",
        return_value=[("https://www.rogerebert.com/reviews/feed/", RogerEbertParser)],
    )
    def test_task_does_nothing_if_task_control_is_disabled(
        self, mocked_function, mocked_rss_feed
    ):
        assert Review.objects.count() == 0
        TaskControl.objects.create(pk=1, is_enabled=False)
        collect_new_reviews()
        assert Review.objects.count() == 0

    @override_settings(
        RSS_PARSERS={"https://www.rogerebert.com/reviews/feed/": "RogerEbertParser"}
    )
    @mock.patch("reviews.notifications.send_mail")
    def test_user_receives_email_after_task_completes(
        self, mock_send_mail, mocked_rss_feed, first_user, mzs
    ):
        first_user.email_notifications = True
        first_user.save()
        TaskControl.objects.create(pk=1, is_enabled=True)
        mzs.follow(first_user)
        collect_new_reviews()

        assert mock_send_mail.called is True

    @override_settings(
        RSS_PARSERS={"https://www.rogerebert.com/reviews/feed/": "RogerEbertParser"}
    )
    @mock.patch("reviews.notifications.send_mail")
    def test_two_users_receive_emails_after_task_completes(
        self, mock_send_mail, mocked_rss_feed, first_user, second_user, sheila
    ):
        first_user.email_notifications = True
        first_user.save()
        second_user.email_notifications = True
        second_user.save()
        TaskControl.objects.create(pk=1, is_enabled=True)
        sheila.follow(first_user)
        sheila.follow(second_user)
        collect_new_reviews()

        assert mock_send_mail.call_count == 2

    @override_settings(
        RSS_PARSERS={"https://www.rogerebert.com/reviews/feed/": "RogerEbertParser"}
    )
    @mock.patch("reviews.notifications.send_mail")
    def test_user_receives_only_one_email(
        self, mock_send_mail, mocked_rss_feed, first_user, mzs, sheila
    ):
        first_user.email_notifications = True
        first_user.save()
        TaskControl.objects.create(pk=1, is_enabled=True)
        mzs.follow(first_user)
        sheila.follow(first_user)
        collect_new_reviews()

        assert mock_send_mail.call_count == 1

    @override_settings(
        RSS_PARSERS={"https://www.rogerebert.com/reviews/feed/": "RogerEbertParser"}
    )
    @mock.patch("reviews.notifications.send_mail")
    def test_user_with_disabled_notifications_will_not_receive_email(
        self, mock_send_mail, mocked_rss_feed, first_user, mzs
    ):
        first_user.email_notifications = False
        first_user.save()
        TaskControl.objects.create(pk=1, is_enabled=True)
        mzs.follow(first_user)
        collect_new_reviews()

        assert mock_send_mail.call_count == 0
