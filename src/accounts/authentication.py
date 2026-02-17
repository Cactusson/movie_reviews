from accounts.models import CustomUser, Token


class PasswordlessAuthenticationBackend:
    def authenticate(self, request, uuid):
        try:
            token = Token.objects.get(uuid=uuid)
            return CustomUser.objects.get(email=token.email)
        except CustomUser.DoesNotExist:
            return CustomUser.objects.create(email=token.email)
        except Token.DoesNotExist:
            return None

    def get_user(self, email):
        try:
            return CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return None
