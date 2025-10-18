from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.http import JsonResponse


def root_view(request):
    return JsonResponse({"message": "Welcome to the CliffINDUS API 🚀"})


urlpatterns = [
    path('admin/', admin.site.urls),

    # 🔐 JWT endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 🧩 Full dotted paths for internal apps
    path('api/auth/', include('cliffindus_backend.authentication.urls')),
    path('api/products/', include('cliffindus_backend.products.urls')),
    path('api/users/', include('cliffindus_backend.users.urls')),
    path('api/', include('cliffindus_backend.users.urls')),


    # 🌐 Root endpoint
    path('', root_view),
]
