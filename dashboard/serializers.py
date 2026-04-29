# dashboard/serializers.py
from rest_framework import serializers


class FarmerDashboardSerializer(serializers.Serializer):
    """
    Response shape for GET /api/dashboard/farmer/
    Returns a summary of the authenticated farmer's
    sales performance.
    """
    total_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(
        max_digits=12, decimal_places=2
    )
    paid_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    delivered_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()
    total_products_listed = serializers.IntegerField()
    average_rating = serializers.FloatField()
    total_ratings = serializers.IntegerField()
    top_products = serializers.ListField(
        child=serializers.DictField()
    )
    revenue_last_7_days = serializers.ListField(
        child=serializers.DictField()
    )


class AdminDashboardSerializer(serializers.Serializer):
    """
    Response shape for GET /api/dashboard/admin/
    Returns platform-wide analytics for county
    government or system administrators.
    """
    total_users = serializers.IntegerField()
    total_farmers = serializers.IntegerField()
    total_consumers = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(
        max_digits=14, decimal_places=2
    )
    orders_by_status = serializers.DictField()
    top_selling_products = serializers.ListField(
        child=serializers.DictField()
    )
    top_farmers_by_revenue = serializers.ListField(
        child=serializers.DictField()
    )
    products_by_category = serializers.ListField(
        child=serializers.DictField()
    )
    orders_last_7_days = serializers.ListField(
        child=serializers.DictField()
    )