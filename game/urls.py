from django.conf.urls import url

from . import views

app_name = "game"
urlpatterns = [
    url(r'^setup$', views.setup_game, name='setup'),
    url(r'^join$', views.join, name='join'),
    url(r'^join/(?P<pk>\d+)/$', views.join_game, name='join_game'),
    url(r'^delete/(?P<pk>\d+)/$', views.delete_game, name='delete'),
]