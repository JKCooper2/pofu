from django.forms import ModelForm
from .models import Setup


class SetupGameForm(ModelForm):
    class Meta:
        model = Setup
        fields = ['num_players', 'message']
