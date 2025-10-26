from django.db import models
from django.conf import settings
from django.utils import timezone


# --------------------------------------------------------
# ✅ CATEGORY MODEL
# --------------------------------------------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# --------------------------------------------------------
# ✅ PRODUCT MODEL
# --------------------------------------------------------
class Product(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category or 'No Category'})"

    @property
    def owner_role(self):
        return getattr(self.owner, "role", None)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Product"
        verbose_name_plural = "Products"


# --------------------------------------------------------
# ✅ CART MODEL
# --------------------------------------------------------
class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_items(self):
        return self.items.count()

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())


# --------------------------------------------------------
# ✅ CART ITEM MODEL
# --------------------------------------------------------
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity


# --------------------------------------------------------
# ✅ ORDER MODEL
# --------------------------------------------------------
class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order #{self.id} ({self.status})"

    class Meta:
        ordering = ["-created_at"]


# --------------------------------------------------------
# ✅ ORDER ITEM MODEL
# --------------------------------------------------------
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} × {self.product.name} (Order {self.order.id})"


# --------------------------------------------------------
# ✅ SHIPPING MODEL
# --------------------------------------------------------
class Shipping(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="shipping")
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    shipped_date = models.DateTimeField(blank=True, null=True)
    delivery_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Shipping for Order {self.order.id}"

    @property
    def is_delivered(self):
        return self.delivery_date is not None

    @property
    def is_shipped(self):
        return self.shipped_date is not None
