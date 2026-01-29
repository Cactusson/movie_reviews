import json

from celery import shared_task

from tools.parse_rss import parse_full_rss_feed


@shared_task
def collect_new_reviews(test_environment=False):
    if test_environment:
        parse_full_rss_feed("https://www.rogerebert.com/reviews/feed/")
        return

    with open("config/feeds.json") as file:
        feeds = json.load(file)
    for feed in feeds:
        parse_full_rss_feed(feed)
