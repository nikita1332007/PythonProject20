from django import forms
from django.utils import timezone
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
        fields = '__all__'

    def clean_start_time(self):
        start_time = self.cleaned_data['start_time']
        if start_time < timezone.now():
            raise forms.ValidationError('Дата и время начала не могут быть в прошлом.')
        return start_time

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            self.add_error('end_time', 'Дата и время окончания должна быть позже даты начала.')
