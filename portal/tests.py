from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class PortalSmokeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='student', email='student@example.com', password='TestPass123!')

    def test_homepage_renders(self):
        response = self.client.get(reverse('portal:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Regional Scholarship Application Portal')

    def test_registration_honeypot_blocks_spam(self):
        response = self.client.post(reverse('portal:register'), {
            'username': 'botuser',
            'email': 'bot@example.com',
            'password1': 'BotPass123!',
            'password2': 'BotPass123!',
            'region': 'North',
            'honeypot': 'spam',
        })
        self.assertFormError(response, 'form', 'honeypot', 'Spam detected.')
