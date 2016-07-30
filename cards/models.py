from django.db import models

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
    image = models.FileField(blank=True)

    def __str__(self):
        return self.get_rank_display() + " of " + self.get_suit_display()


class Deck(models.Model):
    cards = Card.objects.all()

