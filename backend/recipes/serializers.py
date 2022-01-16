from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import (
    Ingredient, Recipe, RecipeIngredient, Tag,
    Favorite, Shopping)
from users.serializers import ProfileSerializer

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Получение списка Тэгов/ Тэга"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class AddIngredientSerializer(serializers.ModelSerializer):
    """Добавление ингредиентов в Рецепт"""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class IngredientSerializer(serializers.ModelSerializer):
    """Получение списка Продуктов/ Продукта"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientAmountSerializer(serializers.ModelSerializer):
    """Получение списка Продуктов Рецепта с количеством"""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Получение списка Рецептов/ Рецепта"""

    tags = TagSerializer(many=True)
    author = ProfileSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = [f.name for f in User._meta.get_fields()]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.favorites.filter(owner=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.shoppings.filter(owner=request.user).exists()

    def get_ingredients(self, obj):
        return RecipeIngredientAmountSerializer(
            RecipeIngredient.objects.filter(recipe=obj), many=True
        ).data


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Создание Рецепта"""

    author = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    ingredients = AddIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'author',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def to_representation(self, obj):
        return RecipeSerializer(
            obj,
            context={'request': self.context.get('request')}
        ).data

    def add_tags(self, tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def add_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags(tags, recipe)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, obj, validated_data):
        obj.image = validated_data.get('image', obj.image)
        obj.name = validated_data.get('name', obj.name)
        obj.text = validated_data.get('text', obj.text)
        obj.cooking_time = validated_data.get(
            'cooking_time', obj.cooking_time)
        obj.tags.clear()
        tags = validated_data.get('tags')
        self.add_tags(tags, obj)
        RecipeIngredient.objects.filter(recipe=obj).all().delete()
        ingredients = validated_data.get('ingredients')
        self.add_ingredients(ingredients, obj)
        obj.save()

        return obj


class RecipeSelectedSerializer(serializers.ModelSerializer):
    """Выбранные рецепты для Подписок и Списка покупок"""

    class Meta:
        model = Recipe
        fields = ('id', 'image', 'name', 'cooking_time',)


class FavoriteSerializer(serializers.ModelSerializer):
    """Избранное"""

    class Meta:
        model = Favorite
        fields = ('__all__')

    def to_representation(self, obj):
        return RecipeSerializer(
            obj.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingSerializer(serializers.ModelSerializer):
    """Покупки"""

    class Meta:
        model = Shopping
        fields = ('__all__')

    def to_representation(self, obj):
        return RecipeSelectedSerializer(
            obj.recipe,
            context={'request': self.context.get('request')}
        ).data
