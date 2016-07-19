from recurrence import Recurrence

from radioco.apps.api.viewsets import ModelViewSetWithoutCreate
from radioco.apps.programmes.models import Programme, Episode
from radioco.apps.schedules.models import ScheduleBoard, Schedule, Transmission
from django import forms
from django import utils
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

    schedule_board = django_filters.CharFilter(name="schedule_board__slug")
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


class TransmissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Schedule.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ScheduleFilter
    serializer_class = serializers.TransmissionSerializer

    def list(self, request, *args, **kwargs):
        data = TransmissionForm(request.query_params)
        data.is_valid()

        transmissions = Transmission.between(
            datetime.datetime.combine(data.cleaned_data.get('after'), datetime.time(0)),
            datetime.datetime.combine(data.cleaned_data.get('before'), datetime.time(23, 59, 59)),
            schedules=self.filter_queryset(self.get_queryset())
        )
        serializer = self.serializer_class(transmissions, many=True)
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

        schedule_excluded = schedule.date_is_excluded(new_start)
        if schedule_excluded:
            schedule_excluded.include_date(new_start)
            schedule_excluded.save()

            if schedule.has_recurrences():
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
            else:
                new_schedule = schedule

            new_schedule.start_date = new_start
            new_schedule.recurrences = Recurrence()
            new_schedule.from_collection = schedule
            new_schedule.save()
