from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from .managers import CreateSuperUserManager


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Эл.почта',
        max_length=254,
        blank=False,
        unique=True,
        error_messages={
            'unique': 'Пользователь с такой почтой уже существует',
        },
    )
    username = models.CharField(
        verbose_name='Ник',
        max_length=150,
        blank=False,
        unique=True,
        error_messages={
            'unique': 'Пользователь с таким username уже существует',
        },
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = CreateSuperUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-id']

    def __str__(self):
        return f'{self.email[:20]} {self.username[:20]}'

    def get_absolute_url(self):
        return reverse('users')


class Subscribe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецептов',
        related_name='subscribing',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='subscribers',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписку'
        verbose_name_plural = 'Подписки'
        ordering = ['author', 'user']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_author_user_subscribing'
            )
        ]

    def __str__(self):
        return f'Подписка {self.user.username} на {self.author.username}'

    def get_absolute_url(self):
        return reverse('subscriptions')
