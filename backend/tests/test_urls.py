from http import HTTPStatus

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from logic.models import Bascket, FavourRecipe, Follow
from recipes.models import Component, Product, Recipe, Tag
from users.models import CustomUser as User


class UrlAbsPathTests(TestCase):
    """Проверка доступности URL.

    /api/tags/                      guest
    /api/tags/{id}/                 guest

    /api/ingredients/               guest
    /api/ingredients/{id}/          guest

    /api/recipes/                   guest
    /api/recipes/{id}/              guest
    /api/download_shopping_cart/    auth-user
    /api/{id}/shopping_cart/        auth-user
    /api/recipes/{id}/favorite/     auth-user

    /api/users/                     guest
    /api/users/{id}/                auth-user
    /api/users/me/                  auth-user
    /api/users/set_password/        auth-user
    /api/users/subscriptions/       auth-user
    /api/users/{id}/subscribe/      auth-user

    /api/auth/token/login/          guest
    /api/auth/token/logout/         auth-user

    Методика тестов:
    - перебор GET запросов по абсолютному пути.
    Клиент гостевой. Ответ не 404.
    """
    def setUp(self):
        self.author = User.objects.create(
            username='Name', email='email@test.fake', password='123qwaszx')
        self.tag = Tag.objects.create(
            name='Casper', color='3', slug='Bull Dog')
        self.product = Product.objects.create(
            name='Muffin', measurement_unit='г')
        
        self.recipe = Recipe.objects.create(
            author=self.author,     
            cooking_time=2,
            title='Test recipe',
            text='test description'
        )
        self.recipe.tags.add(self.tag)
        self.component = Component.objects.create(
            product=self.product, amount=20, recipe=self.recipe)

        self.recipe.save()
        self.component.save()

        

    def test_get_404_status_with_undefined_url(self):
        resp = self.client.get('not_defined_url_test_404')
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)

    def test_get_abs_urls_without_404(self):
        """Проверка абсолютных путей гостевым клиентом."""
        id = 1

        url_table = (

            '/api/tags/',
            f'/api/tags/{id}/',
            '/api/ingredients/',
            f'/api/ingredients/{id}/',

            '/api/recipes/',
            f'/api/recipes/{id}/',


            '/api/users/',
            f'/api/users/{id}/',
            '/api/users/me/',
            '/api/users/set_password/',
            '/api/users/subscriptions/',
            f'/api/users/{id}/subscribe/',

            '/api/auth/token/login/',
            '/api/auth/token/logout/',


            f'/api/recipes/{id}/favorite/',
            '/api/recipes/download_shopping_cart/',
            f'/api/recipes/{id}/shopping_cart/',
            '/admin/'
        )

        for abs_url in url_table:
            with self.subTest(abs_url=abs_url):
                resp = self.client.get(abs_url)
                self.assertNotEqual(resp.status_code, HTTPStatus.NOT_FOUND)
