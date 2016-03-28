from apps.programmes.models import Programme
from apps.schedules.models import Schedule, Transmission
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
    programme = serializers.SerializerMethodField()
    schedule_board = serializers.SerializerMethodField()
    start = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ('id', 'programme', 'schedule_board', 'start', 'end', 'title', 
                  'type','source')

    def get_title(self, schedule):
        return schedule.programme.name

    def get_programme(self, schedule):
        return schedule.programme.slug

    def get_schedule_board(self, schedule):
        return schedule.schedule_board.slug

    def get_start(self, schedule):
        return schedule.recurrences.dtstart

    def get_end(self, schedule):
        # XXX temp workaround while dtstart not mandatory
        try:
            return self.get_start(schedule) + schedule.runtime
        except TypeError:
            return None


class TransmissionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    slug =serializers.SlugField(max_length=100)
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    url = serializers.URLField()
