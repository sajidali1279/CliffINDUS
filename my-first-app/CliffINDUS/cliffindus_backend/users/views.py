from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import RoleUpgradeRequest
from .serializers import RoleUpgradeRequestSerializer
from rest_framework.decorators import action
from .models import User
from .serializers import UserSerializer
from cliffindus_backend.users.permissions import IsAdmin
from rest_framework.views import APIView
from .serializers import UserSerializer



class RoleUpgradeRequestViewSet(viewsets.ModelViewSet):
    """
    Handles creation, listing, and admin approval/rejection of role-upgrade requests.
    """
    queryset = RoleUpgradeRequest.objects.all().order_by('-created_at')
    serializer_class = RoleUpgradeRequestSerializer

    # 🔐 Permission control
    def get_permissions(self):
        if self.action in ['list', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    # 📋 Filter so normal users see only their own requests
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return RoleUpgradeRequest.objects.all().order_by('-created_at')
        return RoleUpgradeRequest.objects.filter(user=user).order_by('-created_at')

    # 📨 Create new upgrade request (user-initiated)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # 🛠️ Admin approval/rejection logic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        if not (user.is_authenticated and user.role == 'admin'):
            return Response(
                {'detail': 'Only admins can approve or reject requests.'},
                status=status.HTTP_403_FORBIDDEN
            )

        status_value = request.data.get('status')
        admin_comment = request.data.get('admin_comment', '').strip()

        if status_value not in ['approved', 'rejected']:
            return Response(
                {'detail': "Invalid status. Must be 'approved' or 'rejected'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.status = status_value
        instance.admin_comment = admin_comment
        instance.save()

        # --- Update user on approval
        if status_value == 'approved':
            instance.user.role = instance.requested_role
            instance.user.is_verified = True
            instance.user.save()

        # --- Send notification email (optional)
        try:
            subject = f"Your role-upgrade request has been {status_value.title()}"
            message = (
                f"Hello {instance.user.username},\n\n"
                f"Your request to upgrade to '{instance.requested_role}' has been {status_value}.\n"
                f"Admin comment: {admin_comment or 'No comment provided.'}\n\n"
                f"— CliffINDUS Team"
            )
            send_mail(
                subject,
                message,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@cliffindus.com'),
                [instance.user.email],
                fail_silently=True,
            )
        except Exception:
            pass  # ignore email failure in dev

        return Response(RoleUpgradeRequestSerializer(instance).data, status=status.HTTP_200_OK)
class UserViewSet(viewsets.ModelViewSet):
    """
    Admin-only viewset for managing user verification and accounts.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    @action(detail=True, methods=['patch'], url_path='verify', permission_classes=[IsAdmin])
    def verify_user(self, request, pk=None):
        """
        PATCH /api/users/<id>/verify/
        Admin-only endpoint to verify wholesalers or retailers directly.
        """
        user = self.get_object()

        if user.role not in ['wholesaler', 'retailer']:
            return Response(
                {"detail": "Only wholesalers or retailers can be verified."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_verified = True
        user.save()

        return Response(
            {"detail": f"{user.role.capitalize()} '{user.email}' verified successfully."},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['patch'], url_path='unverify', permission_classes=[IsAdmin])
    def unverify_user(self, request, pk=None):
        """
        PATCH /api/users/<id>/unverify/
        Allows admin to revoke verification (suspend access).
        """
        user = self.get_object()

        if user.role not in ['wholesaler', 'retailer']:
            return Response(
                {"detail": "Only wholesalers or retailers can be unverified."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_verified = False
        user.save()

        return Response(
            {"detail": f"{user.role.capitalize()} '{user.email}' unverified successfully."},
            status=status.HTTP_200_OK
        )
class RegisterUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Public endpoint for new user registration.
        Defaults to role='consumer' unless specified.
        """
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(role='consumer', is_verified=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)