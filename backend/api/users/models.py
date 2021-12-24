from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from pytils.translit import slugify


class User(AbstractUser):
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
    )

    email = models.EmailField(
        verbose_name='Эл.почта',
        max_length=100,
        unique=True,
        error_messages={
            'unique': 'Пользователь с такой почтой уже существует',
        },
    )
    is_subscribed = models.BooleanField(
        verbose_name='Подписан?',
        default=False,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']

    def __str__(self):
        return f'{self.email[:20]}'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='subscriber',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='author',
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
        return f'Подписка {self.user} на {self.author}'

    def get_absolute_url(self):
        return reverse('subscriptions')
