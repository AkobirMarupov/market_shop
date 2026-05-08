from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from asgiref.sync import async_to_sync 
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q

from shop_bot.models import TelegramUser, OrderChat, Message
from shop_bot.bots.utils import send_telegram_message
from .serializer import (
    TelegramUserSerializer, 
    OrderChatSerializer, 
    MessageCreateSerializer
)

class TelegramUserListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = TelegramUser.objects.all().order_by('-id') 
        serializer = TelegramUserSerializer(users, many=True)
        return Response(serializer.data)


class OrderChatListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        status_filter = request.query_params.get('status')
        
        chats = OrderChat.objects.filter(
            Q(owner=request.user) | Q(usage_link__usage__user=request.user)
        ).distinct()

        chats = chats.select_related(
            'customer', 
            'product', 
            'usage_link__usage'
        ).prefetch_related('messages').order_by('-created_at')

        if status_filter:
            chats = chats.filter(status=status_filter)
            
        serializer = OrderChatSerializer(chats, many=True, context={'request': request})
        return Response(serializer.data)

    @swagger_auto_schema(request_body=MessageCreateSerializer)
    def post(self, request):
        serializer = MessageCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            new_message = serializer.save(owner=request.user, sender_type=0)
            chat = new_message.order_chat

            if chat.status == 'new':
                chat.status = 'active'
                chat.save()

            try:
                customer_id = chat.customer.chat_id
                
                if new_message.latitude and new_message.longitude:
                    async_to_sync(send_telegram_message)(chat_id=customer_id,lat=new_message.latitude, lon=new_message.longitude)
                
                elif new_message.image:
                    async_to_sync(send_telegram_message)(chat_id=customer_id, text=new_message.text, file=request.FILES.get('image'), is_image=True)
                
                elif new_message.video:
                    async_to_sync(send_telegram_message)(chat_id=customer_id, text=new_message.text, file=request.FILES.get('video'),is_video=True)

                elif new_message.text:
                    async_to_sync(send_telegram_message)(chat_id=customer_id,text=new_message.text)

            except Exception as e:
                return Response({
                    "warning": f"Xabar saqlandi, lekin bot yubormadi: {str(e)}",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)