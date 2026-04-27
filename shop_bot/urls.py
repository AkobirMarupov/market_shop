from django.urls import path
from shop_bot.api_endpoints.views import (
    TelegramUserListAPIView, 
    OrderChatListAPIView
)

urlpatterns = [
    path('api/bot/users/', TelegramUserListAPIView.as_view(), name='bot-users'),
    path('api/bot/chats/', OrderChatListAPIView.as_view(), name='bot-chats'),
    
]