from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema

from product.models import Product
from .serializers import ProductSerializer

class ProductListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(responses={200: ProductSerializer(many=True)}, tags=['Product'])
    def get(self, request):
        products = Product.objects.filter(owner=request.user).order_by('-id')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
        

    @swagger_auto_schema(request_body=ProductSerializer, tags=['Product'])
    def post(self, request):
        serializer = ProductSerializer(data=request.data, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(responses={200: ProductSerializer()}, tags=['Product'])
    def get(self, request, pk):
        product = get_object_or_404(Product, owner=request.user, pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)


    @swagger_auto_schema(request_body=ProductSerializer, tags=['Product'])
    def put(self, request, pk):
        product = get_object_or_404(Product, owner=request.user, pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(tags=['Product'])
    def delete(self, request, pk):
        product = get_object_or_404(Product, owner=request.user, pk=pk)
        product.delete()
        return Response({"message": "Mahsulot o'chirildi"}, status=status.HTTP_204_NO_CONTENT)