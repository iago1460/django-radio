# Radioco - Broadcasting Radio Recording Scheduling system.
# Copyright (C) 2014  Iago Veloso Abalo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _


# Not necessary in Django > 1.7
# admin.autodiscover()
admin.site.logout_template = 'home/logged_out.html'
# admin.site.login_form = 'home/login.html'
admin.site.site_header = _('RadioCo administration')
admin.site.site_title = _('RadioCo site admin')
# admin.site.index_title = _('Site administration')



def handler400(request):
    response = render_to_response('home/400.html', {}, context_instance=RequestContext(request))
    response.status_code = 400
    return response

def handler404(request):
    response = render_to_response('home/404.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response

def handler403(request):
    response = render_to_response('home/403.html', {}, context_instance=RequestContext(request))
    response.status_code = 403
    return response

def handler500(request):
    response = render_to_response('home/500.html', {}, context_instance=RequestContext(request))
    response.status_code = 500
    return response


urlpatterns = patterns('',
    url(r'^$', 'radio.libs.home.views.index'),
    url(r'^login/$', 'radio.libs.home.views.user_login', name="login"),
    url(r'^logout/$', 'radio.libs.home.views.user_logout', name="logout"),
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^configuration/schedule_editor/', 'radio.apps.dashboard.views.full_calendar', name="schedule_editor"),
    url(r'^schedules/', include('radio.apps.schedules.urls', namespace="schedules")),
    url(r'^dashboard/', include('radio.apps.dashboard.urls', namespace="dashboard")),
    url(r'^programmes/', include('radio.apps.programmes.urls', namespace="programmes")),
    url(r'^users/', include('radio.apps.users.urls', namespace="users")),

    url(r'^ckeditor/', include('ckeditor.urls')),

    url(r'^api/1/recording_schedules/$', 'radio.libs.home.views.recording_schedules', name="recording_schedules"),
    url(r'^api/1/submit_recorder/$', 'radio.libs.home.views.submit_recorder', name="submit_recorder"),
)

# Media
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""
from django.utils.translation import activate
activate('es')
"""
