from django.contrib import admin
from django.utils.html import format_html
from cliffindus_backend.users.admin_dashboard import cliffindus_admin_site
from cliffindus_backend.products.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price")


class OrderAdmin(admin.ModelAdmin):
    """
    Admin view for Orders — includes seller verification and product owner info.
    """
    list_display = (
        "id",
        "user",
        "seller_name",
        "seller_verification_status",
        "total_price",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email", "id")
    inlines = [OrderItemInline]

    def seller_name(self, obj):
        """Displays the first product's seller (owner)."""
        first_item = obj.items.first()
        if first_item and first_item.product.owner:
            seller = first_item.product.owner
            color_map = {
                "wholesaler": "purple",
                "retailer": "blue",
                "consumer": "green",
                "admin": "red",
            }
            color = color_map.get(seller.role, "gray")
            return format_html(
                f"<b style='color:{color};text-transform:capitalize;'>{seller.username} ({seller.role})</b>"
            )
        return format_html("<span style='color:gray;'>—</span>")
    seller_name.short_description = "Seller"

    def seller_verification_status(self, obj):
        """Shows whether the seller (product owner) is verified."""
        first_item = obj.items.first()
        if not first_item or not first_item.product.owner:
            return format_html("<span style='color:gray;'>No Seller</span>")

        seller = first_item.product.owner
        if seller.is_verified:
            verified_by = seller.verified_by.username if seller.verified_by else "Unknown"
            verified_date = (
                seller.verified_at.strftime("%Y-%m-%d %H:%M")
                if seller.verified_at else "N/A"
            )
            return format_html(
                f"<span style='color:green;'>✅ Verified</span><br>"
                f"<small>by {verified_by} on {verified_date}</small>"
            )
        return format_html("<span style='color:red;'>❌ Unverified</span>")
    seller_verification_status.short_description = "Seller Verification"


# ✅ Ensure it doesn't crash even if already registered
try:
    cliffindus_admin_site.unregister(Order)
except admin.sites.NotRegistered:
    pass

cliffindus_admin_site.register(Order, OrderAdmin)
