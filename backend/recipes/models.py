from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.html import format_html
from pytils.translit import slugify

from .fields import ColorField

User = get_user_model()


class Tag(models.Model):
    """Тэги."""
    name = models.CharField(
        verbose_name='Название тэга',
        help_text='Введите короткое название тэга',
        max_length=200
    )
    color = ColorField(
        verbose_name='Цветовой HEX-код',
        help_text='Укажите цвет тэга',
    )
    slug = models.SlugField(
        verbose_name='Адрес тэга',
        unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['id']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:50]
        super().save(*args, **kwargs)

    def colortile(self):
        if self.color:
            return format_html(
                '<div style="background-color: {0}; \
                height: 32px; width: 32px"></div>',
                self.color
            )
        return 'пусто'


class Ingredient(models.Model):
    """Продукты."""
    name = models.CharField(
        verbose_name='Название продукта',
        help_text='Введите короткое название продукта',
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепты."""
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        help_text='Введите короткое название рецепта',
        max_length=200
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Опишите Ваш рецепт'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        help_text='Загрузите изображение',
        upload_to='recipes/'
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Тэги',
        related_name='recipes',
        help_text='Выберите тэги из списка',
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        verbose_name='Продукты',
        related_name='recipes',
        help_text='Выберите продукты из списка',
        through='RecipeIngredient',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        help_text='Введите время приготовления',
        default=1,
        validators=[MinValueValidator(1, message='Минимальное значение - 1')],
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return f'{self.name[:15]}, {self.author.username[:15]}'


class RecipeIngredient(models.Model):
    """Множественная связь Рецептов с Ингредиентами."""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепты',
        related_name='recipe_ingredients',
        on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='ingredient_recipes',
        on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        default=1,
        validators=[MinValueValidator(1, message='Минимальное значение - 1')],
    )

    class Meta:
        verbose_name = 'Продукты для Рецепта'
        verbose_name_plural = 'Продукты для Рецептов'
        ordering = ['ingredient__name']

    def __str__(self):
        return f'{self.ingredient.name} {self.amount} {self.recipe.name}'


class RecipeTag(models.Model):
    """Множественная связь Рецептов с Тэгами."""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепты',
        related_name='recipe_tags',
        on_delete=models.CASCADE)
    tag = models.ForeignKey(
        Tag,
        verbose_name='Тэги',
        related_name='tag_recipes',
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тэги для Рецепта'
        verbose_name_plural = 'Тэги для Рецептов'
        ordering = ['ingredient__name']

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class Favorite(models.Model):
    """Избранные рецепты."""
    owner = models.ForeignKey(
        User,
        verbose_name='Хозяин',
        related_name='favorite_owners',
        default=1,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранный рецепт',
        related_name='favorites',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ['owner', 'recipe']
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'recipe'],
                name='unique_owner_recipe_favorite'
            )
        ]

    def __str__(self):
        return f'Избранное {self.owner.username}'


class Shopping(models.Model):
    """Список покупок."""
    owner = models.ForeignKey(
        User,
        verbose_name='Хозяин',
        related_name='shopping_owners',
        default=1,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Покупка',
        related_name='shoppings',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Покупку'
        verbose_name_plural = 'Покупки'
        ordering = ['owner', 'recipe']
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'recipe'],
                name='unique_owner_recipe_shopping'
            )
        ]

    def __str__(self):
        return f'Покупки {self.owner.username}'
