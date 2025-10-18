from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer
from cliffindus_backend.products.models import Cart


User = get_user_model()


# ---------------------------
# Register new users (with auto-cart + JWT tokens)
# ---------------------------
class RegisterView(generics.CreateAPIView):
    """
    Allows anyone to register a new account.
    Automatically creates a Cart for the user.
    Returns JWT tokens on success.
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # ✅ Auto-create Cart for the new user
        try:
            Cart.objects.get_or_create(user=user)
        except Exception as e:
            print(f"[AutoCart] Failed to create cart for {user.username}: {e}")

        # ✅ Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": serializer.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

# ---------------------------
# Logout (Blacklist refresh token)
# ---------------------------
class LogoutView(generics.GenericAPIView):
    """
    Allows authenticated users to log out by blacklisting the refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST
            )


# ---------------------------
# User profile (JWT protected)
# ---------------------------
class UserDetailView(generics.RetrieveAPIView):
    """
    Returns details for the currently authenticated user.
    Requires a valid JWT access token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": getattr(user, "role", None),
            "phone": getattr(user, "phone", None),
            "address": getattr(user, "address", None),
        }
        return Response(data, status=status.HTTP_200_OK)
