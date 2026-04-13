from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth.hashers import make_password
from datetime import timedelta
from django.utils import timezone

from account.models import User
from .serializers import (LoginSerializer, SellerCreateSerializer, CheckPhoneSerializer,
                          VerifyOTPSerializer, NewPasswordSerializer)
from account.utils import send_eskiz_sms


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer, tags=['auth'])
    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')

        user = User.objects.filter(phone_number=phone_number).first()

        if user and user.check_password(password):
            if not user.is_active:
                return Response({'error': 'Sizning hisobingiz faol emas!'})
            
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response = Response({'response': access_token}, status=status.HTTP_200_OK)

            response.set_cookie(
                key='refresh_tokrn',
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=7 * 24 * 60 * 60 
            )
            return response
        
        return Response({'error': 'Telefon yoki parol xato'})
    


class AdminCreateSellerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=SellerCreateSerializer, tags=['users'])
    def post(self, request, *args, **kwargs):
        serializer = SellerCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        phone_number = serializer.validated_data['phone_number']
        password = serializer.validated_data['password']

        user = User.objects.filter(phone_number=phone_number).first()

        if user:
            user.role = 'seller'
            user.set_password(password)
            user.is_active = True
            user.save()
            message = 'Foydalanuvchi sotuvchiga aylantirildi!'
        else:
            user = User.objects.create(
                phone_number=phone_number,
                password=make_password(password),
                role='seller',
                is_active=True,
                is_staff=False 
            )
            message = 'Yangi sotuvchi muvaffaqiyatli yaratildi!'

        return Response({
            "message": message,
            "login": user.phone_number,
            "role": user.role
        }, status=status.HTTP_201_CREATED)
    


class CheckPhoneAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=CheckPhoneSerializer, tags=['auth'])
    def post(self, request):
        serializer = CheckPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        user = User.objects.filter(phone_number=phone_number).first()

        if not user:
            return Response({'error': 'Foydalanuvchi topilmadi!'}, status=status.HTTP_404_NOT_FOUND)
        
        now = timezone.now()

        if user.otp_created_at:
            time_diff = now - user.otp_created_at 

            if user.otp_attempts >= 3 and time_diff < timedelta(hours=2):
                remaining = timedelta(hours=2) - time_diff
                return Response({
                    "error": "Siz ko'p urinish qildingiz va bloklangansiz!",
                    "remaining_time": f"{int(remaining.total_seconds() // 60)} daqiqa"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if time_diff < timedelta(seconds=30):
                remaining = timedelta(seconds=30) - time_diff
                return Response({
                    "error": "Biroz kuting!",
                    "remaining_time": f"{int(remaining.total_seconds())} soniya"
                }, status=status.HTTP_400_BAD_REQUEST)

            if time_diff >= timedelta(hours=2):
                user.otp_attempts = 0

        code = send_eskiz_sms(phone_number)
        if code:
            user.verification_code = code
            user.otp_created_at = now
            user.otp_attempts += 1
            user.save()
            return Response({'message': 'Tasdiqlash kodi yuborildi!'}, status=status.HTTP_200_OK)
        
        return Response({"error": "SMS yuborishda xatolik yuz berdi!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


class VerfyATPAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=VerifyOTPSerializer, tags=['auth'])
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']

        user = User.objects.filter(phone_number=phone_number).first()

        if not user:
            return Response({'erroe': 'Foydalanuvchi topilmadi!'}, status=400)
        
        if str(user.verification_code) != str(code):
            return Response({'error': 'Tasdiqlash kodi noto‘g‘ri!'}, status=400)
        
        if user.otp_created_at and (timezone.now() - user.otp_created_at > timedelta(seconds=120)):
            return Response({"error": "Kodni muddati utgan qaytadan surang!"}, status=400)
        
        user.verification_code = None 
        user.save()


        refresh = RefreshToken.for_user(user)

        response = Response({"message": "KOd tasdiqlandi endi yangi parolni urnating!",
                             "eccess": str(refresh.access_token)}, status=200)
        
        response.set_cookie(
            key='refresh_token', 
            value=str(refresh), 
            httponly=True, 
            secure=True,
            samesite='Lax')
        return response
    

class NewPasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(request_body=NewPasswordSerializer, tags=['auth'])
    def put(self, request):
        serializer = NewPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        user.set_password(serializer.validated_data['new_password'])
        user.verification_code = None
        user.otp_attemts = 0
        user.save()

        return Response({"message": "Parol muffaqiyatli yangilandi!"}, status=status.HTTP_200_OK)
    
    

class RefreshTokenAPIView(APIView):
    permission_classes = [ AllowAny]

    @swagger_auto_schema(tags=['users'])
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({"error": "REfresh token (cookie) topilmadi. Login qiling!"}, status=401)
        
        try:
            refresh  = RefreshToken(refresh_token)
            return Response({
                    "access": str(refresh.access_token),
                    "status": "Success"}, status=200)
        except (TokenError, InvalidToken):
            return Response({"error": "REfresh token muddati tugagan. Qayta login shart!"}, status=401)
        


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['auth'])
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            response = Response({
                "message": "Tizimdan muvaffaqiyatli chiqildi!"
            }, status=status.HTTP_200_OK)

            response.delete_cookie('refresh_token')

            return response
        
        except (TokenError, InvalidToken):
            return Response({"error": "Token xato yoki allaqachon chiqilgan!"}, status=400)