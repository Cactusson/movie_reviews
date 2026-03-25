from uuid import UUID

from django.http import HttpRequest

from accounts.models import CustomUser, Token


class PasswordlessAuthenticationBackend:
    def authenticate(self, request: HttpRequest, uuid: UUID) -> CustomUser | None:
        try:
            token = Token.objects.get(uuid=uuid)
            return CustomUser.objects.get(email=token.email)
        except CustomUser.DoesNotExist:
            return CustomUser.objects.create(email=token.email)
        except Token.DoesNotExist:
            return None

    def get_user(self, email: str) -> CustomUser | None:
        try:
            return CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return None
