from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from accounts.models import CustomUser
from reviews.models import Review


def notify_users(new_reviews: list[Review]) -> None:
    users_to_notify: set[CustomUser] = set()
    for review in new_reviews:
        users_to_notify.update(review.author.followers.all())
    for user in users_to_notify:
        if not user.email_notifications:
            continue
        relative_url = reverse("reviews:home_page")
        url = f"{settings.DOMAIN}{relative_url}"
        send_mail(
            "New Reviews Published",
            f"The authors you follow have published new reviews. Check them out: {url}",
            "noreply@movie_reviews",
            [user.email],
        )
