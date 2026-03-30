from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        # Products
        'products': reverse('product-list-create', request=request, format=format),

        # Orders
        'orders': reverse('order-list-create', request=request, format=format),
        'checkout': reverse('checkout', request=request, format=format),

        # Users / Auth
        'register': reverse('register', request=request, format=format),
        'login': reverse('login', request=request, format=format),
        'token_refresh': reverse('token_refresh', request=request, format=format),

        # Payments
        'mpesa_stk_push': reverse('mpesa-stk-push', request=request, format=format),
        'mpesa_callback': reverse('mpesa-callback', request=request, format=format),
        'profile': reverse('profile', request=request, format=format),
    })