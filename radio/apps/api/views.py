from apps.programmes.models import Programme
from rest_framework import viewsets
from rest_framework.response import Response
import serializers


class ProgrammeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Programme.objects.all()
    serializer_class = serializers.ProgrammeSerializer


class ScheduleViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response([])
