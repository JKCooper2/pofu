from django.conf.urls import url

from . import views

app_name = "game"
urlpatterns = [
    url(r'^invite$', views.new_invitation, name='invite'),
    url(r'^invitation/(?P<pk>\d+)/$', views.accept_invitation, name="view_invite")
]