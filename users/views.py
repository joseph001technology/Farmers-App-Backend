from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from users.models import User
from .serializers import CustomTokenSerializer, UserSerializer


# ✅ REGISTER VIEW
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


# ✅ LOGIN VIEW (This is the only login view we need)
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer
    
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
 

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def create_superuser(request):
    """Temporary endpoint to create superuser on Render Free plan"""
    username = request.data.get('username')
    phone_number = request.data.get('phone_number')
    password = request.data.get('password')
    role = request.data.get('role', 'customer')

    if not username or not phone_number or not password:
        return Response({"error": "username, phone_number and password are required"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "User with this username already exists"}, status=400)

    if User.objects.filter(phone_number=phone_number).exists():
        return Response({"error": "User with this phone number already exists"}, status=400)

    try:
        user = User.objects.create_superuser(
            username=username,
            phone_number=phone_number,
            password=password,
            role=role
        )
        return Response({
            "message": f"Superuser '{username}' created successfully!",
            "user_id": user.id,
            "phone_number": user.phone_number
        })
    except Exception as e:
        return Response({"error": str(e)}, status=400)