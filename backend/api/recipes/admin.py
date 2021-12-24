from django import forms
from django.contrib import admin

from .models import Ingredient, Recipe, Tag
import fields


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Администрирование Продуктов."""

    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name', )
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Администрирование Тэгов."""

    prepopulated_fields = {'slug': ('name',)}
    list_display = ('pk', 'name', 'slug', 'colortile')
    formfield_overrides = {
        fields.ColorField: {
            'widget': forms.TextInput(
                attrs={'type': 'color',
                       'style': 'height: 100px; width: 100px;'}
            )
        }
    }
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Администрирование Рецептов."""

    list_display = ('pk', 'name', 'author')
    search_fields = ('name', 'author', 'tags')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
