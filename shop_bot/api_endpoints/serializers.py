from rest_framework import serializers
from shop_bot.models import ChatSession, ChatMessage
from product.models import Product


class ProductShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image']

class ChatMessageSerializer(serializers.ModelSerializer):
    body = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'body', 'image', 'file', 'status', 'created_at']

    def get_status(self, obj):
        return "1" if obj.is_from_admin else "2"

    def get_body(self, obj):
        if obj.file_type == 'location' and obj.latitude:
            return f"? Lokatsiya: http://google.com/maps?q={obj.latitude},{obj.longitude}"
        return obj.text or ""

    def _get_absolute_url(self, obj):
        if obj.media_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.media_file.url)
            return obj.media_file.url
        return None

    def get_image(self, obj):
        # Faqat rasm bo'lsa link qaytaradi
        if obj.file_type == 'photo' and obj.media_file:
            return self._get_absolute_url(obj)
        return None

    def get_file(self, obj):
        # Rasm bo'lmagan boshqa barcha medialar uchun
        if obj.file_type in ['video', 'file', 'document', 'sticker'] and obj.media_file:
            return self._get_absolute_url(obj)
        return None


class UserChatHistorySerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ['id', 'is_active', 'messages', 'updated_at']

class AdminReplySerializer(serializers.Serializer):
    session_id = serializers.IntegerField(required=True)
    text = serializers.CharField(required=False, allow_blank=True)
    media_file = serializers.FileField(required=False, allow_null=True)