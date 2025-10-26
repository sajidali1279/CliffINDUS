from rest_framework import serializers
from .models import User, RoleUpgradeRequest


# --------------------------------------------------------
# ✅ USER SERIALIZER
# --------------------------------------------------------
class UserSerializer(serializers.ModelSerializer):
    verified_info = serializers.CharField(source="get_verification_info", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "role", "is_verified",
            "phone", "address", "verified_info",
        ]
        read_only_fields = ["is_verified", "verified_info"]

    def to_representation(self, instance):
        """Hide sensitive fields for consumers or public users."""
        data = super().to_representation(instance)
        user = self.context.get("request").user if self.context.get("request") else None

        # Only admins can view phone/address of other users
        if not getattr(user, "is_authenticated", False) or getattr(user, "role", None) != "admin":
            data.pop("phone", None)
            data.pop("address", None)

        return data


# --------------------------------------------------------
# ✅ ROLE UPGRADE REQUEST SERIALIZER
# --------------------------------------------------------
class RoleUpgradeRequestSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    requested_role_display = serializers.CharField(source="get_requested_role_display", read_only=True)

    class Meta:
        model = RoleUpgradeRequest
        fields = [
            "id", "user", "requested_role", "requested_role_display",
            "business_name", "business_license",
            "status", "admin_comment", "created_at", "updated_at"
        ]
        read_only_fields = ["status", "admin_comment", "created_at", "updated_at"]
