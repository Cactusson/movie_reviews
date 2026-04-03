from django import forms
from django.contrib.auth import get_user_model

USER_MODEL = get_user_model()


class SettingsForm(forms.Form):
    email_notifications = forms.BooleanField(
        required=False,
        label="Email notifications",
    )
    letterboxd_username = forms.CharField(
        required=False,
        label="Your Letterboxd account",
    )
