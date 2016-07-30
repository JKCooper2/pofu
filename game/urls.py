from django.conf.urls import url

from . import views

app_name = "game"
urlpatterns = [
    url(r'^setup$', views.setup_game, name='setup'),
    url(r'^join$', views.join_game, name='join'),
]