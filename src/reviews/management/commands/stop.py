from typing import Any

from django.core.management import BaseCommand

from reviews.models import TaskControl


class Command(BaseCommand):
    help: str = "Disable task execution"

    def handle(self, *args: Any, **options: Any) -> None:
        TaskControl.disable_tasks()
        self.stdout.write(
            self.style.SUCCESS(
                "⛔ Aggregator is INACTIVE and will NOT add new reviews until enabled again"
            )
        )
