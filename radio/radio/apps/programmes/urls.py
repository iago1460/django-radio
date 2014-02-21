from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView

from radio.apps.programmes import views
from radio.apps.programmes.models import Programme


urlpatterns = patterns('',
    url(r'^$',
        ListView.as_view(
            queryset=Programme.objects.order_by('-name'),
            template_name='programmes/programme_list.html'),
        name='list'),
    url(r'^(?P<slug>[-\w]+)/$', views.programme_detail, name='detail'),
    url(r'^(?P<slug>[-\w]+)/(?P<id>\d+)/$', views.episode_detail, name='episode_detail')
)
