from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from usage.models import UsageLink
from .serializers import UsageLinkSerializer



class UsageLinkListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: UsageLinkSerializer(many=True)}, tags=['UsageLink'])
    def get(self, request):
        links = UsageLink.objects.filter(usage__user=request.user).order_by('-id')
        serializer = UsageLinkSerializer(links, many=True, context={'request': request})
        return Response(serializer.data)


    @swagger_auto_schema(request_body=UsageLinkSerializer, tags=['UsageLink'])
    def post(self, request):
        serializer = UsageLinkSerializer(data=request.data, context={'request': request})
        # Serializer ichidagi Premium mantiqi (1-linkdan keyin pullik) shu yerda ishlaydi
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsageLinkDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: UsageLinkSerializer()}, tags=['UsageLink'])
    def get(self, request, pk):
        link = get_object_or_404(UsageLink, usage__user=request.user, pk=pk)
        serializer = UsageLinkSerializer(link, context={'request': request})
        return Response(serializer.data)


    @swagger_auto_schema(request_body=UsageLinkSerializer, tags=['UsageLink'])
    def put(self, request, pk):
        link = get_object_or_404(UsageLink, usage__user=request.user, pk=pk)
        serializer = UsageLinkSerializer(link, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(tags=['UsageLink'])
    def delete(self, request, pk):
        link = get_object_or_404(UsageLink, usage__user=request.user, pk=pk)
        link.delete()
        return Response({"message": "Link o'chirildi"})