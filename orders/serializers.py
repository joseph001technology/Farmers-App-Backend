 
from rest_framework import serializers
from django.db import transaction
from products.models import Product
from .models import Cart, CartItem, Order, OrderItem


class OrderItemDetailSerializer(serializers.ModelSerializer):
    """Used for reading — shows full product info in order detail."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_image',
                  'quantity', 'price']

    def get_product_image(self, obj):
        request = self.context.get('request')
        if obj.product.image and request:
            return request.build_absolute_uri(obj.product.image.url)
        return None


class OrderItemWriteSerializer(serializers.ModelSerializer):
    """Used for writing — accepts product id + quantity."""
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemWriteSerializer(many=True, write_only=True)
    order_items = OrderItemDetailSerializer(
        many=True, read_only=True, source='items'
    )

    class Meta:
        model = Order
        fields = [
            'id', 'items', 'order_items', 'total_price', 'status',
            'payment_method', 'delivery_address', 'created_at', 'user'
        ]
        read_only_fields = [
            'total_price', 'status', 'created_at', 'user'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(total_price=0, **validated_data)
        total_price = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price = product.price
            OrderItem.objects.create(
                order=order, product=product,
                quantity=quantity, price=price
            )
            total_price += price * quantity
        order.total_price = total_price
        order.save()
        return order


class CheckoutSerializer(serializers.Serializer):
    """
    Accepts items array + optional payment_method and delivery_address.
    Creates an Order from the provided items (not from a backend Cart).
    """
    items = serializers.ListField(
        child=serializers.DictField(), write_only=True
    )
    payment_method = serializers.ChoiceField(
        choices=['mpesa', 'pod'], default='mpesa'
    )
    delivery_address = serializers.CharField(
        required=False, allow_blank=True, default=''
    )

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        items_data = validated_data.get('items', [])
        payment_method = validated_data.get('payment_method', 'mpesa')
        delivery_address = validated_data.get('delivery_address', '')

        if not items_data:
            raise serializers.ValidationError("No items provided.")

        # Determine initial status based on payment method
        initial_status = (
            'pending_delivery' if payment_method == 'pod' else 'pending'
        )

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                total_price=0,
                status=initial_status,
                payment_method=payment_method,
                delivery_address=delivery_address,
            )
            total_price = 0
            for item in items_data:
                product = Product.objects.get(id=item['product'])
                quantity = int(item['quantity'])
                OrderItem.objects.create(
                    order=order, product=product,
                    quantity=quantity, price=product.price
                )
                total_price += product.price * quantity

            order.total_price = total_price
            order.save()

        return order


class FarmerSummarySerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    paid_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    delivered_orders = serializers.IntegerField()
    top_product = serializers.CharField()