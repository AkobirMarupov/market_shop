from rest_framework import serializers
from shop_bot.models import TelegramUser, OrderChat, Message
from django.shortcuts import get_object_or_404


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ['id', 'chat_id', 'full_name', 'username', 'phone_number', 'created_at']


class MessageDetailSerializer(serializers.ModelSerializer):
    video = serializers.FileField(read_only=True)
    class Meta:
        model = Message
        fields = [
            'id', 
            'text', 
            'sender_type', 
            'image', 
            'video', 
            'file', 
            'latitude', 
            'longitude',
            'created_at'
        ]


class OrderChatSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='customer.full_name', read_only=True)
    username = serializers.CharField(source='customer.username', read_only=True)
    chat_id = serializers.IntegerField(source='customer.chat_id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    usage_title = serializers.CharField(source='usage_link.usage.title', read_only=True)
    source_link = serializers.URLField(source='usage_link.link', read_only=True)
    replay = MessageDetailSerializer(source='messages', many=True, read_only=True)

    class Meta:
        model = OrderChat
        fields = [
            'id', 'status', 'usage_title', 'source_link',
            'name', 'username', 'chat_id', 'product_name', 
            'created_at', 'replay'
        ]


class MessageCreateSerializer(serializers.ModelSerializer):
    chat_id = serializers.IntegerField(write_only=True)
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Message
        fields = ['chat_id', 'text', 'image', 'video', 'file', 'latitude', 'longitude', 'sender_type']

    def create(self, validated_data):
        chat_id = validated_data.pop('chat_id')
        order_chat = get_object_or_404(OrderChat, id=chat_id)
        return Message.objects.create(order_chat=order_chat, **validated_data)