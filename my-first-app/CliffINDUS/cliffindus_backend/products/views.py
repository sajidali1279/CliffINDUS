from rest_framework import viewsets, permissions, filters, status, serializers
from rest_framework.response import Response
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend

from cliffindus_backend.products.models import (
    Product, Category, Cart, CartItem, Order, OrderItem, Shipping
)
from cliffindus_backend.products.serializers import (
    ProductSerializer, CategorySerializer,
    CartSerializer, CartItemSerializer,
    OrderSerializer, OrderItemSerializer,
    ShippingSerializer
)
from cliffindus_backend.users.permissions import (
    IsAdmin, IsRetailerOrWholesalerOrReadOnly, IsConsumer, ReadOnly
)
from cliffindus_backend.products.utils import (
    get_visible_products_for,
    get_visible_carts_for,
    get_visible_shipping_for,
    get_visible_orders_for,
)


# ✅ CATEGORY MANAGEMENT (Admin only)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]


# ✅ PRODUCT MANAGEMENT
class ProductViewSet(viewsets.ModelViewSet):
    """
    Handles product CRUD with role-based visibility:
    - Admin: all products
    - Wholesaler: their own products
    - Retailer: verified wholesalers’ products
    - Consumer: verified retailers’ products
    """
    serializer_class = ProductSerializer
    permission_classes = [IsRetailerOrWholesalerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__name', 'price']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

    def get_queryset(self):
        return get_visible_products_for(self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        user = self.request.user
        if not getattr(user, "is_authenticated", False):
            raise serializers.ValidationError({"detail": "Authentication required to create a product."})
        if getattr(user, "role", None) not in ["wholesaler", "admin"]:
            raise serializers.ValidationError({"detail": "Only wholesalers or admins can create products."})
        serializer.save(owner=user)


# ✅ CART VIEW (Consumer only)
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_visible_carts_for(self.request.user).order_by("-id")

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, "role", None) != "consumer":
            raise serializers.ValidationError({"detail": "Only consumers can create carts."})
        serializer.save(user=user)


# ✅ CART ITEM VIEW (Consumer only)
class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)


# ✅ ORDER VIEW
class OrderViewSet(viewsets.ModelViewSet):
    """
    Secure order checkout process with RBAC visibility.
    - Admin: all orders
    - Wholesaler: orders containing their products
    - Retailer: orders from consumers for their products
    - Consumer: their own orders
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_visible_orders_for(self.request.user).order_by('-created_at')

    @transaction.atomic
    def perform_create(self, serializer):
        user = self.request.user

        if getattr(user, "role", None) != "consumer":
            raise serializers.ValidationError({"detail": "Only consumers can place orders."})

        cart, _ = Cart.objects.get_or_create(user=user)
        if not cart.items.exists():
            raise serializers.ValidationError({"detail": "Your cart is empty."})

        total_price = sum(item.product.price * item.quantity for item in cart.items.all())

        order = serializer.save(user=user, total_price=total_price)

        # Copy cart items to order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

        # Empty the cart after checkout
        cart.items.all().delete()
        return order


# ✅ SHIPPING VIEW (Consumer only)
class ShippingViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_visible_shipping_for(self.request.user).order_by("-id")

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, "role", None) != "consumer":
            raise serializers.ValidationError({"detail": "Only consumers can create shipping records."})
        serializer.save()
