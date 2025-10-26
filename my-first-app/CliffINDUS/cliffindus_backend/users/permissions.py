from rest_framework import permissions


# 🛡️ 1. Admin Access
class IsAdmin(permissions.BasePermission):
    """
    Grants full access only to authenticated users with role='admin'.
    Used for managing all accounts, verifications, and backend data.
    """
    def has_permission(self, request, view):
        user = request.user
        return (
            getattr(user, "is_authenticated", False)
            and getattr(user, "role", None) == "admin"
        )


# 🛡️ 2. Retailer / Wholesaler (Verified)
class IsRetailerOrWholesalerOrReadOnly(permissions.BasePermission):
    """
    Retailers and Wholesalers can create/update/delete only if verified.
    Everyone else (including unauthenticated users) can read safely.
    """
    def has_permission(self, request, view):
        # Allow safe methods for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user

        if not getattr(user, "is_authenticated", False):
            return False

        role = getattr(user, "role", None)
        is_verified = getattr(user, "is_verified", False)

        return role in ["retailer", "wholesaler"] and is_verified


# 🛡️ 3. Consumer Access
class IsConsumer(permissions.BasePermission):
    """
    Allows access only to verified consumers (for cart, order, shipping APIs).
    """
    def has_permission(self, request, view):
        user = request.user
        return (
            getattr(user, "is_authenticated", False)
            and getattr(user, "role", None) == "consumer"
            and getattr(user, "is_verified", True)  # Optional verification
        )


# 🛡️ 4. Read-Only (Public Safe Access)
class ReadOnly(permissions.BasePermission):
    """
    Grants read-only (GET/HEAD/OPTIONS) access to all users, including anonymous.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
