from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from game.models import Game, Setup


@login_required
def home(request):
    my_games = Game.objects.games_for_user(request.user)
    joining = Setup.objects.setups_for_user(request.user)
    hosting = Setup.objects.filter(host=request.user)
    context = {'my_games': my_games,
               'joining': joining,
               'hosting': hosting}
    return render(request, 'users/home.html', context)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return redirect('users:home')

    else:
        form = UserCreationForm()

    return render(request, 'users/register.html', {'form': form})