from django.contrib import admin
from django.db import models

from recipes.models import Recipe
from users.models import CustomUser as User


class Bascket(models.Model):
    """Корзина пользователя.

    Поля:
    user - Пользователь.
    recipes - Рецепты в корзине.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='bascket',
        verbose_name='Корзина покупок'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='bascket_recipes',
        verbose_name='Рецепты в списке покупок'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Список рецептов для покупки'
        verbose_name_plural = 'Списки рецептов для покупки'

    def __str__(self):
        return (f'{self.user.username}, '
                f'в корзине рецептов: {self.recipes_count}')

    @property  # type: ignore
    @admin.display(
        description='Рецептов к покупке',
    )
    def recipes_count(self):
        """Вернуть количество рецептов в списке покупок пользователя."""
        return self.user.bascket.count()


class Follow(models.Model):
    """Подписки пользователя.

    Поля:
    user - Пользователь.
    author - На кого подписан.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower', verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following', verbose_name='Автор рецепта'
    )

    class Meta:
        constraints = (
            # пара полей не должна повторяться
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            ),
            # поля не могут ссылаться на один и тот же объект
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='not_yourself_follow'
            ),
        )
        ordering = ('author',)
        verbose_name = 'Подписка пользователя'
        verbose_name_plural = 'Подписки пользователей'

    def __str__(self):
        return (f'Подписчик {self.user.username[:15]}'
                f' на автора {self.author.username[:15]}')

    # имена столбцов для админки logic
    @property  # type: ignore
    @admin.display(
        description='Имеет подписчиков',
    )
    def folower_count(self):
        """Сколько имеет подписчиков"""
        return self.user.following.count()

    @property  # type: ignore
    @admin.display(
        description='Подписан на',
    )
    def folowing_count(self):
        """На скольких пользователей подписан"""
        return self.user.follower.count()


class FavourRecipe(models.Model):
    """Список избранных рецептов пользователя.

    Поля:
    user - Пользователь.
    recipe - Избранный рецепт.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favour_recipes',
        verbose_name='Автор избранного'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favourite',
        verbose_name='Избранные рецепты'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Список избранных рецептов'
        verbose_name_plural = 'Списки избранных рецептов'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_user_recipe',
            ),
        )

    def __str__(self):
        return (f'{self.user.username}, '
                f'в избранном рецептов: {self.recipes_count}')

    @property  # type: ignore
    @admin.display(
        description='Рецептов в избранном',
    )
    def recipes_count(self):
        """Вернуть количество рецептов в избранном пользователя."""
        return self.user.favour_recipes.count()
