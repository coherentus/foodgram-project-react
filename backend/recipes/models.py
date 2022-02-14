from django.conf import settings
from django.contrib import admin
from django.core.validators import MinValueValidator
from django.db import models

from pytils.translit import slugify

User = settings.AUTH_USER_MODEL

MIN_AMOUNT_VALUE = 1
MIN_AMOUNT_MESSAGE = 'Количество ингредиента не может быть меньше единицы'
MIN_COOKING_VALUE = 1
MIN_COOKING_MESSAGE = ('Время приготовления не может быть меньше '
                       'одной минуты')


class Tag(models.Model):
    """Тег.

    Поля:
    name - Название.
    color - Цветовой HEX-код.
    slug
    Related_names:
    'recipes'   from recipes.Recipe
    """
    name = models.CharField(
        unique=True,
        max_length=20,
        verbose_name='Название тега'
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет тега'
    )
    slug = models.SlugField(
        unique=True,
        blank=True, null=True,
        verbose_name='Транслит тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name[:20]}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:20]
        return super().save(*args, **kwargs)


class Product(models.Model):
    """Пищевой продукт.

    Совместно с единицей измерения составляет компонент рецепта.
    Поля:
    name - Название.
    measure_unit - Единица измерения.
    Related_names:
    'components'    from recipes.Component
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Название продукта'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        constraints = (
            # пара полей не должна повторяться
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_product'
            ),
        )
        verbose_name = 'Пищевой продукт'
        verbose_name_plural = 'Пищевые продукты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} - ({self.measurement_unit})'


class Component(models.Model):
    """Компонент рецепта.

    Продукт в количестве, необходимом для рецепта.
    Поля:
    product - id продукта
    recipe - к какому рецепту относится
    amount - количество
    Related_names:
    'recipes'   from recipes.Recipe m2m trough to recipes.Product
    """
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='components',
        verbose_name='Продукт для рецепта'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='recipe_components',
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество продукта',
        default=1,
        validators=(
            MinValueValidator(
                MIN_AMOUNT_VALUE, message=MIN_AMOUNT_MESSAGE
            ),
        )
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return (f'{self.product.name} - {self.amount} '
                f'({self.product.measurement_unit})')


class Recipe(models.Model):
    """Рецепт. Камень преткновения проекта.

    Поля:
    author - Автор публикации.
    title - Название блюда.
    picture - Картинка.
    text - Описание процесса приготовления.
    components - Ингредиенты, выбор из существующих + ед. измерения и кол-во.
    tag - Тег, один или несколько.
    cooking_time - Время на приготовление в минутах.
    pub_date - Дата публикации.
    Related_names:
    'basket_recipes'        from logic.Basket
    'favourite'             from logic.FavourRecipe
    'recipe_ingredients'    from recipes.Component
    """
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes', verbose_name='Автор рецепта'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    picture = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка готового блюда'
    )
    text = models.TextField(
        max_length=3000,
        verbose_name='Описание процесса приготовления'
    )
    components = models.ManyToManyField(
        Product,
        through='Component',
        related_name='recipes',
        verbose_name='Набор ингредиентов',
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='recipes',
        verbose_name='Теги рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        validators=(
            MinValueValidator(
                MIN_COOKING_VALUE, message=MIN_COOKING_MESSAGE
            ),
        ),
        verbose_name='Время на приготовление в минутах'
    )
    pub_date = pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.title[:20]}, {self.author.username}'

    @property  # type: ignore
    @admin.display(
        description='Добавлен в избранное раз',
    )
    def in_favor_count(self):
        """Вернуть сколько раз рецепт добавлен в избранное пользователями.

        relation from logic:FavourRecipes.recipes m2m
        """
        return self.favourite.count()
