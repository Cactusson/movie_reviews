from django.core.management import BaseCommand

from reviews.models import TaskControl


class Command(BaseCommand):
    help = "Disable task execution"

    def handle(self, *args, **options):
        TaskControl.disable_tasks()
        self.stdout.write(
            self.style.SUCCESS(
                "⛔ Aggregator is INACTIVE and will NOT add new reviews until enabled again"
            )
        )
