# users/serializers.py
from rest_framework import serializers
from .models import User, RoleUpgradeRequest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_verified', 'phone', 'address']

class RoleUpgradeRequestSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = RoleUpgradeRequest
        fields = [
            'id', 'user', 'requested_role', 'business_name',
            'business_license', 'status', 'admin_comment',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['status', 'admin_comment']
