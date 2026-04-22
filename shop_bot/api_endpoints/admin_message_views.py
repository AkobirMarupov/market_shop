import requests
import os
from rest_framework.permissions import IsAuthenticated
from account.validate_token import get_user_from_request
from shop_bot.api_endpoints.serializers import AdminMessageSerializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")

class AdminMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user_data = get_user_from_request(request)
        if not user_data:
            return Response(
                {"error": "Token noto'g'ri"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = AdminMessageSerializers(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        admin_message = serializer.save()
        user = admin_message.user
        chat_id = user.user_id
        message = admin_message.message
        image = admin_message.image
        file = admin_message.file
        latitude = admin_message.latitude
        longitude = admin_message.longitude
        if message:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                data={
                    "chat_id": chat_id,
                    "text": message
                }
            )
        if image:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto",
                data={
                    "chat_id": chat_id,
                    "caption": message or ""
                },
                files={
                    "photo": image
                }
            )
        if file:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument",
                data={
                    "chat_id": chat_id,
                    "caption": message or ""
                },
                files={
                    "document": file
                }
            )
        if latitude and longitude:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendLocation",
                data={
                    "chat_id": chat_id,
                    "latitude": latitude,
                    "longitude": longitude
                }
            )
        return Response({
            "status": True,
            "message": "Xabar yuborildi",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)