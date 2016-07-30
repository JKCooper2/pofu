from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import Setup, Invitation
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
    context = {'games': games}
    return render(request, 'game/join_game.html', context)


@login_required
def join_game(request, pk):
    setup = get_object_or_404(Setup, pk=pk)

    if request.user not in [inv.user for inv in setup.invitation_set.all()]:
        invite = Invitation(setup=setup, user=request.user)
        invite.save()

    return redirect('users:home')
