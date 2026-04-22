import requests
from io import BytesIO
from PIL import Image
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from shop_bot.models import BotUser, Channel
from django.core.files.base import ContentFile
from rest_framework.permissions import IsAuthenticated
from account.validate_token import get_user_from_request


class BotUserAPIView(APIView):
    def post(self, request):
        user = request.data.get("user")
        user_id = request.data.get("user_id")
        name = request.data.get("name", "")
        username = request.data.get("username", "")
        profile_url = request.data.get("profile_url", None)
        channel_id = request.data.get("channel", "")
        channel = Channel.objects.filter(id=channel_id).first()
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        user, created = BotUser.objects.get_or_create(
            user_id=user_id,
            channel=channel,
            defaults={"name": name, "username": username}
        )
        if created and profile_url:
            try:
                response = requests.get(profile_url)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    buffer = BytesIO()
                    img.save(buffer, format="WEBP", quality=80)
                    file_name = f"{user_id}.webp"
                    user.profile.save(file_name, ContentFile(buffer.getvalue()), save=True)
            except Exception as e:
                print("Profile image save error:", e)
        status_text = "created" if created else "already_exists"
        return Response({"status": status_text, "user_id": user.user_id})

class BotUserDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, pk):
        user_data = get_user_from_request(request)
        if not user_data:
            return Response({"error": "Token noto'g'ri"}, status=status.HTTP_401_UNAUTHORIZED)
        user = user_data['user']
        queryset = BotUser.objects.filter(pk=pk, user=user.id).first()
        if not queryset:
            return Response({"error": "User mavjud emas!"})
        queryset.delete()
        return Response({"message": "User muvoffaqqiyatli o'chirildi"}, status=status.HTTP_204_NO_CONTENT)