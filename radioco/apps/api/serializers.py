from radioco.apps.programmes.models import Programme, Episode
from radioco.apps.schedules.models import Schedule, ScheduleBoard
from rest_framework import serializers


class ProgrammeSerializer(serializers.ModelSerializer):
    runtime = serializers.DurationField()
    photo = serializers.ImageField()

    class Meta:
        model = Programme
        fields = ('slug', 'name', 'synopsis', 'runtime', 'photo', 'language', 'category')


class EpisodeSerializer(serializers.ModelSerializer):
    programme = serializers.SlugRelatedField(slug_field='slug', queryset=Programme.objects.all)

    class Meta:
        model = Episode
        fields = ('title', 'programme', 'summary',
                  'issue_date', 'season', 'number_in_season')


class ScheduleSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    programme = serializers.SlugRelatedField(slug_field='slug', queryset=Programme.objects.all())
    schedule_board = serializers.SlugRelatedField(slug_field='slug', queryset=ScheduleBoard.objects.all())
    start = serializers.DateTimeField(source='start_date')
    end = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = (
            'id', 'programme', 'schedule_board', 'start', 'end', 'title', 'type', 'source'
        )

    def get_title(self, schedule):
        return schedule.programme.name

    def get_end(self, schedule):
        # XXX temp workaround while dtstart not mandatory
        try:
            return schedule.recurrences.dtstart + schedule.runtime
        except TypeError:
            return None


class TransmissionSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='schedule.id')
    name = serializers.CharField(max_length=100)
    slug = serializers.SlugField(max_length=100)
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    schedule = serializers.IntegerField(source='schedule.id')
    url = serializers.URLField()
    type = serializers.CharField(max_length=1, source='schedule.type')
    source = serializers.IntegerField(source='schedule.source')


class TransmissionSerializerLight(serializers.Serializer):  # WARNING: Hack to save changes
    id = serializers.IntegerField(source='schedule.id')
    start = serializers.DateTimeField()
    new_start = serializers.DateTimeField(allow_null=True)
