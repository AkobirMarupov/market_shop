from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from usage.models import LinkConnect
from .serializers import LinkConnectSerializer



class LinkConnectListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: LinkConnectSerializer(many=True)}, tags=['LinkConnect'])
    def get(self, request):
        connects = LinkConnect.objects.filter(usage__user=request.user).order_by('-id')
        serializer = LinkConnectSerializer(connects, many=True, context={'request': request})
        return Response(serializer.data)


    @swagger_auto_schema(request_body=LinkConnectSerializer, tags=['LinkConnect'])
    def post(self, request):
        serializer = LinkConnectSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LinkConnectDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: LinkConnectSerializer()}, tags=['LinkConnect'])
    def get(self, request, pk):
        connect = get_object_or_404(LinkConnect, usage__user=request.user, pk=pk)
        serializer = LinkConnectSerializer(connect, context={'request': request})
        return Response(serializer.data)


    @swagger_auto_schema(tags=['LinkConnect'])
    def delete(self, request, pk):
        connect = get_object_or_404(LinkConnect, usage__user=request.user, pk=pk)
        connect.delete()
        return Response({"message": "Bog'lanish o'chirildi"})