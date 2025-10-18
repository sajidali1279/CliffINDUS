from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone


# --------------------------------------------------------
# ✅ CUSTOM USER MODEL
# --------------------------------------------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('wholesaler', 'Wholesaler'),
        ('retailer', 'Retailer'),
        ('consumer', 'Consumer'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='consumer')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    # 🧩 Verification tracking fields
    verified_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_users",
        help_text="Admin who verified this account",
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    # --------------------------------------------------------
    # ✅ Helper Methods
    # --------------------------------------------------------

    def mark_verified(self, admin_user=None):
        """Mark this user as verified, set who verified and when."""
        self.is_verified = True
        self.verified_by = admin_user
        self.verified_at = timezone.now()
        self.save(update_fields=["is_verified", "verified_by", "verified_at"])

    def mark_unverified(self, admin_user=None):
        """Unverify this user and clear related info."""
        self.is_verified = False
        self.verified_by = admin_user
        self.verified_at = None
        self.save(update_fields=["is_verified", "verified_by", "verified_at"])

    def get_verification_info(self):
        """Return a readable string of who verified and when."""
        if not self.is_verified:
            return "Unverified"
        admin_name = self.verified_by.username if self.verified_by else "Unknown Admin"
        verified_time = self.verified_at.strftime("%Y-%m-%d %H:%M UTC") if self.verified_at else "N/A"
        return f"Verified by {admin_name} on {verified_time}"

    def __str__(self):
        return f"{self.username} ({self.role})"


# --------------------------------------------------------
# ✅ ROLE UPGRADE REQUEST MODEL
# --------------------------------------------------------
class RoleUpgradeRequest(models.Model):
    ROLE_CHOICES = [
        ('retailer', 'Retailer'),
        ('wholesaler', 'Wholesaler'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='upgrade_requests'
    )
    requested_role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    business_license = models.FileField(upload_to='licenses/', blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    admin_comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --------------------------------------------------------
    # ✅ Helper Methods
    # --------------------------------------------------------

    def approve(self, admin_user=None, comment=None):
        """Approve the request and verify the user."""
        self.status = 'approved'
        self.admin_comment = comment or ''
        self.save(update_fields=["status", "admin_comment"])
        self.user.role = self.requested_role
        self.user.mark_verified(admin_user=admin_user)

    def reject(self, admin_user=None, comment=None):
        """Reject the request."""
        self.status = 'rejected'
        self.admin_comment = comment or ''
        self.save(update_fields=["status", "admin_comment"])

    def __str__(self):
        return f"{self.user.username} → {self.requested_role} ({self.status})"

    class Meta:
        verbose_name = "Role Upgrade Request"
        verbose_name_plural = "Role Upgrade Requests"
        ordering = ['-created_at']
