from apps.programmes.models import Programme
from rest_framework import viewsets
import serializers


class ProgrammeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Programme.objects.all()
    serializer_class = serializers.ProgrammeSerializer
