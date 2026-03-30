from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .mpesa import stk_push
from orders.models import Order
from rest_framework.decorators import api_view, permission_classes


class MpesaSTKPushView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phone = request.data.get("phone")
        order_id = request.data.get("order_id")

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        response = stk_push(phone, order.total_price, f"Order {order.id}")

        # 🔥 SAVE THIS
        checkout_id = response.get("CheckoutRequestID")

        if checkout_id:
            order.checkout_request_id = checkout_id
            order.save()

        return Response(response)


@api_view(['POST'])
@permission_classes([AllowAny])
def mpesa_callback(request):
    data = request.data

    try:
        result = data['Body']['stkCallback']

        checkout_id = result.get('CheckoutRequestID')
        result_code = result.get('ResultCode')

        if result_code == 0:  # ✅ SUCCESS
            order = Order.objects.filter(
                checkout_request_id=checkout_id
            ).first()

            if order:
                order.status = "paid"
                order.save()
                print(f"✅ Payment success for Order {order.id}")

        else:
            print("❌ Payment failed")

    except Exception as e:
        print("❌ Callback error:", e)

    return Response({"message": "Callback received"})