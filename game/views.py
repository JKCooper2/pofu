from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponse

from .models import Invitation, Game
from .forms import InvitationForm


@login_required
def new_invitation(request):
    if request.method == 'POST':
        invitation = Invitation(from_user=request.user)
        form = InvitationForm(data=request.POST, instance=invitation)

        if form.is_valid():
            form.save()
            return redirect('users:home')

    else:
        form = InvitationForm()

    return render(request, 'game/new_invitation.html', {'form': form})


@login_required
def accept_invitation(request, pk):
    invitation = get_object_or_404(Invitation, pk=pk)

    if not request.user == invitation.to_user:
        raise PermissionDenied

    if request.method == 'POST':
        if 'accept' in request.POST:
            # game = Game.objects.new_game(invitation)
            # invitation.delete()
            # return redirect(game.get_absolute_url())

            invitation.delete()
            return HttpResponse("Accepted Invitation")
        else:
            invitation.delete()
            return redirect('users:home')

    else:
        return render(request, 'game/accept_invitation.html', {'invitation': invitation})