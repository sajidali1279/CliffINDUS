from rest_framework import serializers
from .models import Product, Category
from .models import Cart, CartItem, Order, OrderItem, Shipping


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = [
            'id', 'owner', 'name', 'description', 'price',
            'category', 'category_id', 'stock',
            'created_at', 'updated_at'
        ]
class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'subtotal']

    def get_subtotal(self, obj):
        return obj.subtotal


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_total(self, obj):
        return sum(item.subtotal for item in obj.items.all())


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'created_at']
        read_only_fields = ['id', 'user', 'total_price', 'created_at']


class ShippingSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id', read_only=True)

    class Meta:
        model = Shipping
        fields = ['id', 'order_id', 'address', 'city', 'state', 'postal_code',
                  'tracking_number', 'shipped_date', 'delivery_date']