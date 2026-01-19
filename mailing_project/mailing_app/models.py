from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Client(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='clients')
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
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Владелец'
    )
    email = models.EmailField('Email отправителя')
    start_time = models.DateTimeField('Время начала')
    end_time = models.DateTimeField('Время окончания')
    message = models.TextField('Сообщение')
    recipients = models.ManyToManyField(
        Client,
        verbose_name='Получатели',
        blank=False
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        super().clean()
        if self.start_time is None or self.end_time is None:
            raise ValidationError('Время начала и окончания должно быть установлено.')

        if self.start_time < timezone.now():
            raise ValidationError({'start_time': 'Дата и время начала не могут быть в прошлом.'})

        if self.start_time >= self.end_time:
            raise ValidationError({'end_time': 'Дата и время окончания должны быть позже даты начала.'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def status(self):
        from django.utils import timezone
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
        ('success', 'Успешно'),
        ('failed', 'Не успешно'),
    ]

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='attempts')
    attempt_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    server_response = models.TextField(blank=True)

    def __str__(self):
        return f'Попытка #{self.pk} рассылки #{self.mailing.pk} – {self.get_status_display()} в {self.attempt_time}'
