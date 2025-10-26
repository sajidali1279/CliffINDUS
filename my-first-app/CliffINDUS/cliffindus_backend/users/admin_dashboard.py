# ✅ cliffindus_backend/users/admin_dashboard.py
from django.contrib import admin, messages
from django.urls import path
from django.template.response import TemplateResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.utils.html import format_html

# --- Models ---
from cliffindus_backend.users.models import User, RoleUpgradeRequest
from cliffindus_backend.products.models import Product, Order, Category


# --------------------------------------------------------
# ✅ 1. Custom AdminSite
# --------------------------------------------------------
class CliffINDUSAdminSite(admin.AdminSite):
    site_header = "CliffINDUS Administration"
    site_title = "CliffINDUS Admin Portal"
    index_title = "📊 CliffINDUS Dashboard"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("", self.admin_view(self.dashboard_view), name="dashboard"),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        """Renders analytics dashboard + stats."""
        now = timezone.now()
        range_param = request.GET.get("range", "30")
        start_param = request.GET.get("start")
        end_param = request.GET.get("end")

        try:
            range_days = int(range_param)
        except ValueError:
            range_days = 30

        if start_param and end_param:
            try:
                start_date = timezone.datetime.fromisoformat(start_param)
                end_date = timezone.datetime.fromisoformat(end_param)
            except ValueError:
                start_date = now - timedelta(days=range_days)
                end_date = now
        else:
            start_date = now - timedelta(days=range_days)
            end_date = now

        # --- Stats ---
        total_users = User.objects.count()
        verified_users = User.objects.filter(is_verified=True).count()
        wholesalers = User.objects.filter(role="wholesaler").count()
        retailers = User.objects.filter(role="retailer").count()
        consumers = User.objects.filter(role="consumer").count()
        total_orders = Order.objects.count()
        total_products = Product.objects.count()
        pending_upgrades = RoleUpgradeRequest.objects.filter(status="pending").count()

        users_in_range = User.objects.filter(date_joined__range=[start_date, end_date])
        orders_in_range = Order.objects.filter(created_at__range=[start_date, end_date])
        products_in_range = Product.objects.filter(created_at__range=[start_date, end_date])

        new_users = users_in_range.count()
        new_orders = orders_in_range.count()
        new_products = products_in_range.count()

        def growth_rate(current, new):
            if current == 0:
                return 0
            return round((new / current) * 100, 1)

        user_growth = growth_rate(total_users, new_users)
        order_growth = growth_rate(total_orders, new_orders)
        product_growth = growth_rate(total_products, new_products)

        # --- Chart Data ---
        daily_user_data = (
            users_in_range.extra(select={"day": "date(date_joined)"})
            .values("day").order_by("day").annotate(count=Count("id"))
        )
        daily_order_data = (
            orders_in_range.extra(select={"day": "date(created_at)"})
            .values("day").order_by("day").annotate(count=Count("id"))
        )

        user_labels = [str(d["day"]) for d in daily_user_data]
        user_values = [d["count"] for d in daily_user_data]
        order_values = [d["count"] for d in daily_order_data]

        # --- Category Chart ---
        category_data = (
            Category.objects.annotate(total=Count("products"))
            .values("name", "total").order_by("-total")[:5]
        )
        category_labels = [c["name"] for c in category_data]
        category_values = [c["total"] for c in category_data]
        category_colors = [
            "rgba(255,99,132,0.8)",
            "rgba(54,162,235,0.8)",
            "rgba(255,206,86,0.8)",
            "rgba(75,192,192,0.8)",
            "rgba(153,102,255,0.8)",
        ][:len(category_labels)]

        context = dict(
            self.each_context(request),
            title=f"Dashboard – Last {range_days} days",
            stats={
                "total_users": total_users,
                "verified_users": verified_users,
                "wholesalers": wholesalers,
                "retailers": retailers,
                "consumers": consumers,
                "total_orders": total_orders,
                "total_products": total_products,
                "pending_upgrades": pending_upgrades,
                "user_growth": user_growth,
                "order_growth": order_growth,
                "product_growth": product_growth,
                "user_labels": user_labels,
                "user_values": user_values,
                "order_values": order_values,
                "category_labels": category_labels,
                "category_values": category_values,
                "category_colors": category_colors,
                "selected_range": range_days,
                "start_date": start_date,
                "end_date": end_date,
            },
            quick_links=[
                {"name": "Users", "url": "/admin/users/user/"},
                {"name": "Products", "url": "/admin/products/product/"},
                {"name": "Orders", "url": "/admin/products/order/"},
                {"name": "Role Upgrade Requests", "url": "/admin/users/roleupgraderequest/"},
                {"name": "Categories", "url": "/admin/products/category/"},
            ],
        )
        return TemplateResponse(request, "admin/dashboard.html", context)


# --------------------------------------------------------
# ✅ Instantiate our site BEFORE registrations
# --------------------------------------------------------
cliffindus_admin_site = CliffINDUSAdminSite(name="cliffindus_admin")


# --------------------------------------------------------
# ✅ 2. Role Upgrade Request Admin
# --------------------------------------------------------
class RoleUpgradeRequestAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "requested_role",
        "business_name",
        "status_badge",
        "created_at",
        "updated_at",
        "approve_button",
        "reject_button",
    )
    list_filter = ("status", "requested_role", "created_at")
    search_fields = ("user__username", "business_name")

    def status_badge(self, obj):
        color = {"pending": "orange", "approved": "green", "rejected": "red"}.get(obj.status, "gray")
        return format_html(f"<b><span style='color:{color}'>{obj.status.upper()}</span></b>")

    def approve_button(self, obj):
        if obj.status == "pending":
            return format_html(f'<a class="button" href="/admin/users/roleupgraderequest/{obj.id}/approve/">✅ Approve</a>')
        return "—"

    def reject_button(self, obj):
        if obj.status == "pending":
            return format_html(f'<a class="button" href="/admin/users/roleupgraderequest/{obj.id}/reject/">❌ Reject</a>')
        return "—"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("<int:pk>/approve/", self.admin_site.admin_view(self.approve_request), name="approve_request"),
            path("<int:pk>/reject/", self.admin_site.admin_view(self.reject_request), name="reject_request"),
        ]
        return custom_urls + urls

    def approve_request(self, request, pk):
        obj = RoleUpgradeRequest.objects.get(pk=pk)
        obj.approve(admin_user=request.user, comment="Approved via Admin Panel")
        self.message_user(request, f"✅ {obj.user.username} promoted to {obj.requested_role}.", messages.SUCCESS)
        return TemplateResponse(request, "admin/approval_complete.html", {"object": obj, "action": "approved"})

    def reject_request(self, request, pk):
        obj = RoleUpgradeRequest.objects.get(pk=pk)
        obj.reject(admin_user=request.user, comment="Rejected via Admin Panel")
        self.message_user(request, f"❌ {obj.user.username}'s request rejected.", messages.ERROR)
        return TemplateResponse(request, "admin/approval_complete.html", {"object": obj, "action": "rejected"})


# --------------------------------------------------------
# ✅ 3. User Admin
# --------------------------------------------------------
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "role",
        "is_verified_badge",
        "verified_at",
        "verified_by",
        "verify_button",
        "unverify_button",
    )
    list_filter = ("role", "is_verified")
    search_fields = ("username", "email")

    def is_verified_badge(self, obj):
        color = "green" if obj.is_verified else "red"
        label = "✅ Verified" if obj.is_verified else "❌ Unverified"
        return format_html(f'<span style="color:{color};font-weight:bold;">{label}</span>')
    is_verified_badge.short_description = "Verification Status"

    def verify_button(self, obj):
        if not obj.is_verified:
            return format_html(f'<a class="button" href="/admin/users/user/{obj.id}/verify/">✅ Verify</a>')
        return "—"

    def unverify_button(self, obj):
        if obj.is_verified:
            return format_html(f'<a class="button" href="/admin/users/user/{obj.id}/unverify/">❌ Unverify</a>')
        return "—"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("<int:pk>/verify/", self.admin_site.admin_view(self.verify_user), name="verify_user"),
            path("<int:pk>/unverify/", self.admin_site.admin_view(self.unverify_user), name="unverify_user"),
        ]
        return custom_urls + urls

    def verify_user(self, request, pk):
        user = User.objects.get(pk=pk)
        user.mark_verified(admin_user=request.user)
        self.message_user(request, f"✅ {user.username} has been verified.", messages.SUCCESS)
        return TemplateResponse(request, "admin/approval_complete.html", {"object": user, "action": "approved"})

    def unverify_user(self, request, pk):
        user = User.objects.get(pk=pk)
        user.mark_unverified(admin_user=request.user)
        self.message_user(request, f"❌ {user.username} has been unverified.", messages.WARNING)
        return TemplateResponse(request, "admin/approval_complete.html", {"object": user, "action": "rejected"})


# --------------------------------------------------------
# ✅ 4. Product Admin
# --------------------------------------------------------
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "price", "stock", "is_active_badge", "created_at", "toggle_button")
    list_filter = ("is_active", "category")
    search_fields = ("name", "description")

    def is_active_badge(self, obj):
        color = "green" if obj.is_active else "gray"
        label = "🟢 Active" if obj.is_active else "⚪ Inactive"
        return format_html(f'<span style="color:{color};font-weight:bold;">{label}</span>')

    def toggle_button(self, obj):
        if obj.is_active:
            return format_html(f'<a class="button" href="/admin/products/product/{obj.id}/deactivate/">Deactivate</a>')
        else:
            return format_html(f'<a class="button" href="/admin/products/product/{obj.id}/activate/">Activate</a>')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("<int:pk>/activate/", self.admin_site.admin_view(self.activate_product), name="activate_product"),
            path("<int:pk>/deactivate/", self.admin_site.admin_view(self.deactivate_product), name="deactivate_product"),
        ]
        return custom_urls + urls

    def activate_product(self, request, pk):
        product = Product.objects.get(pk=pk)
        product.is_active = True
        product.save(update_fields=["is_active"])
        self.message_user(request, f"✅ Product '{product.name}' activated.", messages.SUCCESS)
        return TemplateResponse(request, "admin/approval_complete.html", {"object": product, "action": "approved"})

    def deactivate_product(self, request, pk):
        product = Product.objects.get(pk=pk)
        product.is_active = False
        product.save(update_fields=["is_active"])
        self.message_user(request, f"⚪ Product '{product.name}' deactivated.", messages.WARNING)
        return TemplateResponse(request, "admin/approval_complete.html", {"object": product, "action": "rejected"})


# --------------------------------------------------------
# ✅ 5. Order Admin
# --------------------------------------------------------
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status_badge", "total_price", "created_at")
    list_filter = ("status",)
    search_fields = ("user__username",)

    def status_badge(self, obj):
        colors = {
            "pending": "orange",
            "processing": "#0dcaf0",
            "shipped": "#007bff",
            "delivered": "green",
            "cancelled": "red",
        }
        color = colors.get(obj.status, "gray")
        return format_html(f'<span style="color:{color};font-weight:bold;text-transform:capitalize;">{obj.status}</span>')


# --------------------------------------------------------
# ✅ 6. Register everything on the active site
# --------------------------------------------------------
cliffindus_admin_site.register(User, UserAdmin)
cliffindus_admin_site.register(Product, ProductAdmin)
cliffindus_admin_site.register(Category)
cliffindus_admin_site.register(Order, OrderAdmin)
cliffindus_admin_site.register(RoleUpgradeRequest, RoleUpgradeRequestAdmin)
