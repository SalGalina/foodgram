from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from .models import Recipe, Favorite


class IngredientSearchFilter(SearchFilter):
    """Фильтрация Продуктов по Названию"""
    search_param = 'name'


class RecipeFilter(FilterSet):
    """Фильтрация Рецептов по Избранному, Списку покупок и Тэгам"""
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_card'
    )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        lookup_expr='iexact'
    )

    def filter_is_favorited(self, queryset, field_name, value):
        if value:
            return queryset.filter(favorites__owner=self.request.user)
        return queryset

    def filter_is_in_shopping_card(self, queryset, field_name, value):
        if value:
            return queryset.filter(shoppings__owner=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['author', 'is_favorited', 'is_in_shopping_cart', 'tags', ]
