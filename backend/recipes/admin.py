from django import forms
from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from .fields import ColorField


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Администрирование Продуктов."""

    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Администрирование Тэгов."""

    prepopulated_fields = {'slug': ('name',)}
    list_display = ('pk', 'name', 'slug', 'colortile')
    formfield_overrides = {
        ColorField: {
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
    list_filter = ('author', 'tags')
    empty_value_display = '-пусто-'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Администрирование Продуктов для рецепта."""

    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    search_fields = ('ingredient__name', 'recipe__author')
    list_filter = ('recipe__author',)
    empty_value_display = '-пусто-'


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    """Администрирование Тэгов для рецепта."""

    list_display = ('pk', 'recipe', 'tag')
    search_fields = ('tag__name', 'recipe__author')
    list_filter = ('recipe__author',)
    empty_value_display = '-пусто-'
