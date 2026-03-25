from typing import Any

from django.core.management import BaseCommand

from reviews.models import TaskControl


class Command(BaseCommand):
    help: str = "Enable task execution"

    def handle(self, *args: Any, **options: Any) -> None:
        TaskControl.enable_tasks()
        self.stdout.write(
            self.style.SUCCESS(
                "✅ Aggregator is ACTIVE and will add new reviews every hour"
            )
        )
