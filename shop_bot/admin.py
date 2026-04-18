from django.contrib import admin
from .models import TelegramNotification

@admin.register(TelegramNotification)
class TelegramNotificationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'product', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'message', 'product__name')
    # Faqat o'qish uchun (o'zgartirib bo'lmasligi uchun)
    readonly_fields = ('full_name', 'chat_id', 'message', 'product', 'created_at')


    # admin.py ichida agar bo'lsa:
def product_title(self, obj):
    return obj.product.name  # Bu yerda ham .name bo'lishi kerak