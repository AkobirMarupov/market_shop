from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from product.models import Category
from .serializers import CategorySerializer


class CategoryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(responses={200: CategorySerializer(many=True)}, tags=['Category'])
    def get(self, request):
        categories = Category.objects.filter(owner=request.user, parent__isnull=True).order_by('-id')
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)


    @swagger_auto_schema(request_body=CategorySerializer, tags=['Category'])
    def post(self, request):
        serializer = CategorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoryDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: CategorySerializer()}, tags=['Category'])
    def get(self, request, pk):
        category = get_object_or_404(Category, owner=request.user, pk=pk)
        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data)


    @swagger_auto_schema(request_body=CategorySerializer, tags=['Category'])
    def put(self, request, pk):
        category = get_object_or_404(Category, owner=request.user, pk=pk)
        serializer = CategorySerializer(category, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


    @swagger_auto_schema(tags=['Category'])
    def delete(self, request, pk):
        category = get_object_or_404(Category, owner=request.user, pk=pk)
        category.delete()
        return Response({"message": "O'chirildi"})