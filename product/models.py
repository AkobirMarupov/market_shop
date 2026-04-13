
from django.db import models
import os
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from usage.utils import send_product_to_telegram
from django.utils.translation import gettext_lazy as _

from common.models import BaseModel
from account.models import User

class Category(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories', verbose_name="Do'kon egasi")
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name="Ota kategoriya")
    slug = models.SlugField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{slugify(self.name)}-{self.owner.id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.owner} | {self.name}"

    class Meta:
        unique_together = ('owner', 'name')
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"


class Product(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', verbose_name="Mahsulot egasi")
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    telegram_message_id = models.BigIntegerField(null=True, blank=True, verbose_name="Telegram Post ID")
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None 
        
        if self.image:
            self.convert_to_webp()
            
        super().save(*args, **kwargs)

        if is_new or not self.telegram_message_id:
            self.share_to_telegram_channels()

    def share_to_telegram_channels(self):
        from usage.models import LinkConnect, UsageLink
        
        connections = LinkConnect.objects.filter(category=self.category)
        
        for conn in connections:
            links = UsageLink.objects.filter(usage=conn.usage, is_active=True)
            
            for l in links:
                chat_id = "@" + l.link.strip('/').split('/')[-1]
                
                msg_id = send_product_to_telegram(chat_id, self, l.link)
                
                if msg_id:
                    self.telegram_message_id = msg_id
                    super(Product, self).save(update_fields=['telegram_message_id'])