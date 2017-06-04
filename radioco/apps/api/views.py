import datetime

import django_filters
import pytz
from django import forms
from django import utils
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.timezone import override
from recurrence import Recurrence
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import list_route
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response

import serializers
from radioco.apps.api.viewsets import UpdateOnlyModelViewSet
from radioco.apps.programmes.models import Programme, Episode
from radioco.apps.schedules.models import Schedule, Transmission


class ProgrammeFilter(filters.FilterSet):
    class Meta:
        model = Programme
        fields = ('name', 'category')


class ProgrammeFilterForm(forms.Form):
    after = forms.DateField(required=False)
    before = forms.DateField(required=False)

    def clean(self):
        cleaned_data = super(ProgrammeFilterForm, self).clean()
        if cleaned_data.get('before') and cleaned_data.get('after'):
            if cleaned_data['after'] > cleaned_data['before']:
                raise ValidationError('after date has to be greater or equals than before date.')
        return cleaned_data


class ProgrammeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Programme.objects.all()
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = ProgrammeFilter
    serializer_class = serializers.ProgrammeSerializer
    lookup_field = 'slug'

    def list(self, request, *args, **kwargs):
        data = ProgrammeFilterForm(request.query_params)
        if not data.is_valid():
            raise DRFValidationError(data.errors)

        after = data.cleaned_data['after']
        before = data.cleaned_data['before']

        # Apply filters to the queryset
        programmes = self.filter_queryset(self.get_queryset())
        if after:
            programmes = programmes.filter(Q(end_date__gte=after) | Q(end_date__isnull=True))
        if before:
            programmes = programmes.filter(Q(start_date__lte=before) | Q(start_date__isnull=True))

        serializer = self.get_serializer(programmes, many=True)
        return Response(serializer.data)


class EpisodeFilter(filters.FilterSet):
    class Meta:
        model = Episode
        fields = ('programme',)

    programme = django_filters.CharFilter(name="programme__slug")


class EpisodeViewSet(viewsets.ReadOnlyModelViewSet):  # FIXME: allowing creation breaks the view
    queryset = Episode.objects.all()
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = EpisodeFilter
    serializer_class = serializers.EpisodeSerializer


class ScheduleFilter(filters.FilterSet):
    class Meta:
        model = Schedule
        fields = ('programme', 'calendar', 'type')

    programme = django_filters.CharFilter(name="programme__slug")


class ScheduleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Schedule.objects.all()
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = ScheduleFilter
    serializer_class = serializers.ScheduleSerializer


class TransmissionForm(forms.Form):
    after = forms.DateField()
    before = forms.DateField()
    calendar = forms.CharField(required=False)
    timezone = forms.ChoiceField(required=False, choices=[(x, x) for x in pytz.all_timezones])

    def clean(self):
        cleaned_data = super(TransmissionForm, self).clean()
        if cleaned_data.get('before') and cleaned_data.get('after'):
            if cleaned_data['after'] > cleaned_data['before']:
                raise ValidationError('after date has to be greater or equals than before date.')
        return cleaned_data

    def clean_timezone(self):
        timezone = self.cleaned_data.get('timezone')
        if timezone:
            return pytz.timezone(timezone)
        return timezone


class TransmissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Schedule.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)  # Transmissions are always order by date
    filter_class = ScheduleFilter
    serializer_class = serializers.TransmissionSerializer

    def list(self, request, *args, **kwargs):
        data = TransmissionForm(request.query_params)
        if not data.is_valid():
            raise DRFValidationError(data.errors)
        requested_timezone = data.cleaned_data.get('timezone')

        after = data.cleaned_data['after']
        before = data.cleaned_data['before']

        tz = requested_timezone or pytz.utc
        after_date = tz.localize(datetime.datetime.combine(after, datetime.time()))
        before_date = tz.localize(datetime.datetime.combine(before, datetime.time(23, 59, 59)))

        # Apply filters to the queryset
        schedules = self.filter_queryset(self.get_queryset())
        # Filter by active calendar if that filter was not provided
        if not data.cleaned_data.get('calendar'):
            schedules = schedules.filter(calendar__is_active=True)

        transmissions = Transmission.between(
            after_date,
            before_date,
            schedules=schedules
        )
        serializer = self.get_serializer(transmissions, many=True)
        with override(timezone=tz):
            return Response(serializer.data)

    @list_route()
    def now(self, request):
        tz = None or pytz.utc  # TODO check for a tz?
        now = utils.timezone.now()
        transmissions = Transmission.at(now)
        serializer = self.get_serializer(transmissions, many=True)
        with override(timezone=tz):
            return Response(serializer.data)


class TransmissionOperationViewSet(UpdateOnlyModelViewSet):
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    serializer_class = serializers.TransmissionSerializerLight
    queryset = Schedule.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response('ok')

    def perform_update(self, serializer):
        schedule = serializer.instance
        start = serializer.validated_data['start']
        new_start = serializer.validated_data['new_start']
        if start == new_start:
            return

        schedule_excluded = Schedule.get_schedule_which_excluded_dt(schedule.programme, new_start)
        if schedule_excluded:
            # Including the date that was excluded
            schedule_excluded.include_date(new_start)
            schedule_excluded.save()

            if schedule.id == schedule_excluded.id:
                # Case when a transmission is moved from one day to other but is still part of the same schedule
                # The object is the same, using schedule_excluded to avoid overriding changes!
                schedule_excluded.exclude_date(start)
                schedule_excluded.save()
            elif schedule.has_recurrences():
                # The schedule has other recurrences excluding only that date (it could be deleted)
                schedule.exclude_date(start)
                schedule.save()
            else:
                # Case when the previous schedule is not necessary
                schedule.delete()
        else:
            if schedule.has_recurrences():
                schedule.exclude_date(start)
                schedule.save()
                new_schedule = Schedule.objects.get(id=schedule.id)
                new_schedule.id = new_schedule.pk = None
                new_schedule.from_collection = schedule
                new_schedule.recurrences = Recurrence()
                new_schedule.start_dt = new_start
                new_schedule.save()
            else:
                schedule.start_dt = new_start
                schedule.save()
