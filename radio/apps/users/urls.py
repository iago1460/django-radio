from django.conf.urls import patterns, url

from radio.apps.users import views


urlpatterns = patterns('',
    url(r'^$', views.UsersView.as_view(), name='list'),
    url(r'^(?P<slug>[-\w]+)/$', views.UserProfileDetailView.as_view(), name='detail'),
)
