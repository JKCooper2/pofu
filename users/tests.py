import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client

from game.models import Setup, Invitation


def add_setup(user):
    setup = Setup(host=user,
                  num_players=4,
                  timestamp=datetime.datetime.now(),
                  message="Test Game")
    setup.save()
    invite = Invitation(setup=setup, user=user)
    invite.save()


class UserViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('test', 'test@pofu.net', 'testpass')

    def test_home_unregistered_user(self):
        """Users home page should redirect to login unregistered user"""
        response = self.client.get(reverse('users:home'))
        self.assertEqual(response.status_code, 302)

    def test_home_registered_user(self):
        """Users home page should load for a registered user"""
        self.client.login(username='test', password='testpass')
        response = self.client.get(reverse('users:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('my_games' in response.context)
        self.assertTrue('joining' in response.context)
        self.assertTrue('hosting' in response.context)

    def test_home_with_setup(self):
        """Games user has setup should display on home page"""
        self.client.login(username='test', password='testpass')
        add_setup(self.user)
        response = self.client.get(reverse('users:home'))

        hosting = response.context['hosting']
        self.assertEqual(len(hosting), 1)
        self.assertEqual(hosting[0].message, "Test Game")
        self.assertEqual(hosting[0].joined(), 1)
        self.assertEqual(hosting[0].host, self.user)

        joining = response.context['joining']
        self.assertEqual(len(joining), 1)
        self.assertEqual(joining[0].message, "Test Game")




