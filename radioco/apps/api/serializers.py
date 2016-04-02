from radioco.apps.programmes.models import Programme
from radioco.apps.schedules.models import Schedule, ScheduleBoard, Transmission
from rest_framework import serializers
import datetime


class ProgrammeSerializer(serializers.ModelSerializer):
    runtime = serializers.DurationField()
    photo = serializers.URLField()

    class Meta:
        model = Programme
        fields = ('slug', 'name', 'synopsis', 'runtime', 'photo', 'language', 'category')


class ScheduleSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    programme = serializers.SlugRelatedField(
        slug_field='slug', queryset=Programme.objects.all())
    schedule_board = serializers.SlugRelatedField(
        slug_field='slug', queryset=ScheduleBoard.objects.all())
    # XXX this is a bit hacky...
    start = serializers.DateTimeField(source='rr_start')
    end = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ('id', 'programme', 'schedule_board', 'start', 'end', 'title', 
                  'type','source')

    def get_title(self, schedule):
        return schedule.programme.name

    def get_end(self, schedule):
        # XXX temp workaround while dtstart not mandatory
        try:
            return schedule.recurrences.dtstart + schedule.runtime
        except TypeError:
            return None


class TransmissionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    slug =serializers.SlugField(max_length=100)
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    url = serializers.URLField()
