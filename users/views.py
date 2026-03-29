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
 