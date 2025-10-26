from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet,
    CategoryViewSet,
    CartViewSet,
    CartItemViewSet,
    OrderViewSet,
    ShippingViewSet,
)

# --------------------------------------------------------
# ✅ ROUTER SETUP
# --------------------------------------------------------
router = DefaultRouter()

# 🧭 Register all major endpoints
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cart-item')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'shipping', ShippingViewSet, basename='shipping')

# --------------------------------------------------------
# ✅ FINAL URL PATTERNS
# --------------------------------------------------------
urlpatterns = [
    path('', include(router.urls)),
]
