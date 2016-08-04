from django.db import models
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

import random

from cards.models import Deck, Hand, Card


class GamesManager(models.Manager):
    def games_for_user(self, user):
        return super(GamesManager, self).get_queryset().filter(
            models.Q(player__user_id=user.id))

    @staticmethod
    def create_game(setup):
        game = Game(host=setup.host)
        game.save()

        invites = setup.invitation_set.all()

        shuffle_order = list(range(len(invites)))
        random.shuffle(shuffle_order)

        for i, invite in enumerate(invites):
            player = Player(game=game, user=invite.user, position=shuffle_order[i])
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
    host = models.ForeignKey(User)
    deck = Deck()
    turn = models.IntegerField(default=0)

    objects = GamesManager()

    def __str__(self):
        return "Game " + str(self.id)

    def start(self):
        all_players = self.player_set.all()
        self.deck.deal(all_players)

        first = all_players.get(position=0)
        first.turn = True
        first.save()

        player = all_players.get(user=self.host)
        player_html = render_to_string('game/player_snippet.html', {'player': player})

        other_players = all_players.exclude(user=self.host)
        other_html = [(p.user.username, render_to_string('game/other_player_snippet.html', {'player': p})) for p in other_players]

        return {'self': player_html,
                'players': other_html}

    def end_round(self):
        print("END OF THE ROUND")

    def next_turn(self):
        if self.turn >= self.player_set.count():
            self.end_round()
            return

        current_player = self.player_set.get(position=self.turn)
        next_player = self.player_set.get(position=self.turn+1)

        current_player.turn = False
        next_player.turn = True


class Player(models.Model):
    game = models.ForeignKey('game.Game')
    user = models.ForeignKey(User)
    points = models.IntegerField(default=0)
    position = models.IntegerField()
    turn = models.BooleanField(default=False)
    action = models.OneToOneField('game.Action', null=True)

    def save(self, **kwargs):
        super(Player, self).save(**kwargs)

        if not hasattr(self, 'hand'):
            hand = Hand(player=self)
            hand.save()

    def __str__(self):
        return str(self.game) + " - " + self.user.username

    def cards_left(self):
        return self.hand.cards.count()

    def cards_in_hand(self):
        return [card.short() for card in self.hand.cards.all()]

    def selected_cards(self):
        return [card.short() for card in self.hand.selected.all()]

    def snippet_html(self):
        player_html = render_to_string('game/player_snippet.html', {'player': self})
        return {'self': player_html}

    def select(self, card_string):
        card_details = card_string.split()
        card = {'rank': card_details[0], 'suit': card_details[1]}

        self.hand.select(card)

    def deselect(self, card_string):
        card_details = card_string.split()
        card = {'rank': card_details[0], 'suit': card_details[1]}

        self.hand.deselect(card)

    def submit_action(self, face):
        face_up = face == "up"

        action = Action(face_up=face_up)
        action.save()
        action.cards.add(*self.hand.selected.all())

        self.action = action

        if self.action.is_valid():
            self.game.next_turn()


class Action(models.Model):
    face_up = models.BooleanField(default=True)
    cards = models.ManyToManyField(Card)
    error = models.CharField(max_length=100, default="")

    def has_error(self):
        return len(self.error) > 0

    def is_valid(self):
        if self.cards.count() <= 0:
            self.error = "Need to selected at least 1 card to play"
            return False

        ranks = [c.rank for c in self.cards.all()]
        if len(set(ranks)) != 1:
            self.error = "All cards must be of the same rank"
            return False

        self.error = ""
        return True


class SetupManager(models.Manager):
    def setups_for_user(self, user):
        return super(SetupManager, self).get_queryset().filter(
            models.Q(invitation__user_id=user.id))


class Setup(models.Model):
    num_players = models.IntegerField(verbose_name="Number of Players",
                                      help_text="2-8 players",
                                      validators=[MinValueValidator(2, message="Must have at least 2 players"),
                                                  MaxValueValidator(8, message="Cannot have more than 8 players")])
    host = models.ForeignKey(User)
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
    setup = models.ForeignKey('game.Setup', null=True)
    user = models.ForeignKey(User)

    def __str__(self):
        return str(self.setup) + ": " + self.user.username
