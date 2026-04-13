from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
  
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError(_('Telefon raqami kiritilishi shart'))
        
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuserda is_staff=True bo\'lishi shart.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuserda is_superuser=True bo\'lishi shart.'))

        return self.create_user(phone_number, password, **extra_fields)

    def get_by_natural_key(self, phone_number):
        return self.get(phone_number=phone_number)