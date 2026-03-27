from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['profile_photo', 'bio', 'location', 'farm_size']


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'username', 'email', 'role', 'password', 'profile']

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Auto-create profile
        Profile.objects.create(user=user)
        return user
    
class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    
class CustomTokenSerializer(TokenObtainPairSerializer):
    username_field = 'phone_number'