from rest_framework.generics import ListAPIView
from shop_bot.models import TelegramNotification
from .serializers import NotificationSerializer

class NotificationListView(ListAPIView):
    queryset = TelegramNotification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer