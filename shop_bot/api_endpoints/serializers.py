from shop_bot.models import BotUser, Message, Product, Channel, AdminMessage
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.utils import timezone
from account.models import User
from django.shortcuts import get_object_or_404

class BotUserSerializers(ModelSerializer):
    class Meta:
        model = BotUser
        fields = ['id', 'name', 'username', 'user_id', 'profile', 'channel']

    def create(self, validated_data):
        user, created = BotUser.objects.get_or_create(
            user_id=validated_data["user_id"],
            defaults={
                "name": validated_data.get("name"),
                "username": validated_data.get("username", "")
            }
        )
        return user

class MessageSerializers(ModelSerializer):
    user_id = serializers.CharField(write_only=True)
    channel = serializers.CharField(write_only=True)
    post = serializers.CharField(write_only=True)

    class Meta:
        model = Message
        fields = ['user_id', 'channel','post', 'message', 'image', 'file', 'latitude', 'longitude', 'created_at']

    def get_created_at(self, obj):
        return timezone.localtime(obj.created_at)

    def create(self, validated_data):
        user_id = validated_data.pop("user_id")
        channel = validated_data.pop("channel")
        user = BotUser.objects.get(user_id=user_id, channel=channel)
        post_id = validated_data.pop("post")
        post = Product.objects.get(id=post_id)
        message = Message.objects.create(user=user, post=post, **validated_data)
        return message

class AdminMessageGetSerializers(serializers.ModelSerializer):
    class Meta:
        model = AdminMessage
        fields = ['id', 'message_id', 'message', 'image', 'file', 'latitude', 'longitude', 'created_at']
        read_only_fields = ['id', 'created_at']

class FeedBackGetSerializers(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'message', 'image', 'file', 'latitude', 'longitude', 'status','created_at']

    def validate_file(self, value):
        ext = value.name.split('.')[-1].lower()
        if ext not in ['webp', 'pdf']:
            raise serializers.ValidationError("Faqat webp yoki pdf mumkin!")
        return value

class PostSerializers(ModelSerializer):
    user_id = serializers.CharField(write_only=True)
    channel = serializers.CharField(write_only=True)
    class Meta:
        model = Product
        fields = ['id', 'user_id', 'channel', 'post_user', 'image', 'title', 'description', 'amount', 'currency']

    def create(self, validated_data):
        user_id = validated_data.pop("user_id")
        channel = validated_data.pop("channel")
        user = BotUser.objects.get(user_id=user_id, channel=channel)
        post = Product.objects.create(user=user, **validated_data)
        return post

class PostGetSerializers(ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'image']

class BotUsersFeedbacks(serializers.ModelSerializer):
    messages = FeedBackGetSerializers(many=True, read_only=True)
    messages_count = serializers.SerializerMethodField()
    posts = PostGetSerializers(many=True, read_only=True)
    posts_count = serializers.SerializerMethodField()
    admin_messages = AdminMessageGetSerializers(many=True, read_only=True)
    admin_messages_count = serializers.SerializerMethodField()
    class Meta:
        model = BotUser
        fields = ['id', 'name', 'username', 'user_id', 'profile', 'posts_count', 'posts',
                  'messages_count', 'messages', 'admin_messages_count','admin_messages']

    def get_messages_count(self, obj):
        return obj.messages.count()

    def get_posts_count(self, obj):
        return obj.posts.count()

    def get_admin_messages_count(self, obj):
        return obj.admin_messages.count()

class ChannelSerializers(serializers.ModelSerializer):
    bot_users = BotUsersFeedbacks(many=True, read_only=True)
    bot_users_count = serializers.SerializerMethodField()
    class Meta:
        model = Channel
        fields = ['id', 'name', 'user', 'bot_users_count', 'bot_users']

    def get_bot_users_count(self, obj):
        return obj.bot_users.count()

class AdminMessageSerializers(serializers.ModelSerializer):
    user_id = serializers.CharField(write_only=True)
    message_id = serializers.IntegerField(write_only=True)
    channel = serializers.CharField(write_only=True)

    class Meta:
        model = AdminMessage
        fields = ['id', 'user_id', 'message_id', 'channel', 'message', 'image', 'file', 'latitude', 'longitude',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')

        user_id = validated_data.pop('user_id')
        message_id = validated_data.pop('message_id')
        channel = validated_data.pop('channel')
        message_text = validated_data.pop('message', None)
        admin = request.user
        user = get_object_or_404(BotUser, user_id=user_id, channel=channel)
        message_id = get_object_or_404(Message, id=message_id)

        return AdminMessage.objects.create(
            admin=admin,
            user=user,
            message_id=message_id,
            message=message_text,
            **validated_data
        )