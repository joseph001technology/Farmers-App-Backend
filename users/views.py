from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, Profile
from .serializers import CustomTokenSerializer, UserSerializer, ProfileSerializer

User = get_user_model()

# ====================== AUTH ======================
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer


# ====================== PROFILE ======================
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "phone_number": request.user.phone_number,
            "email": request.user.email,
            "role": request.user.role,
            "profile": ProfileSerializer(profile).data
        })

    def put(self, request):
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)

        # Update User fields
        user.username = request.data.get("username", user.username)
        user.email = request.data.get("email", user.email)
        user.save()

        # Update Profile fields
        profile.bio = request.data.get("bio", profile.bio)
        profile.location = request.data.get("location", profile.location)
        profile.farm_size = request.data.get("farm_size", profile.farm_size)

        if "profile_photo" in request.FILES:
            profile.profile_photo = request.FILES["profile_photo"]

        profile.save()

        return Response({
            "message": "Profile updated successfully",
            "username": user.username,
            "email": user.email,
            "profile": ProfileSerializer(profile).data
        })