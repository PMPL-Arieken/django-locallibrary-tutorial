from django.contrib.auth.models import User
from django.test import TestCase
from django.urls.base import reverse

# Create your tests here.


class RegisterViewTest(TestCase):

    def setUp(self):
        self.email = 'email@example.com'
        self.password = 'P@ssw0rd'
        self.url_path = reverse('register')

    def test_register_view_valid(self):
        response = self.client.get(self.url_path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Member Registration')

    def test_register_form_valid(self):
        response = self.client.post(
            self.url_path, {
                'email': self.email,
                'password': self.password,
                'password2': self.password,
            })

        user = User.objects.get(username=self.email)
        self.assertEqual(user.email, self.email)
        self.assertEqual(response.status_code, 302)

    def test_register_form_password_not_equals(self):
        response = self.client.post(
            self.url_path, {
                'email': self.email,
                'password': self.password,
                'password2': self.password + 'x',
            })

        count = User.objects.filter(username=self.email).count()
        self.assertEqual(count, 0)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwords must be equal')
        
    def test_register_form_user_already_exists(self):
        user = User.objects.create_user(
            username=self.email,
            email=self.email,
            password=self.password)
        user.save()

        response = self.client.post(
            self.url_path, {
                'email': self.email,
                'password': self.password,
                'password2': self.password,
            })

        count = User.objects.filter(username=self.email).count()
        self.assertEqual(count, 1)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User already exists')
