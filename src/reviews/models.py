from typing import Any

from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

USER_MODEL = get_user_model()


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

    def __str__(self) -> str:
        return self.title

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("reviews:review_detail", kwargs={"pk": self.pk})

    @property
    def formatted_date(self) -> str:
        return self.date.strftime("%B %d, %Y")

    @property
    def first_sentence(self) -> str | None:
        if self.content is None:
            return None
        text = BeautifulSoup(self.content, "html.parser").get_text()[:200].rstrip()
        last_space_index = text.rfind(" ")
        return text[:last_space_index] + "..."


class Author(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    followers: models.ManyToManyField[AbstractBaseUser, Author] = (
        models.ManyToManyField(USER_MODEL, related_name="follows", blank=True)
    )

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("reviews:author_detail", kwargs={"slug": self.slug})

    @property
    def last_name(self) -> str:
        return self.name.split()[-1]

    def follow(self, user: AbstractBaseUser) -> None:
        self.followers.add(user)

    def unfollow(self, user: AbstractBaseUser) -> None:
        self.followers.remove(user)


class TaskControl(models.Model):
    is_enabled = models.BooleanField(default=False)
    enabled_at = models.DateTimeField(null=True, blank=True)
    disabled_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def is_task_enabled(cls) -> bool:
        obj = cls.objects.get_or_create(pk=1)[0]
        return obj.is_enabled

    @classmethod
    def enable_tasks(cls) -> None:
        obj = cls.objects.get_or_create(pk=1)[0]
        if not obj.is_enabled:
            obj.is_enabled = True
            obj.enabled_at = timezone.now()
            obj.save()

    @classmethod
    def disable_tasks(cls) -> None:
        obj = cls.objects.get_or_create(pk=1)[0]
        if obj.is_enabled:
            obj.is_enabled = False
            obj.disabled_at = timezone.now()
            obj.save()
