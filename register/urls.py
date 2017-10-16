from django.conf.urls import url
from . import views
from django.contrib.auth.views import login, logout
# from .forms import LoginForm

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^register_save/$', views.register_save, name='register_save'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^profile_save/$', views.profile_save, name='profile_save'),
    url(r'^login/$', login,
        {'template_name': 'register/login.html'},
        name='login'),
    # TODO: logoutの時にadminの画面になる
    url(r'^logout/$', logout, name='logout'),
    url(r'^plan/$', views.plan, name='plan'),
    url(r'^site_add/$', views.site_add, name='site_add'),
    url(r'^site_add/(?P<site_id>\d+)/$', views.site_add, name='site_edit'),
    url(r'^article_add/(?P<site_id>\d+)/$', views.article_add, name='article_add'),
    url(r'^article_add/(?P<site_id>\d+)/(?P<article_id>\d+)/$', views.article_add, name='article_edit'),
    url(r'^site_del/(?P<site_id>\d+)/$', views.site_del, name='site_del'),
    url(r'^article_del/(?P<site_id>\d+)/(?P<article_id>\d+)/$', views.article_del, name='article_del'),
]
