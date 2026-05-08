from django.db import models
from django.contrib.auth import get_user_model
from product.models import Product
from common.models import BaseModel
from usage.models import UsageLink
import os
import datetime
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile


User = get_user_model()

class TelegramUser(BaseModel):
    chat_id = models.BigIntegerField(unique=True)
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    
    def __str__(self):
        return self.full_name


class OrderChat(BaseModel):
 
    STATUS_CHOICES = [
        ('new', 'Yangi'),
        ('active', 'Jarayonda'),
        ('completed', 'Yakunlangan'),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_chats', null=True, blank=True)
    usage_link = models.ForeignKey(UsageLink, on_delete=models.SET_NULL, null=True, blank=True) # Qaysi linkdan keldi?
    customer = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    

    def __str__(self):
        return f"Chat {self.id}: {self.customer.full_name} - {self.product.name if self.product else 'Noma`lum'}"


class Message(BaseModel):
    SENDER_CHOICES = [
        (0, 'Admin'),
        (1, 'Xaridor'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    order_chat = models.ForeignKey('OrderChat', on_delete=models.CASCADE, related_name='messages')
    sender_type = models.IntegerField(choices=SENDER_CHOICES)
    text = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='messages/images/', null=True, blank=True)
    video = models.FileField(upload_to='messages/videos/', null=True, blank=True)
    file = models.FileField(upload_to='messages/files/', null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    telegram_message_id = models.BigIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Xabar"
        verbose_name_plural = "Xabarlar"

    def __str__(self):
        sender = self.get_sender_type_display()
        return f"Msg {self.id} | {sender} | Chat: {self.order_chat.id}"

    def save(self, *args, **kwargs):
        if self.image and hasattr(self.image, 'file'):
            try:
                if not self.image.name.lower().endswith('.webp'):
                    img = Image.open(self.image)
                    
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGBA")
                    else:
                        img = img.convert("RGB")
                    
                    output = BytesIO()
                    img.save(output, format='WEBP', quality=80)
                    output.seek(0)
                    
                    current_name = os.path.basename(self.image.name)
                    base_name = os.path.splitext(current_name)[0]
                    
                    self.image.save(
                        f"{base_name}.webp", 
                        ContentFile(output.read()), 
                        save=False
                    )
            except Exception as e:
                print(f"Rasm konvertatsiyasida xato: {e}")

        if self.video and not self.video.name:
            now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            self.video.name = f"video_{now}.mp4"
            
        if self.file and not self.file.name:
            now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            self.file.name = f"file_{now}"

        super().save(*args, **kwargs)