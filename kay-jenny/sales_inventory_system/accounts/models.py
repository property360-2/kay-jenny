from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Extended User model with role-based access control"""

    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('CASHIER', 'Cashier'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CASHIER')
    phone = models.CharField(max_length=20, blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'ADMIN'

    @property
    def is_cashier(self):
        return self.role == 'CASHIER'
