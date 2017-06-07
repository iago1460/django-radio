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
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.utils.translation import ugettext_lazy as _
from django.views.i18n import javascript_catalog
from filebrowser.sites import site

admin.site.logout_template = 'radioco/logged_out.html'
admin.site.site_header = _('RadioCo administration')
admin.site.site_title = _('RadioCo site admin')


### templates not implemented, led to strange exceptions when running tests.
# def handler400(request):
#    response = render_to_response('radioco/400.html', {}, context_instance=RequestContext(request))
#    response.status_code = 400
#    return response
#
#
# def handler404(request):
#    response = render_to_response('radioco/404.html', {}, context_instance=RequestContext(request))
#    response.status_code = 404
#    return response
#
#
# def handler403(request):
#    response = render_to_response('radioco/403.html', {}, context_instance=RequestContext(request))
#    response.status_code = 403
#    return response
#
#
# def handler500(request):
#    response = render_to_response('radioco/500.html', {}, context_instance=RequestContext(request))
#    response.status_code = 500
#    return response

js_info_dict = {
    'packages': ('recurrence',),
}

urlpatterns = [
    url(r'^$', 'radioco.apps.radioco.views.index', name="home"),
    url(r'^jsi18n/$', javascript_catalog, js_info_dict, name='javascript-catalog'),
    url(r'^logout/$', 'radioco.apps.radioco.views.user_logout', name="logout"),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/password_reset/$', auth_views.password_reset, name='admin_password_reset'),
    url(r'^admin/password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),

    # url(r'^configuration/schedule_editor/', 'radioco.apps.dashboard.views.full_calendar', name="schedule_editor"),
    url(r'^schedules/', include('radioco.apps.schedules.urls', namespace="schedules")),
    url(r'^programmes/', include('radioco.apps.programmes.urls', namespace="programmes")),
    url(r'^users/', include('radioco.apps.users.urls', namespace="users")),

    url(r'^ckeditor/', include('ckeditor_uploader.urls')),

    url(r'^api/1/recording_schedules/$', 'radioco.apps.api.recorder_views.recording_schedules', name="recording_schedules"),
    url(r'^api/1/submit_recorder/$', 'radioco.apps.api.recorder_views.submit_recorder', name="submit_recorder"),

    url(r'^api/2/', include('radioco.apps.api.urls', namespace="api"))
]

if (settings.TESTING_MODE or settings.DEBUG) and 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]

# Media
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Static
urlpatterns += staticfiles_urlpatterns()
