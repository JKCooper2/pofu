from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

from cards.models import Deck, Hand


class GamesManager(models.Manager):
    def games_for_user(self, user):
        return super(GamesManager, self).get_queryset().filter(
            models.Q(player__user_id=user.id))

    @staticmethod
    def create_game(setup):
        game = Game(host=setup.host)
        game.save()

        for invite in setup.invitation_set.all():
            player = Player(game=game, user=invite.user)
            player.save()

        setup.delete()

        return game


GAME_STATUS = (
    ('A', 'Active'),
    ('F', 'Finished'),
    ('C', 'Cancelled')
)


class Game(models.Model):
    status = models.CharField(max_length=1, default='A', choices=GAME_STATUS)
    title = models.CharField(max_length=50, blank=True)
    deck = Deck()
    host = models.ForeignKey(User, null=True)

    objects = GamesManager()

    def __str__(self):
        return "Game " + str(self.id)


class Player(models.Model):
    game = models.ForeignKey(Game)
    user = models.ForeignKey(User)
    points = models.IntegerField(default=0)
    hand = models.ForeignKey(Hand, null=True)

    def __str__(self):
        return str(self.game) + " - " + self.user.username

    def cards_left(self):
        return self.hand.cards.count()

    def cards(self):
        return [card.short() for card in self.hand.cards.all()]


class SetupManager(models.Manager):
    def setups_for_user(self, user):
        return super(SetupManager, self).get_queryset().filter(
            models.Q(invitation__user_id=user.id))


class Setup(models.Model):
    num_players = models.IntegerField(verbose_name="Number of Players",
                                      help_text="2-8 players",
                                      validators=[MinValueValidator(2, message="Must have at least 2 players"),
                                                  MaxValueValidator(8, message="Cannot have more than 8 players")])
    host = models.ForeignKey(User, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=300, blank=True)

    objects = SetupManager()

    def joined(self):
        return self.invitation_set.count()

    def complete(self):
        return self.joined() == self.num_players

    def create_game(self):
        GamesManager.create_game(setup=self)

    def __str__(self):
        return "Setup " + str(self.id)


class Invitation(models.Model):
    setup = models.ForeignKey(Setup, null=True)
    user = models.ForeignKey(User, null=True)

    def __str__(self):
        return str(self.setup) + ": " + self.user.username
