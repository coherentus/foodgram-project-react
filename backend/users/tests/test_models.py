from django.test import TestCase

from ..models import CustomUser as User


class ModelsStrTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(
            username='Toster',
            email='supr@mail.io',
            password='123'
        )

    def test_models_str_return(self):
        """Проверка, что метод __str__ модели работает корректно."""
        self.assertEqual(str(ModelsStrTests.test_user), 'Toster')
