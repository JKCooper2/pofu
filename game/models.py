from django.db import models
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

import random
import numpy as np

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
    card_face = models.IntegerField(default=2)  # 0 - down, 1 - up, 2 - unset
    round_end = models.BooleanField(default=True)
    order = models.CharField(max_length=40, blank=True)

    objects = GamesManager()

    def __str__(self):
        return "Game " + str(self.id)

    def start(self):
        all_players = self.player_set.all()

        for player in all_players:
            player.reset()

        self.deck.deal(all_players)

        self.turn = 0
        self.order = ','.join(map(str, list(range(len(all_players)))))
        self.save()

        first = all_players.get(position=0)
        first.turn = True
        first.save()

        self.start_round()

    def start_round(self):
        all_players = self.player_set.all()

        if not all([player.ready for player in all_players]):
            print("Not all players ready to start next round")
            return

        # Reset turns
        self.card_face = 2
        self.round_end = False
        self.save()

    def poll(self, user):
        all_players = self.player_set.all()

        player = all_players.get(user=user)
        player_html = render_to_string('game/player_snippet.html', {'player': player})

        other_players = all_players.exclude(user=user)
        other_html = [(p.user.username, render_to_string('game/other_player_snippet.html', {'player': p})) for p in
                      other_players]

        return {'self': player_html,
                'players': other_html}

    def end_round(self):
        all_players = self.player_set.all()

        # Flip cards if necessary
        for player in all_players:
            player.action.face_up = True
            player.action.save()
            player.ready = False    # Used to trigger next round deal
            player.save()

        # Determine winner
        best_score = 0
        best_player = None

        for player in all_players:
            score = player.hand_score()

            print("FIRST PLAY:", player.position, self.order.split(',')[0], self.card_face)

            if player.position == int(self.order.split(',')[0]) and self.card_face == 1:
                print(player.user.username, " GETS BONUS")
                score += 2

            if score > best_score:
                best_score = score
                best_player = player

        # Add points
        points = sum([player.hand_points() for player in all_players])
        best_player.points += points
        best_player.turn = True  # Round winner starts next hand
        best_player.save()

        # Display button to move to next round
        self.card_face = 2
        self.round_end = True

        order0 = list(range(len(all_players)))
        order1 = order0[best_player.position:] + order0[:best_player.position]

        self.order = ','.join(map(str, list(order1)))
        self.save()

    def next_turn(self):
        self.turn += 1

        # Set face-up so other players in the round must follow play
        if self.card_face == 2:
            self.card_face = int(self.player_set.get(position=0).action.face_up)

        if self.turn >= self.player_set.count():
            self.turn = 0
            self.end_round()

        else:
            next_player = self.player_set.get(position=self.order.split(',')[self.turn])
            next_player.turn = True
            next_player.save()

        self.save()


class Player(models.Model):
    game = models.ForeignKey('game.Game')
    user = models.ForeignKey(User)
    points = models.IntegerField(default=0)
    position = models.IntegerField()
    turn = models.BooleanField(default=False)
    action = models.OneToOneField('game.Action', null=True, blank=True)
    error = models.CharField(max_length=100, default="")
    face_up = models.BooleanField(default=False)
    ready = models.BooleanField(default=False)

    def save(self, **kwargs):
        super(Player, self).save(**kwargs)

        if not hasattr(self, 'hand'):
            hand = Hand(player=self)
            hand.save()

    def reset(self):
        self.points = 0
        self.turn = False
        self.error = ""
        self.ready = True
        self.save()

    def __str__(self):
        return str(self.game) + " - " + self.user.username

    def set_ready(self):
        self.ready = True
        self.save()
        self.game.start_round()

    def cards_left(self):
        return self.hand.cards.count() + self.hand.selected.count()

    def cards_in_hand(self):
        return [card.short() for card in self.hand.cards.all()]

    def selected_cards(self):
        return [card.short() for card in self.hand.selected.all()]

    def last_action(self):
        return [card.short() for card in self.action.cards.all()]

    def has_error(self):
        return len(self.error) > 0

    def played_cards(self):
        if self.action.face_up:
            return [card.short() for card in self.action.cards.all()]
        else:
            return [card.back() for card in self.action.cards.all()]

    def snippet_html(self):
        player_html = render_to_string('game/player_snippet.html', {'player': self})
        return {'self': player_html}

    def select_face(self, face):
        self.face_up = face == "up"
        self.save()

    def select(self, card_string):
        card_details = card_string.split()
        card = {'rank': card_details[0], 'suit': card_details[1]}

        self.hand.select(card)

    def deselect(self, card_string):
        card_details = card_string.split()
        card = {'rank': card_details[0], 'suit': card_details[1]}

        self.hand.deselect(card)

    def submit_action(self, face):
        if not self.turn:
            return

        face_up = face == "up" if face is not None else bool(self.game.card_face)

        action = Action(face_up=face_up)
        action.save()
        action.cards.add(*self.hand.selected.all())
        action.save()

        self.error = action.validate()

        if not self.has_error():
            self.action = action
            self.hand.selected.clear()
            self.turn = False   # Used to ensure DB commit is done in time before redisplay
            self.save()

            self.game.next_turn()

    def hand_score(self):
        rank = self.action.cards.all()[0].rank
        if rank == 'A':
            rank = 1
        elif rank == 'J':
            rank = 11
        elif rank == 'Q':
            rank = 12
        elif rank == 'K':
            rank = 13

        return self.action.cards.count() * 13 - 13 + int(rank)

    def hand_points(self):
        rank = self.action.cards.all()[0].rank

        if rank in ['J', 'Q', 'K']:
            return self.action.cards.count() * 2

        else:
            return self.action.cards.count()


class Action(models.Model):
    face_up = models.BooleanField(default=True)
    cards = models.ManyToManyField(Card)

    def validate(self):
        if self.cards.count() <= 0:
            return "Need to selected at least 1 card to play"

        ranks = [c.rank for c in self.cards.all()]
        if len(set(ranks)) != 1:
            return "All cards must be of the same rank"

        return ""


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
