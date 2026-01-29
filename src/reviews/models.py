import re

from bs4 import BeautifulSoup
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


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
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("reviews:author_detail", kwargs={"slug": self.slug})

    @property
    def last_name(self):
        return self.name.split()[-1]


class TaskControl(models.Model):
    is_enabled = models.BooleanField(default=False)
    enabled_at = models.DateTimeField(null=True, blank=True)
    disabled_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def is_task_enabled(cls):
        obj = cls.objects.get_or_create(pk=1)[0]
        return obj.is_enabled

    @classmethod
    def enable_tasks(cls):
        obj = cls.objects.get_or_create(pk=1)[0]
        if not obj.is_enabled:
            obj.is_enabled = True
            obj.enabled_at = timezone.now()
            obj.save()

    @classmethod
    def disable_tasks(cls):
        obj = cls.objects.get_or_create(pk=1)[0]
        if obj.is_enabled:
            obj.is_enabled = False
            obj.disabled_at = timezone.now()
            obj.save()
