from django.contrib import admin
from .models import BotUser, Message, Product, Channel

admin.site.register(BotUser)
admin.site.register(Product)
admin.site.register(Channel)
admin.site.register(Message)