from rest_framework.response import Response
from rest_framework import status
from .models import Otp, UserAccount
from .serializers import VerifyOtpSerializer, ResetEmailPasswordSerializer, ResetPasswordConfirmSerializer, SetEmailSerializer
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from django.core.mail import send_mail
import random
from backend import settings
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from rest_framework.authentication import TokenAuthentication as DRFTokenAuthentication
import requests
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework import viewsets
from .serializers import SocialTokenSerializer
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags




class CustomTokenAuthentication(DRFTokenAuthentication):
    """
    Custom authentication class for token-based authentication to bypass djoser's default authentication
    """
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        return (token.user, token)




class CustomUserViewSet(DjoserUserViewSet):
    """
    Custom user view set to handle user activation, password reset, and email/username management.
    """
    @swagger_auto_schema(request_body=VerifyOtpSerializer, operation_description="A endpoint to verify the OTP sent to the user's email")
    @action(["post"], detail=False)
    def activation(self, request, *args, **kwargs):
        print("Activation endpoint called")  # Initial debug print
        serializer = VerifyOtpSerializer(data=request.data)
        if serializer.is_valid():
            print("Serializer is valid")  # Debug print
            otp = serializer.validated_data['otp']
            email = serializer.validated_data['email']
            # Debugging print statement
            print(f"Received OTP: {otp}, Email: {email}")
            try:
                otp_obj = Otp.objects.select_related('user').get(email=email)
                print(f"OTP Object: {otp_obj}")  # Debugging print statement
                if otp_obj.otp == otp:
                    if otp_obj.expires_at and otp_obj.expires_at < timezone.now():
                        return Response({'status': 'error', 'message': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
                    user_account = otp_obj.user
                    user_account.is_active = True
                    user_account.save()
                    otp_obj.delete()
                    return Response({'status': 'success', 'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'status': 'error', 'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            except Otp.DoesNotExist:
                print("OTP not found")  # Debugging print statement
                return Response({'status': 'error', 'message': 'OTP not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            print("Serializer errors:", serializer.errors)  # Debug print
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=ResetEmailPasswordSerializer, operation_description="Resend activation email with OTP")
    @action(detail=False, methods=['post'], permission_classes=[AllowAny], authentication_classes=[CustomTokenAuthentication])
    def resend_activation(self, request, *args, **kwargs):
        serializer = ResetEmailPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = UserAccount.objects.get(email=email)
                if user.is_active:
                    return Response({'status': 'error', 'message': 'Account is already active'}, status=status.HTTP_400_BAD_REQUEST)

                # Generate OTP
                otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                
                # Save OTP
                Otp.objects.update_or_create(
                    user=user,
                    defaults={
                        'email': email,
                        'otp': otp_code,
                        'expires_at': timezone.now() + timezone.timedelta(minutes=settings.OTP_EXPIRATION_TIME)
                    }
                )

                # Prepare email
                html_message = render_to_string('activation_otp.html', {
                    'otp': otp_code
                })
                plain_message = strip_tags(html_message)
                
                # Send email
                send_mail(
                    subject='Activate Your ExploreDen Account',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=html_message
                )

                return Response({'status': 'success', 'message': 'Activation email sent'}, status=status.HTTP_200_OK)

            except UserAccount.DoesNotExist:
                return Response({'status': 'error', 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=ResetEmailPasswordSerializer, operation_description="An endpoint to initiate the password reset process by sending an OTP to the user's email")
    @action(["post"], detail=False)
    def reset_password(self, request, *args, **kwargs):
        serializer = ResetEmailPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user_account = UserAccount.objects.get(email=email)
                otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

                # Save OTP
                Otp.objects.update_or_create(
                    user=user_account,
                    defaults={
                        'email': email,
                        'otp': otp,
                        'expires_at': timezone.now() + timezone.timedelta(minutes=settings.OTP_EXPIRATION_TIME)
                    }
                )

                # Prepare email
                html_message = render_to_string('password_reset_otp.html', {
                    'otp': otp,
                    'expiry_minutes': settings.OTP_EXPIRATION_TIME
                })
                plain_message = strip_tags(html_message)

                # Send email
                send_mail(
                    subject='Reset Your ExploreDen Password',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=html_message
                )

                return Response({'status': 'success', 'message': 'OTP sent to your email'}, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({'status': 'error', 'message': 'Failed to send OTP email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=ResetPasswordConfirmSerializer, operation_description="An endpoint to confirm the password reset process by verifying the OTP sent to the user's email")
    @action(["post"], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        if serializer.is_valid():
            otp = serializer.validated_data['otp']
            email = serializer.validated_data['email']
            new_password = serializer.validated_data['new_password']
            try:
                otp_obj = Otp.objects.select_related('user').get(email=email)
                if otp_obj.otp == otp:
                    if otp_obj.expires_at and otp_obj.expires_at < timezone.now():
                        return Response({'status': 'error', 'message': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
                    user_account = otp_obj.user
                    user_account.set_password(new_password)
                    user_account.save()
                    otp_obj.delete()
                    return Response({'status': 'success', 'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'status': 'error', 'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            except Otp.DoesNotExist:
                return Response({'status': 'error', 'message': 'OTP not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(auto_schema=None)
    @action(detail=False, methods=['post'])
    def reset_username_confirm(self, request, *args, **kwargs):
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    @swagger_auto_schema(responses={status.HTTP_204_NO_CONTENT: 'DELETED'})
    def destroy(self, request, *args, **kwargs):
        user = request.user
        if user == request.user:
            self.perform_destroy(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(auto_schema=None)
    @action(detail=False, methods=['post'])
    def reset_username(self, request, *args, **kwargs):
        return Response(status=status.HTTP_403_FORBIDDEN)

    @swagger_auto_schema(auto_schema=None)
    @action(["post"], detail=False)
    def set_username(self, request, *args, **kwargs):
        return Response(status=status.HTTP_403_FORBIDDEN)

    @swagger_auto_schema(request_body=SetEmailSerializer, operation_description="An endpoint to set the user's email")
    @action(["post"], detail=False, permission_classes=[IsAuthenticated])
    def set_email(self, request, *args, **kwargs):
        serializer = SetEmailSerializer(data=request.data)
        if serializer.is_valid():
            new_email = serializer.validated_data['new_email']
            password = serializer.validated_data['password']
            user = request.user
            if user.check_password(password):
                user.email = new_email
                user.save()
                return Response({'status': 'success', 'message': 'Email set successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'error', 'message': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(["get", "put", "patch", "delete"], detail=False,  authentication_classes=[CustomTokenAuthentication])
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            user = request.user
            serializer = self.get_serializer(user)
            data = serializer.data
            data['is_verified'] = user.is_active
            return Response(data)
        elif request.method == "PUT":
            return self.update(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)
        elif request.method == "DELETE":
            return self.destroy(request, *args, **kwargs)
    
    

User = get_user_model()


class GoogleOAuth2Login(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(methods=["post"], detail=False, permission_classes=[AllowAny])
    def activation(self, request):
        try:
            # Extract the authorization code from the request
            code = request.data.get("code")

            if not code:
                return Response({"error": "Authorization code is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Exchange authorization code for access token
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                'code': code,
                'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
                'redirect_uri': 'https://exploreden.com.au/oauth/google/callback',
                'grant_type': 'authorization_code',
            }

            token_response = requests.post(token_url, data=data)
            print(f"Token response status: {token_response.status_code}")  # Debug log
            print(f"Token response: {token_response.text}")  # Debug log
            token_response.raise_for_status()

            token_data = token_response.json()
        except Exception as e:
            print(f"Detailed error: {str(e)}")  # Debug log
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        access_token = token_data.get('access_token')

        if not access_token:
            return Response({"error": "Access token not found in response."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch user info using the access token
        user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        try:
            user_info_response = requests.get(
                user_info_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            user_info_response.raise_for_status()
            user_info = user_info_response.json()
        except requests.exceptions.HTTPError as err:
            return Response({"error": f"Failed to fetch user info: {err}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An unexpected error occurred while fetching user info."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user_email = user_info.get('email')
        username = user_email.split('@')[0]
        print(user_info)

        if not user_email:
            return Response({"error": "Email not available in user info."}, status=status.HTTP_400_BAD_REQUEST)

        # Create or retrieve the user
        user, created = User.objects.get_or_create(
            email=user_email,
            defaults={'username': username, 'is_active': True, 'source': 'google'}
        )
        user.is_active = True
        user.save()

        # Generate or retrieve the token for the user
        serializer = SocialTokenSerializer(data={"email": user_email})
        serializer.is_valid(raise_exception=True)
        token_data = serializer.save()

        return Response(token_data, status=status.HTTP_200_OK)
