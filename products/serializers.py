## products/serializers.py

from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    # Writable for upload, excluded from read output (image_url is used instead)
    image     = serializers.ImageField(required=False, allow_null=True, use_url=False)
    image_url = serializers.SerializerMethodField()

    # Flat farmer fields — Flutter reads these directly
    farmer_id       = serializers.SerializerMethodField()
    farmer_name     = serializers.SerializerMethodField()
    farmer_phone    = serializers.SerializerMethodField()
    farmer_location = serializers.SerializerMethodField()
    farmer_photo    = serializers.SerializerMethodField()

    # Ratings
    average_rating = serializers.SerializerMethodField()
    rating_count   = serializers.SerializerMethodField()

    class Meta:
        model  = Product
        fields = [
            'id', 'name', 'category', 'price',
            'quantity', 'description', 'unit',
            'image', 'image_url',
            'harvest_date', 'created_at',
            # Farmer
            'farmer_id', 'farmer_name', 'farmer_phone',
            'farmer_location', 'farmer_photo',
            # Ratings
            'average_rating', 'rating_count',
        ]
        read_only_fields = ['created_at']

    # ── Farmer fields ───────────────────────────────────────────────

    def get_farmer_id(self, obj):
        return obj.farmer.id

    def get_farmer_name(self, obj):
        return obj.farmer.username

    def get_farmer_phone(self, obj):
        return obj.farmer.phone_number

    def get_farmer_location(self, obj):
        """Return farmer's location from their profile."""
        try:
            return obj.farmer.profile.location
        except Exception:
            return None

    def get_farmer_photo(self, obj):
        """Return absolute URL of farmer's profile photo."""
        try:
            photo = obj.farmer.profile.profile_photo
            if not photo:
                return None
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(photo.url)
            return f"https://josephkiarie2.pythonanywhere.com{photo.url}"
        except Exception:
            return None

    # ── Product image ───────────────────────────────────────────────

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    # ── Ratings ─────────────────────────────────────────────────────

    def get_average_rating(self, obj):
        from ratings.models import Rating
        from django.db.models import Avg
        avg = (Rating.objects
               .filter(farmer=obj.farmer)
               .aggregate(avg=Avg('stars'))['avg'])
        return round(avg, 1) if avg else None

    def get_rating_count(self, obj):
        from ratings.models import Rating
        return Rating.objects.filter(farmer=obj.farmer).count()