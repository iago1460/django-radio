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


from django.conf.urls import url, patterns
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from radio.libs.global_settings.models import SiteConfiguration, PodcastConfiguration, CalendarConfiguration


try:
    from django.utils.encoding import force_unicode
except ImportError:
    from django.utils.encoding import force_text as force_unicode


class SingletonModelAdmin(admin.ModelAdmin):
    object_history_template = "global_settings/admin_object_history.html"
    change_form_template = "global_settings/admin_change_form.html"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super(SingletonModelAdmin, self).get_urls()
        url_name_prefix = '%(app_name)s_%(model_name)s' % {
            'app_name': self.model._meta.app_label,
            'model_name': self.model._meta.model_name,
        }
        custom_urls = patterns('',
            url(r'^history/$',
                self.admin_site.admin_view(self.history_view),
                {'object_id': '1'},
                name='%s_history' % url_name_prefix),
            url(r'^$',
                self.admin_site.admin_view(self.change_view),
                {'object_id': '1'},
                name='%s_change' % url_name_prefix),
        )
        # By inserting the custom URLs first, we overwrite the standard URLs.
        return custom_urls + urls

    def response_change(self, request, obj):
        msg = _('%(obj)s was changed successfully.') % {'obj': force_unicode(obj)}
        if '_continue' in request.POST:
            self.message_user(request, msg)
            return HttpResponseRedirect(request.path)
        else:
            self.message_user(request, msg)
            return HttpResponseRedirect("../../")

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if object_id == '1':
            self.model.objects.get_or_create(pk=1)
        return super(SingletonModelAdmin, self).change_view(
            request,
            object_id,
            form_url,
            extra_context,
        )



class PodcastConfigurationAdmin(SingletonModelAdmin):
    readonly_fields = ['recorder_token']
    pass

admin.site.register(SiteConfiguration, SingletonModelAdmin)
admin.site.register(CalendarConfiguration, SingletonModelAdmin)
admin.site.register(PodcastConfiguration, PodcastConfigurationAdmin)
