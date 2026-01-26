import json

from django.core.management.base import BaseCommand

from tools.parse_rss import parse_full_rss_feed


class Command(BaseCommand):
    help = "Collects new movie reviews."

    def add_arguments(self, parser):
        parser.add_argument("--feeds", nargs="+", help="Override default feeds")

    def get_feeds(self, options):
        # pass --feeds option in tests
        if options.get("feeds"):
            return options["feeds"]
        with open("config/feeds.json") as file:
            return json.load(file)

    def handle(self, *args, **options):
        feeds = self.get_feeds(options)
        for feed in feeds:
            parse_full_rss_feed(feed)
