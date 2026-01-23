from django.db import models


class Review(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(
        "reviews.Author", related_name="reviews", on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Author(models.Model):
    name = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
