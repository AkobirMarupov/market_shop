from product.models import Product
from product.api_endpoints.product.serializers import ProductSerializer
from shop_bot.api_endpoints.serializers import PostSerializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class PostCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        serializers = PostSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)

class ProductsGetAPIView(APIView):
    def get(self, request, pk):
        post = Product.objects.filter(pk=pk).first()
        serializers = ProductSerializer(post)
        return Response(serializers.data, status=status.HTTP_200_OK)