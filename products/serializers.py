 
from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    farmer = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'farmer', 'name', 'category', 'price',
            'quantity', 'description', 'image',
            'harvest_date', 'average_rating', 'created_at'
        ]
        read_only_fields = ['created_at']

    def get_farmer(self, obj):
        return f"{obj.farmer.username} ({obj.farmer.phone_number})"

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_average_rating(self, obj):
        from ratings.models import Rating
        from django.db.models import Avg
        avg = Rating.objects.filter(
            farmer=obj.farmer
        ).aggregate(avg=Avg('stars'))['avg']
        return round(avg, 1) if avg else None