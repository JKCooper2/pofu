from django.conf.urls import url

from . import views

app_name = "game"
urlpatterns = [
    url(r'^setup$', views.setup_game, name='setup'),
    url(r'^join$', views.join, name='join'),
    url(r'^join/(?P<pk>\d+)/$', views.join_game, name='join_game'),
    url(r'^delete/(?P<pk>\d+)/$', views.delete_game, name='delete'),
    url(r'^leave/(?P<pk>\d+)/$', views.leave_game, name='leave'),
    url(r'^display/(?P<pk>\d+)/$', views.display, name='display'),
    url(r'^start/(?P<pk>\d+)/$', views.start, name='start'),
    url(r'^poll/(?P<pk>\d+)/$', views.poll, name='poll'),
    url(r'^update/(?P<pk>\d+)/select/$', views.select, name='select'),
    url(r'^update/(?P<pk>\d+)/deselect/$', views.deselect, name='deselect'),
    url(r'^update/(?P<pk>\d+)/submit/$', views.submit, name='submit'),
]
