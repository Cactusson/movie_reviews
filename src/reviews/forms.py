from django.contrib.auth import get_user_model
from django.forms import ModelForm

USER_MODEL = get_user_model()


class SettingsForm(ModelForm):
    class Meta:
        model = USER_MODEL
        fields = ["email_notifications", "letterboxd_user"]
        labels = {
            "email_notifications": "Email notifications",
            "letterboxd_user": "Your Letterboxd account",
        }
