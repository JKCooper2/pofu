from django.db import models
import random

SUITS = (
    ('H', 'Hearts'),
    ('D', 'Diamonds'),
    ('C', 'Clubs'),
    ('S', 'Spades')
)

RANKS = (
    ('A', 'Ace'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
    ('J', 'Jack'),
    ('Q', 'Queen'),
    ('K', 'King'),

)


class Card(models.Model):
    suit = models.CharField(max_length=1, choices=SUITS)
    rank = models.CharField(max_length=2, choices=RANKS)

    def image_path(self):
        return str(self.get_rank_display()).lower() + "_of_" + str(self.get_suit_display()).lower() + ".png"

    def short(self):
        return self.rank, self.suit, self.image_path()

    def __str__(self):
        return self.get_rank_display() + " of " + self.get_suit_display()


class Deck(models.Model):
    cards = Card.objects.all()

    def deal(self, players):
        for player in players:
            player.hand.cards.clear()

        shuffle_order = list(range(len(self.cards)))
        random.shuffle(shuffle_order)

        for i in range(len(self.cards)):
            players[i % len(players)].hand.cards.add(self.cards[shuffle_order[i]])


class Hand(models.Model):
    cards = models.ManyToManyField('cards.Card', related_name="cards")
    player = models.OneToOneField('game.Player')
    selected = models.ManyToManyField('cards.Card', related_name="selected")

    def contains_card(self, card):
        return self.cards.filter(suit=card['suit'], rank=card['rank']).count() == 1

    def select(self, card):
        if not self.contains_card(card):
            return

        c = self.cards.get(suit=card['suit'], rank=card['rank'])
        self.selected.add(c)
        self.cards.remove(c)

    def is_card_in_hand(self, card):
        return self.selected.filter(suit=card['suit'], rank=card['rank']).count() == 1

    def deselect(self, card):
        if not self.is_card_in_hand(card):
            return

        c = self.selected.get(suit=card['suit'], rank=card['rank'])
        self.cards.add(c)
        self.selected.remove(c)

    def __str__(self):
        return "Hand " + str(self.id)