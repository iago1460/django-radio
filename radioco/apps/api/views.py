import pytz
from django.utils.timezone import override, get_default_timezone, get_default_timezone_name
from recurrence import Recurrence

from radioco.apps.radio.tz_utils import convert_date_to_datetime, get_timezone_offset, transform_datetime_tz, \
    transform_dt_checking_dst
from radioco.apps.api.viewsets import ModelViewSetWithoutCreate
from radioco.apps.programmes.models import Programme, Episode
from radioco.apps.schedules.models import ScheduleBoard, Schedule, Transmission
from django import forms
from django import utils
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import list_route
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.response import Response
import datetime
import django_filters
import serializers


class ProgrammeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Programme.objects.all()
    serializer_class = serializers.ProgrammeSerializer
    lookup_field = 'slug'


class EpisodeFilter(filters.FilterSet):
    class Meta:
        model = Episode
        fields = ('programme',)

    programme = django_filters.CharFilter(name="programme__slug")


class EpisodeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Episode.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = EpisodeFilter
    serializer_class = serializers.EpisodeSerializer


class ScheduleFilter(filters.FilterSet):
    class Meta:
        model = Schedule
        fields = ('programme', 'schedule_board', 'type')

    programme = django_filters.CharFilter(name="programme__slug")


class ScheduleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Schedule.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ScheduleFilter
    serializer_class = serializers.ScheduleSerializer


class TransmissionForm(forms.Form):
    after = forms.DateField(required=False)
    before = forms.DateField(required=False)
    schedule_board = forms.CharField(required=False)
    timezone = forms.ChoiceField(choices=[(x, x) for x in pytz.all_timezones])

    def clean_after(self):
        after = self.cleaned_data.get('after')
        if after is None:
            return utils.timezone.now().replace(day=1).date()
        return after

    def clean_before(self):
        # XXX raise if before < after
        before = self.cleaned_data.get('before')
        if before is None:
            return self.clean_after() + datetime.timedelta(days=31)
        return before

    def clean_timezone(self):
        timezone = self.cleaned_data.get('timezone')
        return pytz.timezone(timezone)


class TransmissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Schedule.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ScheduleFilter
    serializer_class = serializers.TransmissionSerializer

    def list(self, request, *args, **kwargs):
        data = TransmissionForm(request.query_params)
        data.is_valid()
        requested_timezone = data.cleaned_data.get('timezone')

        # if requested_timezone:
        #     timezone_without_dst = get_timezone_offset(requested_timezone) # forced timezone
        # else:
        #     timezone_without_dst = get_timezone_offset(get_default_timezone())



        # with override(timezone=timezone_without_dst):
        # after_date = convert_date_to_datetime(data.cleaned_data.get('after'))
        # before_date = convert_date_to_datetime(data.cleaned_data.get('before'), time=datetime.time(23, 59, 59))

        tz = timezone.get_current_timezone()  # Timezone in current use
        after_date = transform_dt_checking_dst(
            tz.localize(datetime.datetime.combine(data.cleaned_data.get('after'), datetime.time()))
        )
        before_date = transform_dt_checking_dst(
            tz.localize(datetime.datetime.combine(data.cleaned_data.get('before'), datetime.time(23, 59, 59)))
        )


        # TODO:
        # after_date created ignored DST!  00:00:00+01:00   ???
        # before_date created ignored DST!  23:59:59+01:00  ???

        transmissions = Transmission.between(
            after_date,
            before_date,
            schedules=self.filter_queryset(self.get_queryset()) #FIXME self.get_queryset()? is this filtering start_date end_date ?
        )

        # with override(timezone=get_default_timezone()):
        #     schedule_1 = Schedule()
        #     schedule_1.id = 6
        #     date_1 = convert_date_to_datetime(
        #         datetime.date(2016, 8, 2), time=datetime.time(23, 50, 0),
        #         tz =  get_default_timezone()
        #     )
        #     date_2 = pytz.UTC.localize(datetime.datetime.combine(datetime.date(2016, 8, 4), time=datetime.time(23, 50, 0)))
        #     date_3 = get_default_timezone().normalize(
        #         (date_2 + datetime.timedelta(days=2)).astimezone(get_default_timezone())
        #     )
        #
        #     transmissions = [
        #         Transmission(schedule_1, date_1), Transmission(schedule_1, date_2),
        #         Transmission(schedule_1, date_3)
        #     ]

        serializer = self.serializer_class(transmissions, timezone=requested_timezone, many=True)
        return Response(serializer.data)

    @list_route()
    def now(self, request):
        now = utils.timezone.now()
        transmissions = Transmission.at(now)
        serializer = serializers.TransmissionSerializer(
            transmissions, many=True)
        return Response(serializer.data)


class TransmissionOperationViewSet(ModelViewSetWithoutCreate):
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
            schedule_excluded.include_date(new_start)
            schedule_excluded.save()

            if schedule.id == schedule_excluded.id:  # Fix to avoid override changes
                schedule_excluded.exclude_date(start)
                schedule_excluded.save()
            elif schedule.has_recurrences():
                schedule.exclude_date(start)
                schedule.save()
            else:
                schedule.delete()
        else:
            if schedule.has_recurrences():
                schedule.exclude_date(start)
                schedule.save()
                new_schedule = Schedule.objects.get(id=schedule.id)
                new_schedule.id = None
                new_schedule.from_collection = schedule
                new_schedule.recurrences = Recurrence()
                new_schedule.start_date = new_start
                new_schedule.save()
            else:
                schedule.start_date = new_start
                schedule.save()
