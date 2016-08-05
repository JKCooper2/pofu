from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import Setup, Invitation, Game
from .forms import SetupGameForm


@login_required
def setup_game(request):
    if request.method == 'POST':
        setup = Setup(host=request.user)
        form = SetupGameForm(data=request.POST, instance=setup)

        if form.is_valid():
            setup = form.save()

            invite = Invitation(setup=setup, user=request.user)
            invite.save()

            return redirect('users:home')

    else:
        form = SetupGameForm()

    return render(request, 'game/setup_game.html', {'form': form})


@login_required
def delete_game(request, pk):
    setup = get_object_or_404(Setup, pk=pk)

    if setup.host == request.user:
        setup.delete()

    else:
        raise PermissionDenied

    return redirect('users:home')


@login_required
def join(request):
    games = Setup.objects.all()
    games = games.exclude(host=request.user)
    context = {'games': games}
    return render(request, 'game/join_game.html', context)


@login_required
def join_game(request, pk):
    setup = get_object_or_404(Setup, pk=pk)

    if request.user not in [inv.user for inv in setup.invitation_set.all()]:
        invite = Invitation(setup=setup, user=request.user)
        invite.save()

    if setup.complete():
        setup.create_game()

    return redirect('users:home')


@login_required
def leave_game(request, pk):
    setup = get_object_or_404(Setup, pk=pk)

    if request.user == setup.host:
        return HttpResponseForbidden("You can't remove yourself from a game you are hosting")

    invite = setup.invitation_set.filter(user=request.user)
    invite.delete()

    return redirect('users:home')


@login_required
def display(request, pk):
    game = get_object_or_404(Game, pk=pk)
    all_players = game.player_set.all()

    player = all_players.get(user=request.user)
    other_players = all_players.exclude(user=request.user)

    context = {'game': game,
               'player': player,
               'other_players': other_players}
    return render(request, 'game/display.html', context)


@login_required
def start(request, pk):
    game = get_object_or_404(Game, pk=pk)

    if game.host != request.user:
        raise PermissionDenied

    game.start()
    response = game.poll(request.user)

    return JsonResponse(response)


@login_required
def select(request, pk):
    game = get_object_or_404(Game, pk=pk)
    player = game.player_set.get(user=request.user)

    if request.method == 'POST':
        card = request.POST['card']
        player.select(card)

    return JsonResponse(player.snippet_html())


@login_required
def deselect(request, pk):
    game = get_object_or_404(Game, pk=pk)
    player = game.player_set.get(user=request.user)

    if request.method == 'POST':
        card = request.POST['card']
        player.deselect(card)

    return JsonResponse(player.snippet_html())


@login_required
def poll(request, pk):
    game = get_object_or_404(Game, pk=pk)
    response = game.poll(request.user)

    return JsonResponse(response)


@login_required
def submit(request, pk):
    game = get_object_or_404(Game, pk=pk)
    player = game.player_set.get(user=request.user)

    if request.method == 'POST':
        post = request.POST
        face = post['face'] if 'face' in post else None
        player.submit_action(face)

    return JsonResponse(player.snippet_html())


@login_required
def face(request, pk):
    game = get_object_or_404(Game, pk=pk)
    player = game.player_set.get(user=request.user)

    if request.method == 'POST':
        post = request.POST
        face = post['face'] if 'face' in post else None
        player.select_face(face)

    return JsonResponse(player.snippet_html())


@login_required
def ready(request, pk):
    game = get_object_or_404(Game, pk=pk)
    player = game.player_set.get(user=request.user)

    if request.method == 'POST':
        player.set_ready()

    return JsonResponse(player.snippet_html())

