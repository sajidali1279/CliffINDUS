from datetime import timedelta
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.utils.timezone import localtime
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.admin import SimpleListFilter
from .admin_dashboard import CliffINDUSAdminSite

from .models import User, RoleUpgradeRequest
from cliffindus_backend.products.models import Product, Order
from cliffindus_backend.users.admin_dashboard import cliffindus_admin_site
from cliffindus_backend.users.models import User


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
# 🧮 CUSTOM FILTER: RECENT VERIFICATION STATUS
# ==========================================================

class RecentVerificationFilter(SimpleListFilter):
    title = "Recent Verification"
    parameter_name = "verified_recently"

    def lookups(self, request, model_admin):
        return [
            ("7days", "Verified in last 7 days"),
            ("30days", "Verified in last 30 days"),
            ("unverified", "Unverified users"),
        ]

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == "7days":
            return queryset.filter(is_verified=True, verified_at__gte=now - timedelta(days=7))
        elif self.value() == "30days":
            return queryset.filter(is_verified=True, verified_at__gte=now - timedelta(days=30))
        elif self.value() == "unverified":
            return queryset.filter(is_verified=False)
        return queryset


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
        "verified_since",
        "total_products",
        "total_orders",
        "last_verified",
        "is_active",
        "last_login",
    )

    list_filter = ("role", "is_verified", "is_active", RecentVerificationFilter)
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
        if not obj.verified_at:
            return format_html("<span style='color:gray;'>—</span>")
        local_time = localtime(obj.verified_at).strftime("%Y-%m-%d %H:%M %Z")
        return format_html(f"<span style='color:teal;'>{local_time}</span>")
    last_verified.short_description = "Last Verified"
    last_verified.admin_order_field = "verified_at"

    # ------------------------------------------------------
    # TIME SINCE VERIFICATION BADGE
    # ------------------------------------------------------
    def verified_since(self, obj):
        """Show how long ago the user was verified."""
        if not obj.is_verified or not obj.verified_at:
            return "-"
        delta = timezone.now() - obj.verified_at
        days = delta.days
        if days < 1:
            return format_html("<span style='color:teal;'>Today</span>")
        elif days == 1:
            return format_html("<span style='color:teal;'>1 day ago</span>")
        elif days < 30:
            return format_html(f"<span style='color:teal;'>{days} days ago</span>")
        else:
            months = days // 30
            return format_html(f"<span style='color:teal;'>{months} month(s) ago</span>")
    verified_since.short_description = "Verified Since"

    # ------------------------------------------------------
    # TOTAL PRODUCTS / ORDERS COUNTS
    # ------------------------------------------------------
    def total_products(self, obj):
        if obj.role not in ("wholesaler", "retailer"):
            return "-"
        return Product.objects.filter(owner=obj).count()
    total_products.short_description = "Products"

    def total_orders(self, obj):
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
            pass

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


try:
    cliffindus_admin_site.unregister(User)
except admin.sites.NotRegistered:
    pass

cliffindus_admin_site.register(User, UserAdmin)