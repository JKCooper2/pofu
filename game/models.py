from django.db import models
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

import random

from cards.models import Deck, Hand, Card


class GamesManager(models.Manager):
    """
    GamesManager is used for performing queries over all game objects
    """
    def games_for_user(self, user):
        return super(GamesManager, self).get_queryset().filter(models.Q(player__user_id=user.id))

    @staticmethod
    def create_game(setup):
        """
        Creates a Game based on a Setup

        Parameters:
            setup - Complete Setup Instance
        """
        game = Game(host=setup.host)
        game.save()

        invites = setup.invitation_set.all()

        for invite in invites:
            player = Player(game=game, user=invite.user)
            player.save()

        setup.delete()


GAME_STATUS = (
    ('A', 'Active'),
    ('F', 'Finished'),
    ('C', 'Cancelled')
)


class Game(models.Model):
    """
    Game is responsible for managing the flow of play

    Fields:
        status - A: Active, F: Finished, C: Cancelled
        host - User hosting the game (grants privileges to this user)

        order - List of player positions in order of turn, e.g. [2, 3, 0, 1]
        turn - Holds the index of the current turn in the order. Current turn is player with position order[turn]
        card_face - Face the lead card was played. 0: down, 1: up, 2: unset

    Related Fields:
        player - Foreign Key from player to game
    """
    status = models.CharField(max_length=1, default='A', choices=GAME_STATUS)
    host = models.ForeignKey(User)

    order = models.CharField(max_length=40, blank=True)
    turn = models.IntegerField(default=0)
    card_face = models.IntegerField(default=2)

    objects = GamesManager()

    def __str__(self):
        return "Game " + str(self.id)

    def is_round_end(self):
        return self.turn >= self.player_set.count()

    def join_order(self, order, split=None):
        """
        Helper function for converting between lists and strings in order to store in DB
        :param order: List of values
        :param split: Index of start point (wraps around)
        :return: string of list joined by ','
        """
        order0 = list(range(len(order)))

        if split is None:
            self.order = ','.join(map(str, order0))

        else:
            order1 = order0[split:] + order0[:split]
            self.order = ','.join(map(str, list(order1)))

        self.save()

    def poll(self, user):
        """
        JS polls server every few seconds to check for updates to the game status
        Could add step to game and only return html if step > what is passed through
        Returned HTML currently only a few KB though

        Parameters:
            user - User instance

        Returns:
            Dictionary containing html of all players
        """
        all_players = self.player_set.all()

        player = all_players.get(user=user)
        player_html = render_to_string('game/player_snippet.html', {'player': player})

        other_players = all_players.exclude(user=user)
        other_html = [(p.user.username, render_to_string('game/other_player_snippet.html', {'player': p})) for p in
                      other_players]

        return {'self': player_html,
                'players': other_html}

    def start(self):
        """
        Starts a new game
        """
        all_players = self.player_set.all()

        # Shuffle positions
        positions = list(range(len(all_players)))
        random.shuffle(positions)

        for i, player in enumerate(all_players):
            turn = positions[i] == 0
            player.reset(position=positions[i], turn=turn)

        # Deal out cards
        Deck().deal(all_players)

        # Store turn order used [0, 1, 2, 3, 4, 5]
        self.join_order(all_players)

        self.turn = 0
        self.save()

        self.start_round()

    def start_round(self):
        """
        Checks if all players are ready and if so starts the game round
        by setting the turn to be 0
        """
        if not all([player.ready for player in self.player_set.all()]):
            return

        # Reset turns
        self.card_face = 2
        self.turn = 0
        self.save()

    def next_turn(self):
        """
        Decides whether to end the round or to update the currently active player
        """
        self.turn += 1
        self.save()

        if self.is_round_end():
            self.end_round()
            return

        # Set face-up based on first player so other players in the round must follow play
        if self.card_face == 2:
            self.card_face = int(self.player_set.get(position=0).action.face_up)
            self.save()

        # Set next players turn to be active
        self.player_set.get(position=self.order.split(',')[self.turn]).set_turn(True)

    def score_bonus(self, player):
        # Bonus of 2 points if first player plays face up
        if player.position == self.order.split(',')[0] and self.card_face == 1:
            return 2

        return 0

    def find_round_winner(self, players):
        """
        Returns Player with best cards for that round
        """
        best_score = 0
        best_player = None

        for player in players:
            player.end_round()
            score = player.hand_score() + self.score_bonus(player)

            # Score has to beat current best in order to win
            if score > best_score:
                best_score = score
                best_player = player

        return best_player

    def end_round(self):
        """
        Scores the round, gives points to winner, alters order
        """
        all_players = self.player_set.all()

        round_winner = self.find_round_winner(all_players)

        # Give winner points
        points = sum([player.hand_points() for player in all_players])
        round_winner.won_round(points)

        # Alter order so round winner goes first
        self.join_order(all_players, round_winner.position)
        self.card_face = 2
        self.save()


class Player(models.Model):
    game = models.ForeignKey('game.Game')
    user = models.ForeignKey(User)
    points = models.IntegerField(default=0)
    position = models.IntegerField(default=0)
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

    def reset(self, position=None, turn=False):
        self.points = 0
        self.turn = turn
        self.error = ""
        self.ready = True

        if position is not None:
            self.position = position

        self.save()

    def __str__(self):
        return str(self.game) + " - " + self.user.username

    def set_ready(self):
        self.ready = True
        self.save()
        self.game.start_round()

    def set_turn(self, turn):
        self.turn = turn
        self.save()

    def end_round(self):
        if not self.action.face_up:
            self.action.face_up = True
            self.action.save()

        self.ready = False  # Used to trigger next round deal
        self.save()

    def won_round(self, points):
        self.points += points
        self.turn = True  # Round winner starts next hand
        self.save()

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
