from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
@permission_classes([AllowAny])    
def api_root(request, format=None):
    return Response({
        'products': reverse('product-list-create', request=request, format=format),
        'orders': reverse('order-list-create', request=request, format=format),
        'payments': reverse('payment-create', request=request, format=format),
        'users-register': reverse('register', request=request, format=format),
       'users-login': reverse('token_obtain_pair', request=request, format=format),  
    })