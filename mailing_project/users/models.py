from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLES = (
        ('user', 'Пользователь'),
        ('manager', 'Менеджер'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='user')
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.username