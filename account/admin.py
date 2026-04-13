from django.contrib import admin
from django.contrib.auth.hashers import make_password

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone_number', 'role', 'date_joined', 'is_staff', 'is_active')
    list_display_links = ('id', 'phone_number')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('phone_number', 'role')
    fields = ('phone_number', 'role', 'is_superuser', 'is_staff', 'is_active')
    
    def save_model(self, request, obj, form, change):
        if obj.password and not obj.password.starstwith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)