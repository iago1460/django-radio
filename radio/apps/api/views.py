from apps.programmes.models import Programme
from apps.schedules.models import Schedule
from rest_framework import permissions, viewsets
import serializers


class ProgrammeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Programme.objects.all()
    serializer_class = serializers.ProgrammeSerializer


class ScheduleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Schedule.objects.all()
    serializer_class = serializers.ScheduleSerializer
