from django.conf.urls import url
from . import views
from django.contrib.auth.views import login,logout
# from .forms import LoginForm

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^check/$', views.check, name='check'),
]
