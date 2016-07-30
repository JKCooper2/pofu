from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from game.models import Game


@login_required
def home(request):
    my_games = Game.objects.games_for_user(request.user)
    context = {'my_games': my_games}
    return render(request, 'users/home.html', context)
