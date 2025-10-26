from cliffindus_backend.users.models import User
from cliffindus_backend.products.models import Product, Order, Cart, Shipping


def get_visible_products_for(user):
    """
    Returns a queryset of products visible to the given user
    based on their role and verification status.
    """
    # ✅ Handle unauthenticated users (AnonymousUser)
    if not getattr(user, "is_authenticated", False):
        return Product.objects.none()

    role = getattr(user, "role", None)

    # ✅ Admin → can see all
    if role == "admin":
        return Product.objects.all()

    # ✅ Wholesaler → see only own products
    if role == "wholesaler":
        return Product.objects.filter(owner=user)

    # ✅ Retailer → see products from verified wholesalers
    if role == "retailer":
        verified_wholesalers = User.objects.filter(role="wholesaler", is_verified=True)
        return Product.objects.filter(owner__in=verified_wholesalers)

    # ✅ Consumer → see products from verified retailers
    if role == "consumer":
        verified_retailers = User.objects.filter(role="retailer", is_verified=True)
        return Product.objects.filter(owner__in=verified_retailers)

    # ✅ Default fallback
    return Product.objects.none()


def get_visible_orders_for(user):
    """
    Returns orders visible to the given user based on their role.
    - Admin: All orders
    - Wholesaler: Orders containing their products
    - Retailer: Orders for their products from consumers
    - Consumer: Their own orders
    """
    if not getattr(user, "is_authenticated", False):
        return Order.objects.none()

    role = getattr(user, "role", None)

    if role == "admin":
        return Order.objects.all()

    if role in ["wholesaler", "retailer"]:
        # Orders that include any product owned by this user
        return Order.objects.filter(items__product__owner=user).distinct()

    if role == "consumer":
        # Only their own orders
        return Order.objects.filter(user=user)

    return Order.objects.none()


def get_visible_carts_for(user):
    """
    Returns carts visible to a user.
    """
    if not getattr(user, "is_authenticated", False):
        return Cart.objects.none()

    role = getattr(user, "role", None)

    if role == "admin":
        return Cart.objects.all()
    if role == "consumer":
        return Cart.objects.filter(user=user)
    return Cart.objects.none()


def get_visible_shipping_for(user):
    """
    Returns shipping records visible to a user.
    """
    if not getattr(user, "is_authenticated", False):
        return Shipping.objects.none()

    role = getattr(user, "role", None)

    if role == "admin":
        return Shipping.objects.all()
    if role == "consumer":
        return Shipping.objects.filter(order__user=user)
    return Shipping.objects.none()
