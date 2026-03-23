from rest_framework import generics
from .models import Payment
from .serializers import PaymentSerializer
from rest_framework.permissions import IsAuthenticated


class PaymentCreateView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]