from rest_framework import serializers
from django.db import transaction
from products.models import Product
from .models import Cart, CartItem, Order, OrderItem
from ratings.serializers import RatingSerializer


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
        with transaction.atomic():
            order = Order.objects.create(total_price=0, **validated_data)
            total_price = 0
            for item_data in items_data:
                product = Product.objects.select_for_update().get(
                    id=item_data['product'].id
                )
                quantity = item_data['quantity']

                if product.quantity < quantity:
                    raise serializers.ValidationError(
                        f"Only {product.quantity} units of '{product.name}' available."
                    )

                OrderItem.objects.create(
                    order=order, product=product,
                    quantity=quantity, price=product.price
                )
                total_price += product.price * quantity

                product.quantity -= quantity
                product.save()

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
                product = Product.objects.select_for_update().get(
                    id=item['product']
                )
                quantity = int(item['quantity'])

                if product.quantity < quantity:
                    raise serializers.ValidationError(
                        f"Only {product.quantity} units of '{product.name}' available."
                    )

                OrderItem.objects.create(
                    order=order, product=product,
                    quantity=quantity, price=product.price
                )
                total_price += product.price * quantity

                product.quantity -= quantity
                product.save()

            order.total_price = total_price
            order.save()

        return order

# ── NEW: Receipt serializer ────────────────────────────────────────
class ReceiptItemSerializer(serializers.ModelSerializer):
    """Line-item on the receipt."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.SerializerMethodField()
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_image',
            'quantity', 'price', 'line_total',
        ]

    def get_product_image(self, obj):
        request = self.context.get('request')
        if obj.product.image and request:
            return request.build_absolute_uri(obj.product.image.url)
        return None

    def get_line_total(self, obj):
        return float(obj.price) * obj.quantity


class ReceiptSerializer(serializers.ModelSerializer):
    """Full invoice-style receipt payload."""
    order_items   = ReceiptItemSerializer(many=True, read_only=True, source='items')
    buyer_name    = serializers.SerializerMethodField()
    buyer_phone   = serializers.SerializerMethodField()
    payment_label = serializers.SerializerMethodField()
    status_label  = serializers.SerializerMethodField()
    seller_name   = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'status_label',
            'total_price',
            'payment_method',
            'payment_label',
            'delivery_address',
            'created_at',
            'buyer_name',
            'buyer_phone',
            'seller_name',
            'order_items',
        ]

    def get_buyer_name(self, obj):
        user = obj.user
        full = f"{user.first_name} {user.last_name}".strip()
        return full or user.username

    def get_buyer_phone(self, obj):
        # Adjust field name if your User model stores phone differently
        return getattr(obj.user, 'phone_number', None) or \
               getattr(obj.user, 'phone', None) or ''

    def get_payment_label(self, obj):
        labels = {
            'mpesa': 'M-Pesa STK Push',
            'pod':   'Pay on Delivery',
        }
        return labels.get(obj.payment_method, obj.payment_method)

    def get_status_label(self, obj):
        labels = {
            'pending':          'Pending Payment',
            'pending_delivery': 'Pending Delivery',
            'paid':             'Paid',
            'out_for_delivery': 'Out for Delivery',
            'delivered':        'Delivered',
            'cancelled':        'Cancelled',
        }
        return labels.get(obj.status, obj.status.title())

    def get_seller_name(self, obj):
        return "FarmFresh Kenya"


# ── (unchanged) ────────────────────────────────────────────────────
class FarmerSummarySerializer(serializers.Serializer):
    total_orders    = serializers.IntegerField()
    total_revenue   = serializers.DecimalField(max_digits=12, decimal_places=2)
    paid_orders     = serializers.IntegerField()
    pending_orders  = serializers.IntegerField()
    delivered_orders = serializers.IntegerField()
    top_product     = serializers.CharField()