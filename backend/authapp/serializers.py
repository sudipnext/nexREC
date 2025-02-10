from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from djoser.serializers import TokenCreateSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token

User = get_user_model()

class CustomTokenCreateSerializer(TokenCreateSerializer):
    def validate(self, attrs):
        # Authenticate the user
        self.user = authenticate(
            email=attrs['email'],
            password=attrs['password'],
        )

        if not self.user:
            raise AuthenticationFailed(_('Invalid credentials'), 'authorization')

        # Allow token creation regardless of is_active status
        return attrs


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
        )
        user.save()  # Save the user instance first to get a primary key
        user.set_password(validated_data['password'])
        user.save()  # Save again to store the hashed password
        return user
    

class VerifyOtpSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    email = serializers.EmailField()

class ResetEmailPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordConfirmSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    email = serializers.EmailField()
    new_password = serializers.CharField(max_length=128)


class SetEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
    password = serializers.CharField(max_length=128)


class SocialTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def create(self, validated_data):
        user = User.objects.get(email=validated_data['email'])
        token, created = Token.objects.get_or_create(user=user)
        return {
            'token': token.key,
            'user': user.email
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'is_active', 'is_staff', 'is_superuser']
        read_only_fields = ['id', 'is_active', 'is_staff', 'is_superuser']
