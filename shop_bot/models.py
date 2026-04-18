from django.db import models
from product.models import Product

class TelegramNotification(models.Model):
    STATUS_CHOICES = [
        ('yangi', 'yangi'),
        ('oqildi', 'oʻqildi'),
        ('yakunlandi', 'yakunlandi'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bot_notifications')
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, null=True, blank=True)
    chat_id = models.BigIntegerField()
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='yangi')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bot Xabarnomasi"
        verbose_name_plural = "Bot Xabarnomalari"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.product.name if self.product else 'No Product'}"