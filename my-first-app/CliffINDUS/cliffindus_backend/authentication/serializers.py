from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from cliffindus_backend.users.models import User


User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles user registration, password validation,
    and ensures both passwords match before saving.
    """
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "password2",
            "role",
            "phone",
            "address",
        )
        extra_kwargs = {
            "email": {"required": True},
        }

    def validate(self, attrs):
        """
        Ensure both password fields match.
        """
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        """
        Remove password2, create user securely.
        """
        validated_data.pop("password2", None)

        if "role" not in validated_data or not validated_data["role"]:
            validated_data["role"] = "consumer"

        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    For returning user details via /api/auth/user/ endpoint.
    (Used internally if needed for other APIs)
    """
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "role",
            "phone",
            "address",
        )
