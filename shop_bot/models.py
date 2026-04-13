from django.db import models
from common.models import BaseModel
from product.models import Product


class ChatSession(BaseModel):
    chat_id = models.BigIntegerField()
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, null=True, blank=True) # Qo'shildi
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='bot_sessions')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        product_title = self.product.name if self.product else 'Umumiy'
        return f"{self.full_name} (@{self.username or 'N/A'}) | {product_title}"


class ChatMessage(BaseModel):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    is_from_admin = models.BooleanField(default=False)
    text = models.TextField(null=True, blank=True)
    media_file = models.FileField(upload_to='chat_media/', null=True, blank=True)
    file_type = models.CharField(max_length=20, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    telegram_message_id = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{'Admin' if self.is_from_admin else 'User'}: {self.text[:20] if self.text else 'Media'}"


class ProductComment(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bot_comments')
    user_chat_id = models.BigIntegerField()
    full_name = models.CharField(max_length=255)
    text = models.TextField()
    telegram_message_id = models.BigIntegerField()
    reply_text = models.TextField(null=True, blank=True, verbose_name="Admin javobi")
    is_replied = models.BooleanField(default=False, verbose_name="Javob berildimi?")

    def __str__(self):
        return f"{self.full_name} - {self.product.name}"
