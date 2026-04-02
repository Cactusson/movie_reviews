import uuid
from typing import TYPE_CHECKING, Any

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone

if TYPE_CHECKING:
    from reviews.models import Author


class Token(models.Model):
    email = models.EmailField()
    uuid = models.UUIDField(default=uuid.uuid4, max_length=40)


class CustomUserManager(BaseUserManager["CustomUser"]):
    def create_user(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "CustomUser":
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "CustomUser":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser):
    email = models.EmailField(primary_key=True)
    email_notifications = models.BooleanField(default=False)
    letterboxd_user = models.OneToOneField(
        "reviews.LetterboxdUser",
        related_name="user",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    follows: models.QuerySet[Author]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    def __str__(self) -> str:
        return self.email
