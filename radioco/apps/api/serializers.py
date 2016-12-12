from radioco.apps.radioco.tz_utils import transform_datetime_tz, get_active_timezone
from radioco.apps.programmes.models import Programme, Episode
from radioco.apps.schedules.models import Schedule
from rest_framework import serializers


class DateTimeFieldTz(serializers.DateTimeField):
    """
    Field to display the datetime in the current timezone
    """

    def to_representation(self, date):
        return super(DateTimeFieldTz, self).to_representation(transform_datetime_tz(date, tz=get_active_timezone()))


class ProgrammeSerializer(serializers.ModelSerializer):
    runtime = serializers.DurationField()
    photo = serializers.ImageField()

    class Meta:
        model = Programme
        fields = ('id', 'slug', 'name', 'synopsis', 'runtime', 'photo', 'language', 'category')


class EpisodeSerializer(serializers.ModelSerializer):
    programme = serializers.SlugRelatedField(slug_field='slug', queryset=Programme.objects.all)

    class Meta:
        model = Episode
        fields = ('title', 'programme', 'summary', 'issue_date', 'season', 'number_in_season')


class ScheduleSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    programme = serializers.SlugRelatedField(slug_field='slug', queryset=Programme.objects.all())
    start = serializers.DateTimeField(source='start_dt')
    runtime = serializers.ReadOnlyField()

    class Meta:
        model = Schedule
        fields = (
            'id', 'programme', 'calendar', 'start', 'runtime', 'title', 'type', 'source'
        )

    def get_title(self, schedule):
        return schedule.programme.name

    def validate(self, attrs):
        programme = attrs.get('programme')
        start = attrs.get('start_dt')

        if programme.start_dt and programme.start_dt > start \
                or programme.end_dt and programme.end_dt < start:
                    raise serializers.ValidationError('Schedule is outside of the programme dates constraints')
        return attrs


class TransmissionSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='schedule.id')
    name = serializers.CharField(max_length=100)
    slug = serializers.SlugField(max_length=100)
    start = DateTimeFieldTz()
    end = DateTimeFieldTz()
    schedule = serializers.IntegerField(source='schedule.id')
    programme_url = serializers.URLField()
    episode_url = serializers.URLField()
    type = serializers.CharField(max_length=1, source='schedule.type')
    source = serializers.IntegerField(source='schedule.source')


class TransmissionSerializerLight(serializers.Serializer):  # WARNING: Hack to save changes
    id = serializers.IntegerField(source='schedule.id')
    start = serializers.DateTimeField()
    new_start = serializers.DateTimeField(allow_null=True)

    def validate(self, attrs):
        programme = self.instance.programme
        new_start = attrs.get('new_start')

        if programme.start_dt and programme.start_dt > new_start \
                or programme.end_dt and programme.end_dt < new_start:
                    raise serializers.ValidationError('Schedule is outside of the programme dates constraints')
        return attrs
