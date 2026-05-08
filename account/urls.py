from django.urls import path
from account.api_endpoints.auth.views import ( LoginAPIView, AdminCreateSellerAPIView, CheckPhoneAPIView,
                                              VerfyATPAPIView, NewPasswordAPIView, RefreshTokenAPIView, LogoutAPIView)



urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('create-login/', AdminCreateSellerAPIView.as_view(), name='admin-create-login'),
    path('send-sms/', CheckPhoneAPIView.as_view(), name='send-sms'),
    path('sms-code/', VerfyATPAPIView.as_view(), name='sms-code'),
    path('new-password/', NewPasswordAPIView.as_view(), name='new-password'),
    path('token-refresh/', RefreshTokenAPIView.as_view(), name='token-refresh'),
    path('logout/', LogoutAPIView.as_view(), name='logout')
    
]