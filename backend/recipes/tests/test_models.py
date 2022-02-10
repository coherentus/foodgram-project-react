from django.test import TestCase

from recipes.models import Component, Tag, Product, Recipe
from users.models import CustomUser as User

TAG_TITLE = 'Очень длинное название тега для проверки'
PRODUCT_NAME = 'Картофель'
MEASURE_UNIT = 'Штука'
AMOUNT = 30
RECIPE_TITLE = 'Очень длинное название рецепта для проверки'
RECIPE_AUTHOR = 'Поварёшкин'


class ModelsStrTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(
            username=RECIPE_AUTHOR,
            email='ssdr@io.oi',
            password='qwerty654321'
        )

        cls.tag = Tag.objects.create(
            name=TAG_TITLE,
            color='#123456'
        )
        cls.product = Product.objects.create(
            name=PRODUCT_NAME,
            measurement_unit=MEASURE_UNIT
        )        

        cls.recipe = Recipe.objects.create(
            title=RECIPE_TITLE,
            author=cls.test_user,
            text='Тестовое описание.',            
        )
        cls.component = Component.objects.create(
            product=cls.product,
            amount=AMOUNT,
            recipe = cls.recipe
        )
        cls.recipe.tags.add(cls.tag)

        cls.test_model_response = (
            (cls.tag, TAG_TITLE[:20]),
            (cls.product, f'{PRODUCT_NAME} - ({MEASURE_UNIT})'),
            (cls.component, f'{PRODUCT_NAME} - {AMOUNT} ({MEASURE_UNIT})'),
            (cls.recipe, f'{RECIPE_TITLE[:20]}, {RECIPE_AUTHOR}'),
        )

    def test_models_str_return(self):
        """Проверка, что методы __str__ моделей работают корректно."""
        for model_name, str_value in ModelsStrTests.test_model_response:
            with self.subTest(model_name=model_name):
                self.assertEqual(str(model_name), str_value)
