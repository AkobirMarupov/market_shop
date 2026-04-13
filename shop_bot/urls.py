from django.urls import path
from shop_bot.api_endpoints.views import *

urlpatterns = [
    path('webhook/', BotWebhookAPIView.as_view(), name='bot_webhook'),
    path('feedback/', FeedbackAPIView.as_view(), name='bot_feedback'),
    path('chats/', AdminChatManagerAPIView.as_view(), name='admin_chat_manager'),
    path('messages/<int:pk>/delete/', ChatMessageDeleteAPIView.as_view(), name='message_delete'),
    path('sessions/<int:pk>/delete/', ChatSessionDeleteAPIView.as_view(), name='session_delete'),
]