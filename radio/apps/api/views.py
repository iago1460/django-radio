from apps.programmes.models import Programme
from apps.schedules.models import Schedule, Transmission
from django import utils
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
import datetime
import serializers


class ProgrammeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Programme.objects.all()
    serializer_class = serializers.ProgrammeSerializer


class ScheduleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Schedule.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('programme', 'schedule_board', 'type')
    serializer_class = serializers.ScheduleSerializer


class TransmissionViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        now = utils.timezone.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0)
        transmissions = Transmission.between(
            now, now+datetime.timedelta(days=31))
        serializer = serializers.TransmissionSerializer(
            transmissions, many=True)
        return Response(serializer.data)

    @list_route()
    def now(self, request):
        now = utils.timezone.now()
        transmissions = Transmission.at(now)
        serializer = serializers.TransmissionSerializer(
            transmissions, many=True)
        return Response(serializer.data)
