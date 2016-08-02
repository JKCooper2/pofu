from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client

from .models import Setup, Invitation, Game, Player
from .forms import SetupGameForm


def create_game(client):
    client.login(username='test', password='testpass')
    client.post(reverse('game:setup'), {'num_players': 2, 'message': "Test Game"})
    client.logout()
    client.login(username='test2', password='test2pass')
    client.get(reverse('game:join_game', kwargs={'pk': 1}))


class GameViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('test', 'test@pofu.net', 'testpass')
        self.player = User.objects.create_user('test2', 'test2@pofu.net', 'test2pass')
        self.client.login(username='test', password='testpass')

    def test_view_setup_game(self):
        """game/setup displays setup form"""
        response = self.client.get(reverse('game:setup'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

        form = response.context['form']
        self.assertEqual(len(form.fields), 2)

    def test_form_validation_errors(self):
        """Check Form validation errors"""
        form = SetupGameForm(data={'num_players': 2, 'message': "Test"})
        self.assertTrue(form.is_valid())

        form = SetupGameForm(data={'num_players': 8, 'message': ""})
        self.assertTrue(form.is_valid())

        form = SetupGameForm(data={'num_players': 1, 'message': "Test"})
        self.assertFalse(form.is_valid())

        form = SetupGameForm(data={'num_players': 9, 'message': "Test"})
        self.assertFalse(form.is_valid())

    def test_form_validation_display(self):
        """Test error display is correct"""
        response = self.client.post(reverse('game:setup'), {'num_players': 1, 'message': "Test"})
        self.assertFormError(response, 'form', 'num_players', "Must have at least 2 players")

        response = self.client.post(reverse('game:setup'), {'num_players': 9, 'message': "Test"})
        self.assertFormError(response, 'form', 'num_players', "Cannot have more than 8 players")

    def test_setup_created(self):
        """Test valid form submit creates a valid Setup"""
        self.client.post(reverse('game:setup'), {'num_players': 2, 'message': "Test Game"})
        setup = Setup.objects.get(pk=1)
        self.assertEqual(setup.host, self.user)
        self.assertEqual(setup.message, "Test Game")
        self.assertEqual(setup.num_players, 2)
        self.assertEqual(setup.joined(), 1)
        self.assertFalse(setup.complete())

    def test_setup_games_show_in_hosted(self):
        """Setup Games display on user/home"""
        self.client.post(reverse('game:setup'), {'num_players': 2, 'message': "Test Game"})
        response = self.client.get(reverse('users:home'))

        hosting = response.context['hosting']
        self.assertEqual(len(hosting), 1)
        self.assertEqual(hosting[0].joined(), 1)
        self.assertFalse(hosting[0].complete())
        self.assertTrue(self.user in [i.user for i in hosting[0].invitation_set.all()])

    def test_join_game_shows_available_setups(self):
        """Other players can see games available to join on Join Games page"""
        self.client.post(reverse('game:setup'), {'num_players': 2, 'message': "Test Game"})
        self.client.logout()
        self.client.login(username='test2', password='test2pass')
        response = self.client.get(reverse('game:join'))

        self.assertTrue('games' in response.context)

        games = response.context['games']
        self.assertEqual(len(games), 1)
        self.assertEqual(games[0].message, "Test Game")
        self.assertEqual(games[0].num_players, 2)
        self.assertEqual(games[0].host, self.user)
        self.assertEqual(games[0].joined(), 1)

    def test_not_last_person_to_join_setup(self):
        """Test joined games display on users home page"""
        self.client.post(reverse('game:setup'), {'num_players': 3, 'message': "Test Game"})
        self.client.logout()
        self.client.login(username='test2', password='test2pass')

        self.client.get(reverse('game:join_game', kwargs={'pk': 1}))

        response = self.client.get(reverse('users:home'))
        self.assertTrue('joining' in response.context)

        self.assertEqual(len(Setup.objects.all()), 1)
        self.assertEqual(len(Invitation.objects.all()), 2)

        joining = response.context['joining']
        self.assertEqual(len(joining), 1)
        self.assertEqual(joining[0].joined(), 2)
        self.assertFalse(joining[0].complete())
        self.assertTrue(self.player in [i.user for i in joining[0].invitation_set.all()])

    def test_last_person_to_join_setup_creates_game(self):
        """Final person to join game has game in Games and not Joining"""
        self.client.post(reverse('game:setup'), {'num_players': 2, 'message': "Test Game"})
        self.client.logout()
        self.client.login(username='test2', password='test2pass')

        self.client.get(reverse('game:join_game', kwargs={'pk': 1}))

        response = self.client.get(reverse('users:home'))

        joining = response.context['joining']
        self.assertEqual(len(joining), 0)

        self.assertEqual(len(Setup.objects.all()), 0)
        self.assertEqual(len(Invitation.objects.all()), 0)
        self.assertEqual(len(Game.objects.all()), 1)
        self.assertEqual(len(Player.objects.all()), 2)

        games = response.context['my_games']
        self.assertEqual(len(games), 1)
        self.assertEqual(games[0].host, self.user)
        self.assertEqual(games[0].status, 'A')
        self.assertEqual(games[0].turn, 0)
        self.assertEqual(games[0].player_set.count(), 2)
        self.assertTrue(self.player in [p.user for p in games[0].player_set.all()])
        self.assertTrue(self.user in [p.user for p in games[0].player_set.all()])

    def test_joining_game_that_doesnt_exist(self):
        """Joining game that doesn't exist throws 404"""
        response = self.client.get(reverse('game:join_game', kwargs={'pk': 1}))
        self.assertTrue(response.status_code, 404)
