from rest_framework import serializers
from shop_bot.models import TelegramNotification

class NotificationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='full_name')
    notification_list = serializers.SerializerMethodField(method_name='get_notification_list')

    class Meta:
        model = TelegramNotification
        fields = ['id', 'status', 'message', 'name', 'chat_id', 'created_at', 'notification_list']

    def get_notification_list(self, obj):
        return {
            "image": obj.product.image.url if obj.product and obj.product.image else None
        }