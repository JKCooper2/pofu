from django.conf.urls import url

from . import views

app_name = "users"
urlpatterns = [
    url(r'^home$', views.home, name='home'),
    url(r'^register$', views.register, name='register'),
]