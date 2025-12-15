from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from mailing_project.mailing_project import settings


class Client(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)

    def __str__(self):
        return f'{self.full_name} <{self.email}>'


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Client)

    def clean(self):
        # Проверяем, что start_time не в прошлом
        if self.start_time < timezone.now():
            raise ValidationError({'start_time': 'Дата и время начала не могут быть в прошлом.'})

        if self.start_time >= self.end_time:
            raise ValidationError({'end_time': 'Дата и время окончания должна быть позже даты начала.'})

    @property
    def status(self):
        now = timezone.now()
        if now < self.start_time:
            return 'Создана'
        elif self.start_time <= now <= self.end_time:
            return 'Запущена'
        else:
            return 'Завершена'

    def __str__(self):
        return f'Рассылка #{self.pk} ({self.status})'


class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ('Успешно', 'Успешно'),
        ('Не успешно', 'Не успешно'),
    ]

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='attempts')
    attempt_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    server_response = models.TextField(blank=True)

    def __str__(self):
        return f'Попытка #{self.pk} рассылки #{self.mailing.pk} – {self.status} в {self.attempt_time}'


class Client(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='clients')

class Mailing(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mailings')