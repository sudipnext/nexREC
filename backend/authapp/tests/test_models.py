from django.test import TestCase
from authapp.models import UserAccount

class TestUserAccount(TestCase):
    def test_user_creation(self):
        user = UserAccount.objects.create_user(email="hello@gmail.com", username="hello", password="testpassword")
        self.assertEqual(user.pk, 1, "Should create a User instance")
        self.assertFalse(user.is_active, "Default value for is_active should be False")
        self.assertFalse(user.is_staff, "Default value for is_staff should be False")
        self.assertFalse(user.is_superuser, "Default value for is_superuser should be False")
        self.assertEqual(user.email, "hello@gmail.com", "User should have an email")
        self.assertEqual(user.username, "hello", "User should have a username")
        self.assertIsNotNone(user.date_joined, "User should have a date_joined")

    def test_set_password(self):
        user = UserAccount.objects.create_user(email="test@example.com", username="testuser", password="oldpassword")
        user.set_password('new_password')
        self.assertTrue(user.check_password('new_password'), "Password should be set correctly")

    def test_create_superuser(self):
        user = UserAccount.objects.create_superuser(
            email='superuser@test.com',
            password='superpassword',
            username='superuser'
        )
        self.assertTrue(user.is_staff, "Superuser should have is_staff=True")
        self.assertTrue(user.is_superuser, "Superuser should have is_superuser=True")
        self.assertTrue(user.check_password('superpassword'), "Superuser password should be set correctly")

    def test_user_creation_without_email(self):
        with self.assertRaises(ValueError) as context:
            UserAccount.objects.create_user(email=None, password='password', username='test')
        self.assertEqual(str(context.exception), "The Email field must be set", "Should raise a ValueError")

    def test_create_superuser_is_staff_false(self):
        with self.assertRaises(ValueError) as context:
            UserAccount.objects.create_superuser(
                is_staff=False,
                username='superuser',
                email='hello@gmail.com',
                password='superpassword'
            )
        self.assertEqual(str(context.exception), "Superuser must have is_staff=True.", "Should raise a ValueError")

    def test_create_superuser_is_superuser_false(self):
        with self.assertRaises(ValueError) as context:
            UserAccount.objects.create_superuser(
                is_superuser=False,
                username='superuser',
                password='superpassword',
                email='hello@gmail.com',
            )
        self.assertEqual(str(context.exception), "Superuser must have is_superuser=True.", "Should raise a ValueError")