from rest_framework.test import APITestCase
from rest_framework import status
from authapp.models import UserAccount, Otp


class TestAuthAPI(APITestCase):
    def setUp(self):
        self.signup_url = '/auth/users/'
        self.login_url = '/auth/token/login/'
        self.logout_url = '/auth/token/logout/'
        self.user_data_url = '/auth/users/me/'
        self.update_user_data_url = '/auth/users/me/'
        self.delete_user_data_url = '/auth/users/me/'
        self.change_password_url = '/auth/users/set_password/'
        self.reset_password_url = '/auth/users/reset_password/'
        self.reset_password_confirm_url = '/auth/users/reset_password_confirm/'
        self.set_email_url = '/auth/users/set_email/'
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword"
        }
        self.change_password_data = {
            "new_password": "Hello123456",
            "current_password": self.user_data["password"]
        }

    def test_signup(self):
        response = self.client.post(
            self.signup_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_signup_with_existing_email(self):
        UserAccount.objects.create_user(**self.user_data)
        response = self.client.post(
            self.signup_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('email'), [
                         'user account with this email already exists.'])

    def test_login_without_activation(self):
        UserAccount.objects.create_user(**self.user_data)
        login_data = {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_activation(self):
        user = UserAccount.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        login_data = {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('auth_token', response.data)

    def test_login_with_wrong_password(self):
        user = UserAccount.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        login_data = {
            "email": self.user_data['email'],
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('non_field_errors'), [
                         'Unable to log in with provided credentials.'])

    def test_logout(self):
        user = UserAccount.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        login_data = {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }
        login_response = self.client.post(
            self.login_url, login_data, format='json')
        token = login_response.data.get('auth_token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_user_data_without_token(self):
        response = self.client.get(self.user_data_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_data_with_token(self):
        user = UserAccount.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        login_data = {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }
        login_response = self.client.post(
            self.login_url, login_data, format='json')
        token = login_response.data.get('auth_token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.get(self.user_data_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user_data_without_token(self):
        user = UserAccount.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        response = self.client.put(
            self.update_user_data_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_data_with_token(self):
        user = UserAccount.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        login_data = {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }
        login_response = self.client.post(
            self.login_url, login_data, format='json')
        token = login_response.data.get('auth_token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.put(
            self.update_user_data_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user_data_without_token(self):
        user = UserAccount.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        response = self.client.delete(self.delete_user_data_url, data={
                                      "current_password": self.user_data['password']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user_data_with_token(self):
        user = UserAccount.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        login_data = {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }
        login_response = self.client.post(
            self.login_url, login_data, format='json')
        token = login_response.data.get('auth_token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        response = self.client.delete(self.delete_user_data_url, data={
                                      "current_password": self.user_data['password']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_change_password_without_token(self):
        user = UserAccount.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        response = self.client.post(
            self.change_password_url,
            {"new_password": "Hello123456",
                "current_password": self.user_data["password"]},
            format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_with_token(self):
        user = UserAccount.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        login_data = {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }
        login_response = self.client.post(
            self.login_url, login_data, format='json')
        token = login_response.data.get('auth_token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.post(
            self.change_password_url,
            {"new_password": "Hello123456",
                "current_password": self.user_data["password"]},
            format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_reset_password_view(self):
        user = UserAccount.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        data = {
            "email": self.user_data['email']
        }
        response = self.client.post(
            self.reset_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'OTP sent to your email')

    def test_reset_password_confirm_view(self):
        user = UserAccount.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        otp_obj = Otp.objects.get(user=user)
        data = {
            "email": self.user_data['email'],
            "otp": otp_obj.otp,
            "new_password": "Hello123456"
        }
        response = self.client.post(
            self.reset_password_confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'],
                         'Password reset successfully')

    def test_set_email_view(self):
        user = UserAccount.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        login_data = {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }
        login_response = self.client.post(
            self.login_url, login_data, format='json')
        token = login_response.data.get('auth_token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        data = {
            "password": self.user_data['password'],
            "new_email": "user@example.com"
        }
        response = self.client.post(self.set_email_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'Email set successfully')
