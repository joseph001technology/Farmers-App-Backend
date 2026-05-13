## users/serializers.py
## Replace your existing file with this

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Profile


class ProfileSerializer(serializers.ModelSerializer):
    # Return absolute URL for profile_photo so Flutter can load it directly
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['profile_photo', 'bio', 'location', 'farm_size']

    def get_profile_photo(self, obj):
        if not obj.profile_photo:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.profile_photo.url)
        # Fallback: build URL manually using your domain
        return f"https://josephkiarie2.pythonanywhere.com{obj.profile_photo.url}"


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    profile  = ProfileSerializer(read_only=True)

    class Meta:
        model  = User
        fields = ['id', 'phone_number', 'username', 'email',
                  'role', 'password', 'profile']

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        Profile.objects.create(user=user)
        return user


# Public read-only serializer — safe to expose without auth
class PublicFarmerSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model  = User
        fields = ['id', 'username', 'role', 'profile']


class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    password     = serializers.CharField(write_only=True, required=True)


class CustomTokenSerializer(TokenObtainPairSerializer):
    username_field = 'phone_number'

    def validate(self, attrs):
        phone_number = attrs.get('phone_number') or attrs.get('phone')
        password     = attrs.get('password')

        if not phone_number or not password:
            raise serializers.ValidationError(
                "Phone number and password are required.")

        attrs = {'phone_number': phone_number, 'password': password}
        data  = super().validate(attrs)

        data['role']         = self.user.role
        data['username']     = self.user.username
        data['phone_number'] = self.user.phone_number

        return data