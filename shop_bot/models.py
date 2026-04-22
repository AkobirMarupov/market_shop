from django.db import models
from PIL import Image
from io import BytesIO
from account.models import User
from django.core.files.base import ContentFile
from common.models import BaseModel


STATUS = [
    ("1", "New"),
    ("2", "Answered"),
]

class Channel(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    user = models.IntegerField()

    class Meta:
        db_table = 'channel'
        verbose_name = 'Channel'
        verbose_name_plural = 'Channels'

    def __str__(self):
        return self.name


class BotUser(BaseModel):
    user = models.IntegerField(null=True, blank=True)
    user_id = models.CharField(max_length=120)
    name = models.CharField(max_length=120, null=True, blank=True)
    username = models.CharField(max_length=120, null=True, blank=True)
    profile = models.ImageField(upload_to='botusers/', null=True, blank=True)
    channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, null=True, blank=True, related_name='bot_users')


    def save(self, *args, **kwargs):
        if self.profile:
            try:
                img = Image.open(self.profile)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                buffer = BytesIO()
                img.save(buffer, format="WEBP", quality=80)
                file_name = self.profile.name.split('.')[0] + ".webp"
                self.profile.save(file_name, ContentFile(buffer.getvalue()), save=False)
            except Exception as e:
                print("Image convert error:", e)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or self.username or str(self.user_id)


class Product(BaseModel):
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE, related_name='posts')
    post_user = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=120, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="UZS")
    image = models.ImageField(upload_to='posts/')


    def save(self, *args, **kwargs):
        if self.image:
            try:
                img = Image.open(self.image)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                buffer = BytesIO()
                img.save(buffer, format="WEBP", quality=80)
                file_name = self.image.name.split('.')[0] + ".webp"
                self.image.save(file_name, ContentFile(buffer.getvalue()), save=False)
            except Exception as e:
                print("Post image convert error:", e)

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'post'
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return self.title

class Message(BaseModel):
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE, related_name='messages')
    post = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='feedbacks/', null=True, blank=True)
    file = models.FileField(upload_to='feedbacks/', null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="1")


    def save(self, *args, **kwargs):
        if self.image:
            try:
                img = Image.open(self.image)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                buffer = BytesIO()
                img.save(buffer, format="WEBP", quality=80)
                file_name = self.image.name.split('.')[0] + ".webp"
                self.image.save(file_name, ContentFile(buffer.getvalue()), save=False)
            except Exception as e:
                print("Post image convert error:", e)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.message[:20] if self.message else 'No text'}"

class AdminMessage(BaseModel):
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_messages')
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE, related_name='admin_messages')
    message_id = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='admin_messages')
    message = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='admin_messages/', null=True, blank=True)
    file = models.FileField(upload_to='admin_messages/', null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="1")


    def save(self, *args, **kwargs):
        if self.image:
            try:
                img = Image.open(self.image)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                buffer = BytesIO()
                img.save(buffer, format="WEBP", quality=80)
                file_name = self.image.name.split('.')[0] + ".webp"
                self.image.save(file_name, ContentFile(buffer.getvalue()), save=False)
            except Exception as e:
                print("Post image convert error:", e)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.message[:20] if self.message else 'No text'}"