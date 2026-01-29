from django.core.management import BaseCommand

from reviews.models import TaskControl


class Command(BaseCommand):
    help = "Check task execution status"

    def handle(self, *args, **options):
        if TaskControl.is_task_enabled():
            self.stdout.write(
                self.style.SUCCESS(
                    "✅ Aggregator is ACTIVE and will add new reviews every hour"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "⛔ Aggregator is INACTIVE and will NOT add new reviews until enabled again"
                )
            )
