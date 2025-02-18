from django.test import TestCase
from authapp.models import UserAccount
from authapp.serializers import UserCreateSerializer

class TestUserCreateSerializer(TestCase):
    def test_email_duplicate(self):
        user = UserAccount.objects.create_user(email="existing@example.com", username="existinguser", password="testpass")
        self.assertIsNotNone(user.pk, "UserAccount instance should be created")

        data = {
            'email': user.email,
            'username': 'testuser',
            'password': 'testpassword'
        }
        serializer = UserCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid(), "Serializer should be invalid due to duplicate email")
        self.assertIn('email', serializer.errors, "Errors should contain 'email'")
        self.assertEqual(serializer.errors['email'][0], 'user account with this email already exists.', "Should raise error if email already exists")
    
    def test_create_user(self):
        data = {
            'email': 'hello@gmail.com',
            'username': 'testuser',
            'password': 'testpassword'
        }
        serializer = UserCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), "Serializer should be valid")
        user = serializer.save()
        self.assertIsNotNone(user.pk, "UserAccount instance should be created")
        self.assertEqual(user.email, data['email'], "Email should be the same")
        self.assertEqual(user.username, data['username'], "Username should be the same")
        self.assertTrue(user.check_password(data['password']), "Password should be set correctly")