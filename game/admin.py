from django.contrib import admin

from .models import Game, Player


class PlayerInline(admin.StackedInline):
    model = Player
    extra = 2


class GameAdmin(admin.ModelAdmin):
    inlines = [PlayerInline]

admin.site.register(Game, GameAdmin)
