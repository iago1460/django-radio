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


# XXX this code was missed to review, assume there are several bugs. REVIEW!
# Delete me when done!


from dateutil.relativedelta import relativedelta
from django import forms
from django.contrib import admin
from django.forms import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from radioco.apps.programmes.models import Programme, Podcast, Episode, Role, Participant
from radioco.apps.schedules.models import Calendar


# PROGRAMME
from radioco.apps.schedules.utils import next_dates


class NonStaffRoleInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            self.instance = kwargs['instance']
        if 'person_object' in kwargs:
            self.person = kwargs.pop('person_object')
        super(NonStaffRoleInlineForm, self).__init__(*args, **kwargs)

    def clean(self):
        '''
        Check unique together: person, role, programme
        '''
        cleaned_data = super(NonStaffRoleInlineForm, self).clean()
        if 'person' in cleaned_data:
            person = cleaned_data['person']
        else:
            person = self.person
        role = cleaned_data['role']
        programme = cleaned_data['programme']
        qs = Role.objects.filter(role=role, programme=programme, person=person)
        if self.instance.id:
            qs = qs.exclude(pk=self.instance.id)
        if qs.count() > 0:
            raise ValidationError(_('This user has already a role in this programme.'))
        return cleaned_data


class NonStaffRoleInlineFormset(forms.models.BaseInlineFormSet):
    def _construct_form(self, i, **kwargs):
        kwargs['person_object'] = self.person
        return super(NonStaffRoleInlineFormset, self)._construct_form(i, **kwargs)


class NonStaffRoleInline(admin.StackedInline):
    model = Role
    extra = 0
    form = NonStaffRoleInlineForm
    formset = NonStaffRoleInlineFormset
    list_select_related = True

    def get_formset(self, request, obj=None, **kwargs):
        kwargs['fields'] = ['person', 'role', 'description']
        if not request.user.has_perm('programmes.see_all_roles'):
            self.exclude = ['person']
        else:
            self.exclude = []
        formset = super(NonStaffRoleInline, self).get_formset(request, obj, **kwargs)
        formset.person = request.user
        return formset

    def get_queryset(self, request):
        qs = super(NonStaffRoleInline, self).get_queryset(request).select_related('programme', 'person')
        if not request.user.has_perm('programmes.see_all_roles'):
            qs = qs.filter(person=request.user)
        return qs


class NonStaffProgrammeAdmin(admin.ModelAdmin):
    list_display = ('name', '_runtime', 'current_season', 'category', 'start_date', 'end_date')
    search_fields = ['name']
    list_filter = ['_runtime', 'category']
    inlines = [NonStaffRoleInline]

    def get_prepopulated_fields(self, request, obj=None):
        if request.user.has_perm('programmes.add_programme'):
            self.prepopulated_fields = {"slug": ("name",)}  # FIXME: DJANGO BUG?
            return self.prepopulated_fields
        return {}

    def get_fieldsets(self, request, obj=None):
        if request.user.has_perm('programmes.add_programme'):
            return (
                (None, {
                    'fields': ('name', 'slug', 'synopsis', 'category', 'current_season', 'photo', 'language', '_runtime')
                }),
                (_('Advanced options'), {
                    'fields': ('start_date', 'end_date'),
                }),
            )
        else:
            return (
                (None, {
                    'fields': ('name', 'synopsis', 'category', 'current_season', 'photo', 'language')
                }),
            )

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            # if no person field is displayed
            if not instance.pk and not request.user.has_perm('programmes.see_all_roles'):
                instance.person = request.user
            instance.save()
        formset.save_m2m()

    def get_queryset(self, request):
        qs = super(NonStaffProgrammeAdmin, self).get_queryset(request)
        if not request.user.has_perm('programmes.see_all_programmes'):
            qs = qs.filter(announcers__in=[request.user]).distinct()
        return qs


# EPISODE
class NonStaffParticipantInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            self.instance = kwargs['instance']
        if 'person_object' in kwargs:
            self.person = kwargs.pop('person_object')
        super(NonStaffParticipantInlineForm, self).__init__(*args, **kwargs)

    def clean(self):
        if 'person' in self.cleaned_data:
            person = self.cleaned_data['person']
        else:
            person = self.person
        role = self.cleaned_data['role']
        episode = self.cleaned_data['episode']
        qs = Participant.objects.filter(role=role, episode=episode, person=person)
        if self.instance.id:
            qs = qs.exclude(pk=self.instance.id)
        if qs.count() > 0:
            raise ValidationError(_('This user has already a role in this episode.'))
        return super(NonStaffParticipantInlineForm, self).clean()


class NonStaffParticipantInlineFormset(forms.models.BaseInlineFormSet):
    def _construct_form(self, i, **kwargs):
        kwargs['person_object'] = self.person
        return super(NonStaffParticipantInlineFormset, self)._construct_form(i, **kwargs)


class NonStaffParticipantInline(admin.StackedInline):
    model = Participant
    extra = 0
    form = NonStaffParticipantInlineForm
    formset = NonStaffParticipantInlineFormset

    def get_formset(self, request, obj=None, **kwargs):

        kwargs['fields'] = ['person', 'role', 'description']
        if not request.user.has_perm('programmes.see_all_participants'):
            self.exclude = ['person']
        else:
            self.exclude = []
        formset = super(NonStaffParticipantInline, self).get_formset(request, obj, **kwargs)
        formset.person = request.user
        return formset

    def get_queryset(self, request):
        qs = super(NonStaffParticipantInline, self).get_queryset(request).select_related('episode__programme', 'person')
        if not request.user.has_perm('programmes.see_all_participants'):
            qs = qs.filter(person=request.user)
        return qs


class NonStaffEpisodeAdminForm(forms.ModelForm):
    class Meta:
        model = Episode
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(NonStaffEpisodeAdminForm, self).__init__(*args, **kwargs)

    def clean_programme(self):
        programme = self.cleaned_data['programme']
        now = timezone.now()
        if not self.instance.pk:
            last_episode = Episode.objects.last(programme)
            if last_episode:
                if last_episode.issue_date:
                    after = last_episode.issue_date + programme.runtime
                    if after < now:
                        after = now
                else:
                    raise forms.ValidationError(_('There are no available schedules.'))
            else:
                after = now

            try:
                next(next_dates(Calendar.get_active(), programme, after))
            except StopIteration:
                raise forms.ValidationError(_('There are no available schedules.'))
        return programme


class OwnEpisodeProgrammeListFilter(admin.SimpleListFilter):
    '''
    Check people in programmes besides episodes, better performance
    '''
    title = _('programmes')
    parameter_name = 'programme'

    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            return [(programme.id, programme.name) for programme in Programme.objects.all()]
        return [(programme.id, programme.name) for programme in Programme.objects.filter(announcers__in=[request.user]).distinct()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(programme__id=self.value())
        else:
            return queryset


class OwnEpisodeIssueDateListFilter(admin.SimpleListFilter):
    title = _('issue date')
    parameter_name = 'date'

    def lookups(self, request, model_admin):
        return (
            ('next', _('Next episodes')),
            ('untilnow', _('Until now')),
            ('lastweek', _('Last week')),
            ('twoweeks', _('Since two weeks ago')),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'next':
            return queryset.filter(issue_date__gte=now) | queryset.filter(issue_date__isnull=True)
        elif self.value() == 'lastweek':
            return queryset.filter(issue_date__gte=(now - relativedelta(days=7)), issue_date__lte=now)
        elif self.value() == 'twoweeks':
            return queryset.filter(issue_date__gte=(now - relativedelta(days=14)), issue_date__lte=now)
        elif self.value() == 'untilnow':
            return queryset.filter(issue_date__lte=now)
        else:
            return queryset


class PodcastInline(admin.StackedInline):
    inline_classes = ('grp-collapse grp-open',)
    extra = 0
    model = Podcast


class NonStaffEpisodeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'season', 'number_in_season', 'issue_date', 'programme')
    list_select_related = True
    ordering = ['-season', '-number_in_season']
    list_filter = ['issue_date', OwnEpisodeProgrammeListFilter, OwnEpisodeIssueDateListFilter]
    search_fields = ['programme__name']
    inlines = [NonStaffParticipantInline, PodcastInline]
    fields = ['programme', 'title', 'summary', 'issue_date', 'season', 'number_in_season']
    form = NonStaffEpisodeAdminForm

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            programme = obj.programme
            last_episode = Episode.objects.last(programme)
            now = timezone.now()
            if last_episode:
                after = last_episode.issue_date + programme.runtime
                if after < now:
                    after = now
            else:
                after = now
            date = next(next_dates(Calendar.get_active(), programme, after))
            Episode.objects.create_episode(
                episode=obj, last_episode=last_episode,
                date=date, programme=programme)
        else:
            obj.save()

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(NonStaffEpisodeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'programme':
            if request and not request.user.has_perm('programmes.see_all_episodes'):
                field.queryset = field.queryset.filter(announcers__in=[request.user]).distinct()
        return field

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['programme', 'issue_date', 'season', 'number_in_season']
        else:
            return ['issue_date', 'season', 'number_in_season']

    def save_formset(self, request, form, formset, change):
        # if formset.model != InlineModel:
        #   return super(NonStaffProgrammeAdmin, self).save_formset(request, form, formset, change)
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if not instance.pk and not request.user.has_perm('programmes.see_all_participants'):
                instance.person = request.user
            instance.save()
        formset.save_m2m()

    def get_queryset(self, request):
        qs = super(NonStaffEpisodeAdmin, self).get_queryset(request)
        if not request.user.has_perm('programmes.see_all_episodes'):
            qs = qs.filter(people__in=[request.user]).distinct()
        return qs


admin.site.register(Programme, NonStaffProgrammeAdmin)
admin.site.register(Episode, NonStaffEpisodeAdmin)
