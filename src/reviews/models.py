import re

from bs4 import BeautifulSoup
from django.db import models
from django.urls import reverse


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

    def get_absolute_url(self):
        return reverse("reviews:review_detail", kwargs={"pk": self.pk})

    @property
    def formatted_date(self):
        return self.date.strftime("%B %d, %Y")

    @property
    def first_sentence(self):
        if self.content is None:
            return None
        content = BeautifulSoup(self.content, "html.parser").get_text()
        match = re.match(r"^.*?[.!?](?:\s|$)", content)
        if match:
            return match.group(0).strip()
        return content.strip()


class Author(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
