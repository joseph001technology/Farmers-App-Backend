from rest_framework import serializers
from .models import Rating
from orders.models import Order


class RatingSerializer(serializers.ModelSerializer):
    consumer_name = serializers.CharField(
        source='consumer.username', read_only=True
    )
    farmer_name = serializers.CharField(
        source='farmer.username', read_only=True
    )

    class Meta:
        model = Rating
        fields = [
            'id', 'farmer', 'farmer_name', 'consumer', 'consumer_name',
            'order', 'stars', 'review', 'created_at'
        ]
        read_only_fields = ['consumer', 'created_at']

    def validate_order(self, order):
        request = self.context['request']
        # Only the consumer who placed the order can rate
        if order.user != request.user:
            raise serializers.ValidationError(
                "You can only rate orders you placed."
            )
        # Order must be delivered before rating
        if order.status != 'delivered':
            raise serializers.ValidationError(
                "You can only rate after the order is delivered."
            )
        # Prevent duplicate ratings
        if hasattr(order, 'rating'):
            raise serializers.ValidationError(
                "You have already rated this order."
            )
        return order

    def validate_farmer(self, farmer):
        if farmer.role != 'farmer':
            raise serializers.ValidationError("Rated user must be a farmer.")
        return farmer

    def create(self, validated_data):
        validated_data['consumer'] = self.context['request'].user
        return super().create(validated_data)


class FarmerRatingSummarySerializer(serializers.Serializer):
    farmer_id = serializers.IntegerField()
    farmer_name = serializers.CharField()
    average_stars = serializers.FloatField()
    total_ratings = serializers.IntegerField()
    ratings = RatingSerializer(many=True)