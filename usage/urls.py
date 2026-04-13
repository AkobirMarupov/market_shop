from django.urls import path
from usage.api_endpoints.usage import UsageListCreateAPIView, UsageDetailAPIView
from usage.api_endpoints.link import UsageLinkListCreateAPIView, UsageLinkDetailAPIView
from usage.api_endpoints.usage_category import LinkConnectListCreateAPIView, LinkConnectDetailAPIView
from usage.api_endpoints.send_post import SyncMultipleCategoriesToTelegramAPIView


urlpatterns = [
    # Usage
    path('usages/', UsageListCreateAPIView.as_view()),
    path('usages/<int:pk>/', UsageDetailAPIView.as_view()),

    # UsageLink
    path('usage-links/', UsageLinkListCreateAPIView.as_view()),
    path('usage-links/<int:pk>/', UsageLinkDetailAPIView.as_view()),

    # LinkConnect
    path('link-connects/', LinkConnectListCreateAPIView.as_view()),
    path('link-connects/<int:pk>/', LinkConnectDetailAPIView.as_view()),

    path('send-to-telegram/', SyncMultipleCategoriesToTelegramAPIView.as_view(), name='send-to-telegram'),
]
