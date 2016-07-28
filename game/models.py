from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    status = models.CharField(max_length=1, default='A', choices=[('A', 'Active'), ('I', 'Inactive')])
    title = models.CharField(max_length=50)

    def __str__(self):
        return "Game " + str(self.id)


class Player(models.Model):
    game = models.ForeignKey(Game)
    user = models.ForeignKey(User)

    def __str__(self):
        return str(self.game) + " - " + self.user.username
