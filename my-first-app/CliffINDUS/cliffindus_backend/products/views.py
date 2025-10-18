from rest_framework import viewsets, permissions, filters, status, serializers
from rest_framework.response import Response
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, Category, Cart, CartItem, Order, OrderItem, Shipping
from .serializers import (
    ProductSerializer, CategorySerializer,
    CartSerializer, CartItemSerializer,
    OrderSerializer, OrderItemSerializer,
    ShippingSerializer
)
from cliffindus_backend.users.permissions import (
    IsAdmin,
    IsRetailerOrWholesalerOrReadOnly,
    IsConsumer,
    ReadOnly
)



# ✅ CATEGORY MANAGEMENT (Admin only)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin]


# ✅ PRODUCT MANAGEMENT
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [IsRetailerOrWholesalerOrReadOnly | IsAdmin | ReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__name', 'price']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# ✅ CART VIEW (Consumer only)
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsConsumer]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ✅ CART ITEM VIEW (Consumer only)
class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsConsumer]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)


# ✅ ORDER VIEW (Consumer only, verified checkout logic)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [IsConsumer]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=user).order_by('-created_at')

    @transaction.atomic
    def perform_create(self, serializer):
        user = self.request.user
        cart, created = Cart.objects.get_or_create(user=user)

        if not cart.items.exists():
            raise serializers.ValidationError({"detail": "Your cart is empty."})

        total_price = sum(item.product.price * item.quantity for item in cart.items.all())

        order = serializer.save(user=user, total_price=total_price)

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart.items.all().delete()
        return order


# ✅ SHIPPING VIEW (Consumer only)
class ShippingViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingSerializer
    permission_classes = [IsConsumer]

    def get_queryset(self):
        return Shipping.objects.filter(order__user=self.request.user)
