from django.db import models


class Review(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(
        "reviews.Author", related_name="reviews", on_delete=models.CASCADE
    )
    url = models.URLField()
    date = models.DateField()
    content = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ("title", "author", "url", "date")
        ordering = ("-date",)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Author(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
