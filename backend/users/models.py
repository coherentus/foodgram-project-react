from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Кастомная модель пользователя.

    В качестве логина используется поле email.
    Сортировка по умолчанию - по id.
    Related_names:
    'bascket'           from logic.Bascket
    'follower'          from logic.Follow
    'following'         from logic.Follow
    'favour_recipes'    from logic.FavourRecipe
    """
    email = models.EmailField(
        unique=True,
        db_index=True,
        max_length=124,
        verbose_name='Email-адрес пользователя'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        verbose_name='Никнейм пользователя'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия пользователя'
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль пользователя'
    )
    date_joined = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации'
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Админ'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Аккаунт разрешён'
    )

    USERNAME_FIELD = 'email'

    # список обязательных полей для команды createsuperuser
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}'

    @property  # type: ignore
    @admin.display(
        description='Подписан на',
    )
    def follows(self):
        """Вернуть количество подписок пользователя.

        relation from logic:Follow.user one2many
        """
        return self.follower.count()

    @property
    def is_not_active(self):
        return (not self.is_active)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    # related name для модели CustomUser 'auth_token'
    if created:
        Token.objects.create(user=instance)
