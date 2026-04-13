from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from usage.models import Usage
from .serializers import UsageSerializer



class UsageListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: UsageSerializer(many=True)}, tags=['Usage'])
    def get(self, request):
        usages = Usage.objects.filter(user=request.user).order_by('-id')
        serializer = UsageSerializer(usages, many=True, context={'request': request})
        return Response(serializer.data)


    @swagger_auto_schema(request_body=UsageSerializer, tags=['Usage'])
    def post(self, request):
        serializer = UsageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsageDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: UsageSerializer()}, tags=['Usage'])
    def get(self, request, pk):
        usage = get_object_or_404(Usage, user=request.user, pk=pk)
        serializer = UsageSerializer(usage, context={'request': request})
        return Response(serializer.data)


    @swagger_auto_schema(request_body=UsageSerializer, tags=['Usage'])
    def put(self, request, pk):
        usage = get_object_or_404(Usage, user=request.user, pk=pk)
        serializer = UsageSerializer(usage, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(tags=['Usage'])
    def delete(self, request, pk):
        usage = get_object_or_404(Usage, user=request.user, pk=pk)
        usage.delete()
        return Response({"message": "Guruh o'chirildi"})