from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class GamesManager(models.Manager):
    def games_for_user(self, user):
        return super(GamesManager, self).get_queryset().filter(
            models.Q(player__user_id=user.id))


GAME_STATUS = (
    ('A', 'Active'),
    ('F', 'Finished'),
    ('C', 'Cancelled')
)


class Game(models.Model):
    status = models.CharField(max_length=1, default='A', choices=GAME_STATUS)
    title = models.CharField(max_length=50)

    host = models.ForeignKey(User, null=True)

    objects = GamesManager()

    def __str__(self):
        return "Game " + str(self.id)


class Setup(models.Model):
    num_players = models.IntegerField(verbose_name="Number of Players",
                                      help_text="2-8 players",
                                      validators=[MinValueValidator(2, message="Must have at least 2 players"),
                                                  MaxValueValidator(8, message="Cannot have more than 8 players")])
    host = models.ForeignKey(User, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=300, blank=True)

    def joined(self):
        return self.invitation_set.count()

    def __str__(self):
        return "Setup " + str(self.id)


class Player(models.Model):
    game = models.ForeignKey(Game)
    user = models.ForeignKey(User)

    def __str__(self):
        return str(self.game) + " - " + self.user.username


class Invitation(models.Model):
    setup = models.ForeignKey(Setup, null=True)
    to_user = models.ForeignKey(User, null=True)

    def __str__(self):
        return str(self.setup) + ": " + self.to_user.username
