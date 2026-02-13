from django.core.management.base import BaseCommand

from reviews.parsers import collect_movies_from_feeds


class Command(BaseCommand):
    help = "Collects new movie reviews."

    def add_arguments(self, parser):
        parser.add_argument(
            "--init",
            action="store_true",
            help="Use when collecting reviews for the first time",
        )

    def handle(self, *args, **options):
        if options["init"]:
            collect_movies_from_feeds(ignore_cutoff_date=True)
        else:
            collect_movies_from_feeds()
