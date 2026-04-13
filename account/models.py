from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from common.models import BaseModel
from account.manager import UserManager


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        SELLER = 'seller', _('Sotuvchi')
        CUSTOMER = 'customer', _('Xaridor')

    phone_number = models.CharField(max_length=15, unique=True)
    verification_code = models.BigIntegerField(unique=True, null=True, blank=True)
    role = models.CharField(max_length=15, choices=Role.choices, default=Role.CUSTOMER)
    date_joined = models.DateTimeField(auto_now_add=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    otp_attempts = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number' 
    REQUIRED_FIELDS = [] 

    class Meta:
        db_table = 'user'
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.phone_number} ({self.get_role_display()})"
