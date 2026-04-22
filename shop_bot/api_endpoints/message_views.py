from shop_bot.api_endpoints.serializers import MessageSerializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from account.validate_token import get_user_from_request
from rest_framework.permissions import IsAuthenticated

from .serializers import ChannelSerializers
from shop_bot.models import Channel



class MessageAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializers = MessageSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)
    


class ChannelCreateAPIView(APIView):
    def post(self, request):
        name = request.data.get("name")
        user_id = request.data.get("user")
        channel, created = Channel.objects.get_or_create(name=name, defaults={"user": user_id})
        return Response({"id": channel.id, "created": created}, status=status.HTTP_201_CREATED)

class ChannelGetAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user_data = get_user_from_request(request)
        if not user_data:
            return Response({"error": "Token noto'g'ri"}, status=status.HTTP_401_UNAUTHORIZED)
        user = user_data['user']
        queryset = Channel.objects.filter(user=user.id)
        serializers = ChannelSerializers(queryset, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)