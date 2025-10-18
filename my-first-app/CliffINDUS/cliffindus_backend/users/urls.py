from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoleUpgradeRequestViewSet, UserViewSet, RegisterUserView

router = DefaultRouter()
router.register(r'upgrade-requests', RoleUpgradeRequestViewSet, basename='upgrade-request')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterUserView.as_view(), name='register'),
]
