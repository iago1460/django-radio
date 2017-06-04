from django.core.urlresolvers import reverse

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
    photo_url = serializers.SerializerMethodField()
    rss_url = serializers.SerializerMethodField()

    def get_photo_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.photo.url)

    def get_rss_url(self, obj):
        return self.context['request'].build_absolute_uri(reverse('programmes:rss', args=[obj.slug]))

    class Meta:
        model = Programme
        fields = ('id', 'slug', 'name', 'synopsis', 'runtime', 'photo_url', 'rss_url', 'language', 'category')


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
    programme = serializers.IntegerField(source='schedule.programme.id')
    programme_url = serializers.SerializerMethodField()
    episode_url = serializers.SerializerMethodField()
    type = serializers.CharField(max_length=1, source='schedule.type')
    source = serializers.IntegerField(source='schedule.source.id')

    def get_programme_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.programme_url) if obj.programme_url else None

    def get_episode_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.episode_url) if obj.episode_url else None


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
