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
    
    
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

class CustomTokenSerializer(TokenObtainPairSerializer):
    username_field = 'phone_number'

    def validate(self, attrs):
        # Get the phone number from whatever key the frontend sends
        phone_number = attrs.get('phone_number') or attrs.get('phone')
        password = attrs.get('password')

        if not phone_number or not password:
            raise serializers.ValidationError("Phone number and password are required.")

        # 🔥 IMPORTANT: Pass the data using the exact key that username_field expects
        # We override the data so SimpleJWT finds 'phone_number'
        attrs = {
            'phone_number': phone_number,
            'password': password,
        }

        # Now call the parent with correctly keyed data
        data = super().validate(attrs)

        # Add extra fields to the response
        data['role'] = self.user.role
        data['username'] = self.user.username
        data['phone_number'] = self.user.phone_number

        return data