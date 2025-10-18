from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import localtime
from django.core.mail import send_mail
from django.conf import settings

from .models import User, RoleUpgradeRequest
from cliffindus_backend.products.models import Product, Order


# ==========================================================
# 🧩 INLINE TABLES
# ==========================================================

class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ("name", "price", "created_at")
    readonly_fields = ("name", "price", "created_at")
    can_delete = False
    show_change_link = True


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    fields = ("id", "total_price", "status", "created_at")
    readonly_fields = ("id", "total_price", "status", "created_at")
    can_delete = False
    show_change_link = True


class RoleUpgradeRequestInline(admin.TabularInline):
    model = RoleUpgradeRequest
    extra = 0
    fields = ("requested_role", "status", "created_at")
    readonly_fields = ("requested_role", "status", "created_at")
    can_delete = False
    show_change_link = True


# ==========================================================
# 🧑‍💼 USER ADMIN CONFIGURATION
# ==========================================================

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Customized Django Admin view for the User model."""
    list_display = (
        "username",
        "email",
        "role_colored",
        "verification_badge",
        "total_products",
        "total_orders",
        "last_verified",
        "is_active",
        "last_login",
    )

    list_filter = ("role", "is_verified", "is_active", "verified_at")
    search_fields = ("username", "email")
    ordering = ("id",)
    actions = ["verify_users", "unverify_users"]
    readonly_fields = ("verification_summary", "role_colored")

    # ------------------------------------------------------
    # DYNAMIC INLINES BASED ON ROLE
    # ------------------------------------------------------
    def get_inlines(self, request, obj=None):
        if not obj:
            return []
        if obj.role == "wholesaler":
            return [ProductInline, RoleUpgradeRequestInline]
        elif obj.role in ("retailer", "consumer"):
            return [OrderInline, RoleUpgradeRequestInline]
        else:
            return [RoleUpgradeRequestInline]

    # ------------------------------------------------------
    # ROLE DISPLAY (COLORED)
    # ------------------------------------------------------
    def role_colored(self, obj):
        colors = {
            "admin": "red",
            "wholesaler": "purple",
            "retailer": "blue",
            "consumer": "green",
        }
        color = colors.get(obj.role, "gray")
        return format_html(f"<b style='color:{color};text-transform:capitalize;'>{obj.role}</b>")
    role_colored.short_description = "Role"

    # ------------------------------------------------------
    # VERIFICATION SUMMARY (DETAIL VIEW)
    # ------------------------------------------------------
    def verification_summary(self, obj):
        if not obj.is_verified:
            return format_html("<b style='color:red;'>❌ Unverified</b>")
        admin_name = obj.verified_by.username if obj.verified_by else "Unknown"
        verified_time = (
            localtime(obj.verified_at).strftime("%Y-%m-%d %H:%M %Z")
            if obj.verified_at else "N/A"
        )
        return format_html(
            "<b style='color:green;'>✅ Verified by {}</b><br><small>{}</small>",
            admin_name,
            verified_time,
        )
    verification_summary.short_description = "Verification Details"

    # ------------------------------------------------------
    # VERIFICATION BADGE (LIST VIEW)
    # ------------------------------------------------------
    def verification_badge(self, obj):
        color = "green" if obj.is_verified else "red"
        label = "Verified" if obj.is_verified else "Unverified"
        return format_html(f"<span style='color:{color};font-weight:bold;'>{label}</span>")
    verification_badge.short_description = "Status"

    # ------------------------------------------------------
    # LAST VERIFIED AT COLUMN
    # ------------------------------------------------------
    def last_verified(self, obj):
        """Display last verification timestamp."""
        if not obj.verified_at:
            return format_html("<span style='color:gray;'>—</span>")
        local_time = localtime(obj.verified_at).strftime("%Y-%m-%d %H:%M %Z")
        return format_html(f"<span style='color:teal;'>{local_time}</span>")
    last_verified.short_description = "Last Verified"
    last_verified.admin_order_field = "verified_at"

     # ------------------------------------------------------
    # TOTAL PRODUCTS / ORDERS COUNTS
    # ------------------------------------------------------
    def total_products(self, obj):
        """Count total products owned by wholesalers and retailers."""
        if obj.role not in ("wholesaler", "retailer"):
            return "-"
        return Product.objects.filter(owner=obj).count()
    total_products.short_description = "Products"

    def total_orders(self, obj):
        """Count total orders placed by retailers and consumers."""
        if obj.role not in ("retailer", "consumer"):
            return "-"
        return Order.objects.filter(user=obj).count()
    total_orders.short_description = "Orders"


    # ------------------------------------------------------
    # FIELD LAYOUT (DETAIL VIEW)
    # ------------------------------------------------------
    def get_fieldsets(self, request, obj=None):
        return (
            (None, {
                "fields": (
                    "username",
                    "email",
                    "role_colored",
                    "verification_summary",
                )
            }),
            ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        )

    # ------------------------------------------------------
    # EMAIL NOTIFICATION HELPER
    # ------------------------------------------------------
    def send_verification_email(self, user, verified=True):
        """Send notification email to user on verification change."""
        subject = "Account Verification Update"
        status = "verified ✅" if verified else "unverified ❌"
        message = (
            f"Hello {user.username},\n\n"
            f"Your account has been {status} by an administrator.\n"
            f"— CliffINDUS Team"
        )
        try:
            send_mail(
                subject,
                message,
                getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@cliffindus.com"),
                [user.email],
                fail_silently=True,
            )
        except Exception:
            pass  # ignore email failure in dev mode

    # ------------------------------------------------------
    # ADMIN BULK ACTIONS
    # ------------------------------------------------------
    def verify_users(self, request, queryset):
        for user in queryset:
            user.mark_verified(admin_user=request.user)
            self.send_verification_email(user, verified=True)
        self.message_user(request, f"{queryset.count()} user(s) verified ✅")

    def unverify_users(self, request, queryset):
        for user in queryset:
            user.mark_unverified(admin_user=request.user)
            self.send_verification_email(user, verified=False)
        self.message_user(request, f"{queryset.count()} user(s) unverified ❌")
