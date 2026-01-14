from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2')
