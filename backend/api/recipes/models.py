from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from pytils.translit import slugify

from .fields import ColorField

User = get_user_model()


class Ingredient(models.Model):
    """Класс для продуктов."""
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

    def get_absolute_url(self):
        return reverse('ingredients', kwargs={'ingredient_id': self.pk})


class Tag(models.Model):
    """Класс для тэгов."""
    name = models.CharField(
        verbose_name='Название тэга',
        help_text='Введите короткое название тэга',
        max_length=200
    )
    color = ColorField(
        default='#FF0000',
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
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tags', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:50]
        super().save(*args, **kwargs)

    def colortile(self):
        if self.color:
            return format_html(
                '<div style="background-color: {0}; \
                height: 100px; width: 100px"></div>',
                self.color
            )
        return 'пусто'


class Recipe(models.Model):
    """Класс для рецептов."""
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
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
        through='RecipeTag',
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        verbose_name='Продукты',
        related_name='recipes',
        help_text='Выберите продукты из списка',
        through='RecipeIngredient',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        help_text='Введите время приготовления',
        max_length=7,
        validators=[MinValueValidator(1)],
    )
    is_favorited = models.BooleanField(
        verbose_name='Избранный',
        help_text='Добавьте рецепт в Избранное',
        default=False,
    )
    is_in_shopping_cart = models.BooleanField(
        verbose_name='Список покупок',
        help_text='Добавьте рецепт в Список покупок',
        default=False,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return f'{self.name[:15]}, \
            {self.author.last_name} {self.author.first_name}'

    def get_absolute_url(self):
        return reverse('recipes', kwargs={'recipe_id': self.pk})


class RecipeIngredient(models.Model):
    """Множественная связь Рецептов с Ингредиентами."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class RecipeTag(models.Model):
    """Множественная связь Рецептов с Тэгами."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe} {self.tag}'
