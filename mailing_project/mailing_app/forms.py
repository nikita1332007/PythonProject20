from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from users.models import CustomUser
from .models import Client, Message, Mailing



class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = '__all__'


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['email', 'start_time', 'end_time', 'message', 'recipients']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@domain.com'
            }),
            'start_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'step': '1',
                'class': 'form-control'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'step': '1',
                'class': 'form-control'
            }),
            'message': forms.Textarea(attrs={
                'rows': 6,
                'class': 'form-control',
                'placeholder': 'Введите текст рассылки...'
            }),
        }
        error_messages = {
            'email': {
                'required': 'Введите email отправителя',
                'invalid': 'Неверный формат email',
            },
            'message': {
                'required': 'Введите текст рассылки',
            },
            'recipients': {
                'required': 'Выберите хотя бы одного получателя',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['recipients'].queryset = Client.objects.all()
        self.fields['recipients'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')

        if start and end:
            if start >= end:
                raise ValidationError('Время начала должно быть раньше времени окончания')
            if start < timezone.now():
                raise ValidationError('Время начала не может быть в прошлом')
        return cleaned_data

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Электронная почта",
        widget=forms.EmailInput(attrs={"autofocus": True, "placeholder": "Введите email"})
    )
