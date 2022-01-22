from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from .models import Subscribe
from recipes.models import Recipe

User = get_user_model()


class ProfileCreateSerializer(UserCreateSerializer):
    """Создание пользователя"""

    email = serializers.EmailField(
        max_length=150,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )


class Meta:
    model = User
    fields = (
        'email',
        'username',
        'first_name',
        'last_name',
        'password',
    )


class ProfileSerializer(UserSerializer):
    """Получение списка пользователей/ пользователя"""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        read_only_fields = [f.name for f in User._meta.get_fields()]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=request.user, author=obj).exists()


class RecipeSubscribeSerializer(serializers.ModelSerializer):
    """Рецепты для Подписок"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscribeSerializer(serializers.ModelSerializer):
    """Подписка пользователя"""

    class Meta:
        model = Subscribe
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого автора.'
            )
        ]

    def to_representation(self, obj):
        return SubscribeListSerializer(
            obj.author,
            context={'request': self.context.get('request')}
        ).data


class SubscribeListSerializer(serializers.ModelSerializer):
    """Список подписок пользователя"""

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return 0
        return 1 if Subscribe.objects.filter(
            user=request.user, author=obj).exists() else 0

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        return RecipeSubscribeSerializer(
            recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
