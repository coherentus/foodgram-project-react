from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    User model manager для переопределения поля email в качестве логина.
    """
    def create_user(self, email, password, username, **extra_fields):
        """
        Создать и записать объект User c email, username и password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Создать объект User c email, username, password и меткой админа.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if not extra_fields.get('is_staff'):
            raise ValueError(
                'Для суперюзера обязательно is_staff==True.'
            )
        if not extra_fields.get('is_superuser'):
            raise ValueError(
                'Для суперюзера обязательно is_superuser==True.'
            )
        return self.create_user(email, password, **extra_fields)
