from rest_framework import permissions

# 🛡️ 1. Admin Access
class IsAdmin(permissions.BasePermission):
    """
    Grants full access only to users with role='admin'.
    Used for verification, management, and platform control.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )

# 🛡️ 2. Retailer/Wholesaler (Verified)
class IsRetailerOrWholesalerOrReadOnly(permissions.BasePermission):
    """
    Retailers and Wholesalers can create/update/delete only if verified.
    Everyone else has read-only access.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  # Allow GET, HEAD, OPTIONS for everyone

        user = request.user
        return (
            user.is_authenticated and
            user.role in ['retailer', 'wholesaler'] and
            getattr(user, 'is_verified', False)
        )

# 🛡️ 3. Consumer Access
class IsConsumer(permissions.BasePermission):
    """
    Allows access only to verified consumers (e.g., cart, orders).
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'consumer'
        )

# 🛡️ 4. Read-Only for Everyone (Safe GET access)
class ReadOnly(permissions.BasePermission):
    """
    Allows only GET/HEAD/OPTIONS.
    Useful for public views like product listing or promotions.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
