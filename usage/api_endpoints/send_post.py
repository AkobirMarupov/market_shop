import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema

from usage.models import Category, LinkConnect, UsageLink
from product.models import Product
from usage.utils import send_product_to_telegram, get_handle_from_link
from .serializers import TelegramSyncSerializer


class SyncMultipleCategoriesToTelegramAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Kategoriyalarni tegishli kanallarga saralab yuborish",
        request_body=TelegramSyncSerializer,
        tags=['Telegram-Bot']
    )
    def post(self, request):
        serializer = TelegramSyncSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        category_ids = serializer.validated_data.get('category_ids', [])
        results = []
        total_sent_overall = 0

        for cat_id in category_ids:
            category_obj = Category.objects.filter(id=cat_id, owner=request.user).first()
            if not category_obj:
                results.append({"id": cat_id, "status": "Kategoriya topilmadi"})
                continue

            connections = LinkConnect.objects.filter(category=category_obj, usage__user=request.user)
            
            if not connections.exists():
                results.append({"category": category_obj.name, "status": "Ushbu kategoriya hech qanday kanalga ulanmagan"})
                continue

            products = Product.objects.filter(category=category_obj)
            cat_sent_count = 0
            
            for conn in connections:
                active_links = UsageLink.objects.filter(
                    usage=conn.usage, 
                    is_active=True
                )
                
                for link_obj in active_links:
                    chat_handle = get_handle_from_link(link_obj.link)
                    
                    for product in products:
                        success = send_product_to_telegram(
                            chat_id=chat_handle, 
                            product=product, 
                            channel_link=link_obj.link
                        )
                        if success:
                            cat_sent_count += 1
                        
                        time.sleep(0.3)

            results.append({
                "category": category_obj.name,
                "products_count": products.count(),
                "messages_sent": cat_sent_count
            })
            total_sent_overall += cat_sent_count

        return Response({
            "status": "completed",
            "total_sent_overall": total_sent_overall,
            "details": results
        }, status=status.HTTP_200_OK)