from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = (
        ('farmer', 'Farmer'),
        ('customer', 'Customer'),
    )

    phone_number = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')

    # Keep username but make it required and unique
    username = models.CharField(max_length=150, unique=True)

    USERNAME_FIELD = 'phone_number'      # Login with phone
    REQUIRED_FIELDS = ['username', 'role']

    def __str__(self):
        return f"{self.username} ({self.phone_number})"
    
    def save(self, *args, **kwargs):
        if self.phone_number.startswith('0'):
            self.phone_number = '254' + self.phone_number[1:]
        super().save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    farm_size = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # in acres
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"