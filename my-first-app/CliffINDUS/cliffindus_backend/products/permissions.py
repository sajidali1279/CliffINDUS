from rest_framework import permissions


class IsRetailerOrWholesalerOrReadOnly(permissions.BasePermission):
    """
    Allows retailers and wholesalers (verified) to modify products.
    Everyone else has read-only (safe method) access.
    """

    def has_permission(self, request, view):
        # ✅ Allow safe methods (GET, HEAD, OPTIONS) for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user

        # ✅ Ensure authenticated and verified
        if not getattr(user, "is_authenticated", False):
            return False

        role = getattr(user, "role", None)
        is_verified = getattr(user, "is_verified", False)

        return role in ["retailer", "wholesaler"] and is_verified
