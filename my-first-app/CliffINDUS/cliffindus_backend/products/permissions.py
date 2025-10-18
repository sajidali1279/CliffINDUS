from rest_framework import permissions

class IsRetailerOrWholesalerOrReadOnly(permissions.BasePermission):
    """
    Allow only Retailers and Wholesalers to modify products.
    Consumers can only view.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        return user.is_authenticated and user.role in ['retailer', 'wholesaler']
