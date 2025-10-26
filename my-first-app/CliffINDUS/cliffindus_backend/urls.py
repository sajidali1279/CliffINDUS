from django.urls import path, include
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from cliffindus_backend.users.admin_dashboard import cliffindus_admin_site


# --------------------------------------------------------
# ✅ ROOT API VIEW
# --------------------------------------------------------
def root_view(request):
    return JsonResponse({
        "message": "Welcome to the CliffINDUS API 🚀",
        "available_endpoints": {
            "users": "/api/users/",
            "products": "/api/products/",
            "auth": "/api/users/auth/login/",
            "admin_panel": "/admin/",
        }
    })


# --------------------------------------------------------
# ✅ URL ROUTES
# --------------------------------------------------------
urlpatterns = [
    # 🧭 Custom Admin Dashboard
    path("admin/", cliffindus_admin_site.urls),

    # 🔐 JWT Authentication (global fallback)
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # 🧩 App-specific APIs
    path("api/users/", include("cliffindus_backend.users.urls")),
    path("api/products/", include("cliffindus_backend.products.urls")),

    # 🌍 Root welcome route
    path("", root_view),
]
