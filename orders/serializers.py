from rest_framework import serializers

from products.models import Product
from .models import Cart, CartItem, Order, OrderItem
from products.serializers import ProductSerializer
from django.db import transaction

# -------- CART --------
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'


# -------- ORDER --------
class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']   # ONLY these


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)
    order_items = OrderItemSerializer(many=True, read_only=True, source='items')

    class Meta:
        model = Order
        fields = ['id', 'items', 'order_items', 'total_price', 'status', 'created_at', 'user']
        read_only_fields = ['total_price', 'status', 'created_at', 'user']

    def create(self, validated_data):   # 👈 RIGHT HERE
        items_data = validated_data.pop('items')

        order = Order.objects.create(
            total_price=0,
            **validated_data
        )

        total_price = 0

        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price = product.price

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )

            total_price += price * quantity

        order.total_price = total_price
        order.save()

        return order
    
    
class CheckoutSerializer(serializers.Serializer):
    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Your cart is empty.")

        # Use the correct related_name (most common is cartitem_set)
        cart_items = cart.cartitem_set.all()   # ← Change this if your related_name is different

        if not cart_items.exists():
            raise serializers.ValidationError("Your cart is empty.")

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                total_price=0,
                status="pending"
            )

            total_price = 0

            for cart_item in cart_items:
                order_item = OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                total_price += order_item.price * order_item.quantity

            order.total_price = total_price
            order.save()

            # Optional: Clear cart after successful checkout
            # cart.cartitem_set.all().delete()

        return order