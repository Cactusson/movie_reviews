import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("reviews")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "collect_new_reviews": {
        "task": "reviews.tasks.collect_new_reviews",
        "schedule": crontab(minute="0"),
        "options": {"expires": 3630},
    }
}
