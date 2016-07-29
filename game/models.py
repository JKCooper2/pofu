from django.db import models
from django.contrib.auth.models import User


class GamesManager(models.Manager):
    def games_for_user(self, user):
        return super(GamesManager, self).get_queryset().filter(
            models.Q(player__user_id=user.id))


class Game(models.Model):
    status = models.CharField(max_length=1, default='A', choices=[('A', 'Active'), ('I', 'Inactive')])
    title = models.CharField(max_length=50)

    objects = GamesManager()

    def __str__(self):
        return "Game " + str(self.id)


class Player(models.Model):
    game = models.ForeignKey(Game)
    user = models.ForeignKey(User)

    def __str__(self):
        return str(self.game) + " - " + self.user.username


class Invitation(models.Model):
    from_user = models.ForeignKey(User, related_name='invitations_sent')
    to_user = models.ForeignKey(User, related_name='invitations_received',
                                verbose_name="User to invite",
                                help_text="Please select the user you want to play a game against")
    message = models.CharField(max_length=300, blank=True,
                               help_text="Adding a friendly message is never a bad idea")
    timestamp = models.DateTimeField(auto_now_add=True)
