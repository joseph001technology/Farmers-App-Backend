 
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('fresh_produce', 'Fresh Produce'),
        ('grains_seeds', 'Grains & Seeds'),
        ('livestock', 'Livestock & Poultry'),
        ('animal_derivatives', 'Animal Derivatives'),
        ('processed_goods', 'Value-Added Goods'),
        ('nursery_floral', 'Nursery & Floral'),
        ('inputs_chemicals', 'Inputs & Amendments'),
        ('animal_feed', 'Feed & Nutrition'),
        ('machinery', 'Heavy Machinery'),
        ('tools_hardware', 'Tools & Hardware'),
        ('timber_bio', 'Timber & Bio-Resources'),
        ('services', 'Farm Services'),
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