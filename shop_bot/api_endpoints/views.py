import os
import requests
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_yasg.utils import swagger_auto_schema

from config import settings
from product.models import Product
from shop_bot.models import ChatSession, ChatMessage, ProductComment
from .serializers import *

BOT_TOKEN = settings.BOT_TOKEN


class AdminChatManagerAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    @swagger_auto_schema(
        tags=['Admin Chat'],
        responses={200: UserChatHistorySerializer(many=True)}
    )
    def get(self, request):
        sessions = ChatSession.objects.filter(
            is_active=True
        ).prefetch_related('messages').order_by('-updated_at')
        
        serializer = UserChatHistorySerializer(sessions, many=True, context={'request': request})
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=AdminReplySerializer, tags=['Admin Chat'])
    def post(self, request):
        serializer = AdminReplySerializer(data=request.data)
        if serializer.is_valid():
            session = get_object_or_404(ChatSession, id=serializer.validated_data['session_id'])
            text = serializer.validated_data.get('text', '')
            media = request.FILES.get('media_file')

            f_type = "text"
            if media:
                if media.content_type.startswith('image/'): f_type = "photo"
                elif media.content_type.startswith('video/'): f_type = "video"
                else: f_type = "file"

            msg = ChatMessage.objects.create(
                session=session, 
                text=text, 
                media_file=media, 
                file_type=f_type, 
                is_from_admin=True
            )

            # 2. Telegramga yuborish
            self.send_to_tg(session.chat_id, msg)
            
            return Response(ChatMessageSerializer(msg, context={'request': request}).data, status=201)
        return Response(serializer.errors, status=400)

    def send_to_tg(self, chat_id, msg):
        url_base = f"https://api.telegram.org/bot{BOT_TOKEN}"
        if msg.file_type == "photo":
            requests.post(f"{url_base}/sendPhoto", data={'chat_id': chat_id, 'caption': msg.text}, files={'photo': msg.media_file.open()})
        elif msg.file_type == "video":
            requests.post(f"{url_base}/sendVideo", data={'chat_id': chat_id, 'caption': msg.text}, files={'video': msg.media_file.open()})
        elif msg.file_type == "file":
            requests.post(f"{url_base}/sendDocument", data={'chat_id': chat_id, 'caption': msg.text}, files={'document': msg.media_file.open()})
        else:
            requests.post(f"{url_base}/sendMessage", data={'chat_id': chat_id, 'text': msg.text, 'parse_mode': 'HTML'})



class BotWebhookAPIView(APIView):
    def post(self, request):
        msg = request.data.get("message") or request.data.get("edited_message")
        if not msg: 
            return Response(status=200)

        chat_id = msg['chat']['id']
        
        text = msg.get("text") or msg.get("caption") or ""
        

        if text.startswith("/start"):
            parts = text.split()
            if len(parts) > 1 and parts.isdigit():
                p_id = int(parts)
                product = get_object_or_404(Product, id=p_id)
                ChatSession.objects.filter(chat_id=chat_id, is_active=True).update(is_active=False)
                ChatSession.objects.create(
                    chat_id=chat_id, 
                    full_name=f"{msg['from'].get('first_name','')} {msg['from'].get('last_name','')}".strip(), 
                    product=product
                )
                
                welcome = f"? <b>{product.name}</b>\n? Narxi: {product.price} so'm\n\nSavolingizni yozishingiz mumkin."
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": chat_id, "text": welcome, "parse_mode": "HTML"})
                return Response(status=200)

        session = ChatSession.objects.filter(chat_id=chat_id, is_active=True).last()
        if session:
            f_id, f_type, lat, lon = None, None, None, None

            if "photo" in msg:
                f_id = msg["photo"][-1]["file_id"]
                f_type = "photo"
            elif "video" in msg:
                f_id = msg["video"]["file_id"]
                f_type = "video"
            elif "document" in msg:
                f_id = msg["document"]["file_id"]
                f_type = "file"
            elif "location" in msg:
                lat = msg["location"]["latitude"]
                lon = msg["location"]["longitude"]
                f_type = "location"
            else:
                f_type = "text"

            media = self.download_file(f_id) if f_id else None
            
            ChatMessage.objects.create(
                session=session,
                text=text,           # Rasm ostidagi matn yoki oddiy matn
                media_file=media,    # Yuklab olingan fayl
                file_type=f_type,    # 'photo', 'video', 'file', 'text'
                latitude=lat,
                longitude=lon,
                is_from_admin=False
            )
            
        return Response(status=200)

    def download_file(self, f_id):
        try:
            res = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={f_id}").json()
            if res.get("ok"):
                f_path = res["result"]["file_path"]
                content = requests.get(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{f_path}").content
                return ContentFile(content, name=os.path.basename(f_path))
        except Exception as e:
            print(f"Fayl yuklashda xato: {e}")
            return None
        

    
class ChatMessageDeleteAPIView(APIView):

    @swagger_auto_schema(tags=['Admin Chat'])
    def delete(self, request, pk):

        message = get_object_or_404(ChatMessage, pk=pk)
        
        if message.media_file:
            if os.path.isfile(message.media_file.path):
                os.remove(message.media_file.path)
        
        message.delete()
        return Response(
            {"detail": "Xabar muvaffaqiyatli o'chirildi."}, 
            status=status.HTTP_204_NO_CONTENT
        )

class ChatSessionDeleteAPIView(APIView):

    @swagger_auto_schema(tags=['Admin Chat'])
    def delete(self, request, pk):
        session = get_object_or_404(ChatSession, pk=pk)

        session.delete()
        return Response(
            {"detail": "Chat sessiyasi va barcha xabarlar o'chirildi."}, 
            status=status.HTTP_204_NO_CONTENT
        )


class FeedbackAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user_id = request.data.get('user_id')
        body = request.data.get('body', '')
        post_id = request.data.get('post')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        file_obj = request.FILES.get('file') or request.FILES.get('image')

        if not user_id or not post_id:
            return Response(
                {"detail": "user_id va post maydonlari majburiy."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            chat_id = int(user_id)
        except (TypeError, ValueError):
            return Response(
                {"detail": "user_id noto'g'ri formatda."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product = get_object_or_404(Product, pk=post_id)

        session, _ = ChatSession.objects.get_or_create(
            chat_id=chat_id,
            product=product,
            defaults={'full_name': self.get_full_name(chat_id)}
        )

        file_type = self.get_file_type(file_obj, latitude, longitude, body)

        ChatMessage.objects.create(
            session=session,
            text=body or None,
            media_file=file_obj if file_obj else None,
            file_type=file_type,
            latitude=latitude or None,
            longitude=longitude or None,
            is_from_admin=False,
        )

        if body:
            ProductComment.objects.create(
                product=product,
                user_chat_id=chat_id,
                full_name=session.full_name,
                text=body,
                telegram_message_id=0,
            )

        return Response({"detail": "Feedback muvaffaqiyatli qabul qilindi."}, status=status.HTTP_201_CREATED)

    def get_full_name(self, chat_id):
        User = get_user_model()
        user = User.objects.filter(telegram_id=chat_id).first()
        if user:
            return user.phone_number
        return f"Telegram foydalanuvchi {chat_id}"

    def get_file_type(self, file_obj, latitude, longitude, body):
        if file_obj:
            content_type = file_obj.content_type or ""
            if content_type.startswith('image/'):
                return 'photo'
            if content_type.startswith('video/'):
                return 'video'
            return 'file'

        if latitude or longitude:
            return 'location'

        if body:
            return 'text'

        return None