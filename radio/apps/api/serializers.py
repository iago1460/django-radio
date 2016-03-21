from apps.programmes.models import Programme
from apps.schedules.models import Schedule, Transmission
from rest_framework import serializers
import datetime


class ProgrammeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programme
        fields = ('slug', 'name', 'synopsis', 'runtime', 'photo', 'language', 'category')


class ScheduleSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    textColor = serializers.SerializerMethodField()
    backgroundColor = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ('id', 'programme', 'schedule_board', 'start', 'end', 'title', 
                  'type', 'textColor', 'backgroundColor', 'source')

    def get_title(self, schedule):
        return schedule.programme.name

    def get_textColor(self, schedule):
        text_colours = {"L": "black", "B": "black", "S": "black"}
        return text_colours[schedule.type]

    def get_backgroundColor(self, schedule):
        background_colours = {"L": "#F9AD81", "B": "#C4DF9B", "S": "#8493CA"}
        return background_colours[schedule.type]


class TransmissionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    slug =serializers.SlugField(max_length=100)
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    url = serializers.URLField()
