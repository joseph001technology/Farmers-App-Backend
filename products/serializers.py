from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    farmer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'