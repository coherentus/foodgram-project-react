from django.test import TestCase

from logic.models import Bascket, FavourRecipe, Follow
from recipes.models import Recipe
from users.models import CustomUser as User


class ModelsStrTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create(
            username='Toster',
            email='tost@tst.tt'
        )
        cls.user_follower = User.objects.create(
            username='Follow_Toster',
            email='follow@tst.tt'
        )

        cls.recipe = Recipe.objects.create(
            title='test_recipe',
            author=cls.user_author
        )

        cls.bascket = Bascket.objects.create(
            user=cls.user_follower,
            recipe=cls.recipe
        )

        cls.favor_recipe = FavourRecipe.objects.create(
            user=cls.user_follower,
            recipe=cls.recipe
        )

        cls.follow = Follow.objects.create(
            user=cls.user_author,
            author=cls.user_follower
        )

        cls.test_model_response = (
            # Bascket
            (
                cls.bascket,
                (f'{cls.user_follower.username}, в корзине рецептов: '
                 f'{cls.bascket.recipes_count}')
            ),
            # Favourite
            (
                cls.favor_recipe,
                (f'{cls.user_follower.username}, в избранном рецептов: '
                 f'{cls.favor_recipe.recipes_count}')
            ),
            # Follow
            (
                cls.follow,
                (f'Подписчик {cls.user_author.username[:15]} '
                 f'на автора {cls.user_follower.username[:15]}')
            ),
        )

    def test_models_str_return(self):
        """Проверка, что методы __str__ моделей работают корректно."""
        for model_name, str_value in ModelsStrTests.test_model_response:
            with self.subTest(model_name=model_name):
                self.assertEqual(str(model_name), str_value)
