from django.urls import path
from shop_bot.api_endpoints.admin_message_views import *
from shop_bot.api_endpoints.bot_user_views import *
from shop_bot.api_endpoints.message_views import *
from shop_bot.api_endpoints.post_views import *



urlpatterns = [
    # path('bot/bot_users/', BotUserAPIView.as_view(), name="bot-user"),
    path('bot/message/', MessageAPIView.as_view(), name="message"),
    # path('bot/posts/', PostCreateAPIView.as_view()),
    # path('bot/products/<int:pk>/', ProductsGetAPIView.as_view()),
    # path('bot/channels/', ChannelCreateAPIView.as_view()),
    path('notifications', ChannelGetAPIView.as_view()),
    path('notifications/<int:pk>', BotUserDeleteAPIView.as_view(), name='notifications_delete'),
    path('notifications/reply', AdminMessageAPIView.as_view()),
]

