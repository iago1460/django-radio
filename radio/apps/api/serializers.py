from apps.programmes.models import Programme
from apps.schedules.models import Schedule
from rest_framework import serializers
import datetime


class ProgrammeSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='programmes:detail',
        lookup_field='slug')

    class Meta:
        model = Programme
        fields = ('id', 'url', 'name', 'synopsis', 'runtime', 'photo', 'language', 'category')


class ScheduleSerializer(serializers.ModelSerializer):
#    start = serializers.SerializerMethodField()
#    end = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    textColor = serializers.SerializerMethodField()
    backgroundColor = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ('id', 'programme', 'schedule_board', 'start', 'end', 'title', 
                  'type', 'textColor', 'backgroundColor', 'source')

#    def get_start(self, schedule):
#        return datetime.datetime.combine(schedule.programme.start_date, schedule.start_hour)
#
#    def get_end(self, schedule):
#        return self.get_start(schedule) + schedule.runtime

    def get_title(self, schedule):
        return schedule.programme.name

    def get_textColor(self, schedule):
        text_colours = {"L": "black", "B": "black", "S": "black"}
        return text_colours[schedule.type]

    def get_backgroundColor(self, schedule):
        background_colours = {"L": "#F9AD81", "B": "#C4DF9B", "S": "#8493CA"}
        return background_colours[schedule.type]
