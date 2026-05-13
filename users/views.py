## users/views.py
## Replace your existing file with this

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import NotFound

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, Profile
from .serializers import (
    CustomTokenSerializer, UserSerializer,
    ProfileSerializer, PublicFarmerSerializer,
)

User = get_user_model()


# ── AUTH ───────────────────────────────────────────────────────────────
class RegisterView(generics.CreateAPIView):
    queryset           = User.objects.all()
    serializer_class   = UserSerializer
    permission_classes = [AllowAny]


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer


# ── OWN PROFILE (authenticated) ────────────────────────────────────────
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        return Response({
            "id":           request.user.id,
            "username":     request.user.username,
            "phone_number": request.user.phone_number,
            "email":        request.user.email,
            "role":         request.user.role,
            "profile":      ProfileSerializer(
                                profile, context={'request': request}
                            ).data,
        })

    def put(self, request):
        user    = request.user
        profile, _ = Profile.objects.get_or_create(user=user)

        user.username = request.data.get("username", user.username)
        user.email    = request.data.get("email",    user.email)
        user.save()

        profile.bio       = request.data.get("bio",       profile.bio)
        profile.location  = request.data.get("location",  profile.location)
        profile.farm_size = request.data.get("farm_size", profile.farm_size)

        if "profile_photo" in request.FILES:
            profile.profile_photo = request.FILES["profile_photo"]

        profile.save()

        return Response({
            "message":  "Profile updated successfully",
            "username": user.username,
            "email":    user.email,
            "profile":  ProfileSerializer(
                            profile, context={'request': request}
                        ).data,
        })


# ── PUBLIC FARMER PROFILE (no auth required) ───────────────────────────
class PublicFarmerProfileView(APIView):
    """
    GET /api/users/farmer/<id>/
    Returns public info for a farmer: id, username, role, profile photo,
    bio, location, farm_size.  No authentication required.
    """
    permission_classes = [AllowAny]

    def get(self, request, farmer_id):
        try:
            user = User.objects.select_related('profile').get(
                pk=farmer_id, role='farmer'
            )
        except User.DoesNotExist:
            raise NotFound(f"Farmer with id {farmer_id} not found.")

        # Ensure profile exists
        Profile.objects.get_or_create(user=user)
        serializer = PublicFarmerSerializer(user, context={'request': request})
        return Response(serializer.data)


# ── PUBLIC FARMER LIST (no auth required) ─────────────────────────────
class PublicFarmerListView(generics.ListAPIView):
    """
    GET /api/users/farmers/
    Returns all farmers with their public profiles.
    """
    permission_classes = [AllowAny]
    serializer_class   = PublicFarmerSerializer

    def get_queryset(self):
        return (User.objects
                .filter(role='farmer')
                .select_related('profile')
                .order_by('username'))