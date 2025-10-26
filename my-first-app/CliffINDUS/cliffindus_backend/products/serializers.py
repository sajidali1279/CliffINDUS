from rest_framework import serializers
from .models import Product, Category, Cart, CartItem, Order, OrderItem, Shipping


# --------------------------------------------------------
# ✅ CATEGORY SERIALIZER
# --------------------------------------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


# --------------------------------------------------------
# ✅ PRODUCT SERIALIZER (role-aware)
# --------------------------------------------------------
class ProductSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    owner_role = serializers.CharField(source="owner.role", read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = [
            "id", "owner", "owner_role", "name", "description",
            "price", "category", "category_id", "stock",
            "is_active", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "owner", "owner_role", "created_at", "updated_at"]

    def to_representation(self, instance):
        """Limit sensitive fields based on user role."""
        data = super().to_representation(instance)
        user = self.context.get("request").user if self.context.get("request") else None

        # Hide inactive products for consumers or anonymous users
        if not getattr(user, "is_authenticated", False) or getattr(user, "role", None) == "consumer":
            if not instance.is_active:
                return None
        return data


# --------------------------------------------------------
# ✅ CART ITEM SERIALIZER
# --------------------------------------------------------
class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "product_price", "quantity", "subtotal"]

    def get_subtotal(self, obj):
        return obj.subtotal


# --------------------------------------------------------
# ✅ CART SERIALIZER (nested)
# --------------------------------------------------------
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(source="total_items", read_only=True)
    total_price = serializers.DecimalField(source="total_price", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_items", "total_price", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]


# --------------------------------------------------------
# ✅ ORDER ITEM SERIALIZER
# --------------------------------------------------------
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price"]


# --------------------------------------------------------
# ✅ ORDER SERIALIZER (nested items)
# --------------------------------------------------------
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "total_price", "status", "items", "created_at"]
        read_only_fields = ["id", "user", "total_price", "created_at"]


# --------------------------------------------------------
# ✅ SHIPPING SERIALIZER
# --------------------------------------------------------
class ShippingSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source="order.id", read_only=True)
    is_shipped = serializers.BooleanField(source="is_shipped", read_only=True)
    is_delivered = serializers.BooleanField(source="is_delivered", read_only=True)

    class Meta:
        model = Shipping
        fields = [
            "id", "order_id", "address", "city", "state", "postal_code",
            "tracking_number", "shipped_date", "delivery_date",
            "is_shipped", "is_delivered"
        ]
