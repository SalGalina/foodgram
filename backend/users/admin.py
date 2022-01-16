from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Subscribe

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Администрирование Пользователей."""

    list_display = (
        'pk',
        'email',
        'username',
        'first_name',
        'last_name',
    )
    search_fields = ('email', 'username')
    empty_value_display = '-пусто-'


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    """Администрирование Подписок."""

    list_display = ('pk', 'author', 'user')
    search_fields = ('author', 'user')
    list_filter = ('author',)
    empty_value_display = '-пусто-'
