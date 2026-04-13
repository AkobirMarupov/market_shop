from django.urls import path
from product.api_endpoints.product.views import ProductListCreateAPIView, ProductDetailAPIView
from product.api_endpoints.categoriy.views import CategoryAPIView, CategoryDetailAPIView


urlpatterns = [
    path('categories/', CategoryAPIView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='category-detail'),
    path('products/', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
]