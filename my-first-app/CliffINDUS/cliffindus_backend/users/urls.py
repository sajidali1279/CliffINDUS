from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RoleUpgradeRequestViewSet, UserViewSet, RegisterUserView

# --------------------------------------------------------
# ✅ ROUTER SETUP
# --------------------------------------------------------
router = DefaultRouter()
router.register(r'upgrade-requests', RoleUpgradeRequestViewSet, basename='upgrade-request')
router.register(r'users', UserViewSet, basename='user')

# --------------------------------------------------------
# ✅ URL PATTERNS
# --------------------------------------------------------
urlpatterns = [
    path('', include(router.urls)),

    # 🔐 Authentication (JWT)
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 🧾 Registration
    path('register/', RegisterUserView.as_view(), name='register'),
]
