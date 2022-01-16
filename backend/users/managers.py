from django.contrib.auth.models import UserManager


class CreateSuperUserManager(UserManager):

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError(
                'Главный админ должен иметь статус is_staff=True.'
            )
        if not extra_fields.get('is_superuser'):
            raise ValueError(
                'Главный админ должен иметь статус is_superuser=True.'
            )

        return self._create_user(username, email, password, **extra_fields)
