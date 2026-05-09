from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Order
from .serializers import (
    CheckoutSerializer,
    OrderSerializer,
    ReceiptSerializer,
)


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only fetch their own orders
        return Order.objects.filter(user=self.request.user)


class CheckoutView(generics.CreateAPIView):
    serializer_class = CheckoutSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        order_serializer = OrderSerializer(order, context={'request': request})
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)


# ── NEW: cancel order ──────────────────────────────────────────────
class OrderCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)

        if order.status not in ('pending', 'pending_delivery'):
            return Response(
                {"error": "Only pending orders can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = 'cancelled'
        order.save()
        return Response({"message": f"Order #{order.id} cancelled."})


# ── NEW: receipt endpoint ──────────────────────────────────────────
class OrderReceiptView(APIView):
    """
    GET /api/orders/<pk>/receipt/

    Returns a full invoice-style receipt for the given order.
    Only available once the order is paid or delivered.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)

        if order.status not in ('paid', 'delivered'):
            return Response(
                {
                    "error": "Receipt is only available for paid or delivered orders.",
                    "status": order.status,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ReceiptSerializer(order, context={'request': request})
        return Response(serializer.data)