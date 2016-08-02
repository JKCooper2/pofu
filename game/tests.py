import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from .models import Setup, Invitation


def create_setup():
    host = User.objects.create_user(username="test1", email="1@test.com", password="test1")
    setup = Setup(host=host, num_players=4, timestamp=datetime.datetime.now())
    invite = Invitation(setup=setup, user=host)

