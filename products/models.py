 
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
        ('grains', 'Grains'),
        ('animal_products', 'Animal Products'),
        ('manure', 'Manure'),
        ('others', 'Others'),
    ]

    farmer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='products'
    )
    name = models.CharField(max_length=255)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='others'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    harvest_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name