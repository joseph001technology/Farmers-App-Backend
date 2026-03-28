from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User
from .serializers import CustomTokenSerializer, UserSerializer


# ✅ REGISTER VIEW
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# ✅ LOGIN VIEW (This is the only login view we need)
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer