from django.core.management.base import BaseCommand

from tools.parse_rss import parse_full_rss_feed, read_feeds_from_json_file


class Command(BaseCommand):
    help = "Collects new movie reviews."

    def add_arguments(self, parser):
        parser.add_argument(
            "--init",
            action="store_true",
            help="Use when collecting reviews for the first time",
        )

    def handle(self, *args, **options):
        feeds = read_feeds_from_json_file()
        for feed in feeds:
            if options["init"]:
                parse_full_rss_feed(feed, ignore_cutoff_date=True)
            else:
                parse_full_rss_feed(feed)
