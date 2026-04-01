from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('guest', 'Гость'),
        ('client', 'Клиент'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')

    # Добавляем related_name, чтобы избежать конфликта со стандартной моделью User
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.'
    )

    def __str__(self):
        return f"{self.full_name} ({self.username})"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'