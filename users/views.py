from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import CustomTokenSerializer, UserSerializer, UserLoginSerializer

# ✅ REGISTER VIEW
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# ✅ LOGIN VIEW
class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")

        user = authenticate(request, phone_number=phone_number, password=password)

        if user is not None:
            return Response({
                "message": "Login successful",
                "user_id": user.id,
                "phone_number": user.phone_number,
                "username": user.username,
                "role": user.role
            })
        else:
            return Response({
                "error": "Invalid credentials"
            }, status=status.HTTP_401_UNAUTHORIZED)
            
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer