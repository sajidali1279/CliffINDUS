from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, CategoryViewSet,
    CartViewSet, CartItemViewSet, OrderViewSet, ShippingViewSet
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cart-item')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'shipping', ShippingViewSet, basename='shipping')

urlpatterns = router.urls
