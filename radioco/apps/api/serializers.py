from django.core.urlresolvers import reverse

from radioco.apps.global_settings.models import SiteConfiguration
from radioco.apps.radioco.tz_utils import transform_datetime_tz, get_active_timezone
from radioco.apps.programmes.models import Programme, Episode
from radioco.apps.schedules.models import Schedule
from rest_framework import serializers


class AbsoluteURLField(serializers.URLField):
    """
    A field similar to URLField but returning always the absolute url

    For example:

    class ExampleSerializer(self):
        episode_url = AbsoluteURLField()
        photo_url = AbsoluteURLField(source='photo.url', read_only=True)
        rss_url = AbsoluteURLField(source='slug', reverse_url='programmes:rss')
    """
    def __init__(self, method_name=None, source=None, reverse_url=None, **kwargs):
        self.method_name = method_name
        self.reverse_url = reverse_url
        kwargs['source'] = source
        super(AbsoluteURLField, self).__init__(**kwargs)

    def to_representation(self, value):
        if self.reverse_url:
            value = reverse(self.reverse_url, args=[value])
        return super(AbsoluteURLField, self).to_representation(self.context['request'].build_absolute_uri(value)) if value else None


class DateTimeFieldTz(serializers.DateTimeField):
    """
    Field to display the datetime in the current timezone
    """

    def to_representation(self, date):
        return super(DateTimeFieldTz, self).to_representation(transform_datetime_tz(date, tz=get_active_timezone()))


class ProgrammeSerializer(serializers.ModelSerializer):
    runtime = serializers.DurationField()
    photo_url = AbsoluteURLField(source='photo.url', read_only=True)
    rss_url = AbsoluteURLField(source='slug', reverse_url='programmes:rss')

    class Meta:
        model = Programme
        fields = ('id', 'slug', 'name', 'synopsis', 'runtime', 'photo_url', 'rss_url', 'language', 'category')


class RadiocomProgrammeSerializer(serializers.ModelSerializer):
    logo_url = AbsoluteURLField(source='photo.url', read_only=True)
    rss_url = AbsoluteURLField(source='slug', reverse_url='programmes:rss')
    description = serializers.CharField(source='synopsis')

    class Meta:
        model = Programme
        fields = ('id', 'name', 'description', 'logo_url', 'rss_url')


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
    episode = serializers.IntegerField(source='episode.id')
    programme = serializers.IntegerField(source='programme.id')
    programme_url = AbsoluteURLField()
    episode_url = AbsoluteURLField()
    type = serializers.CharField(max_length=1, source='schedule.type')
    source = serializers.IntegerField(source='schedule.source.id')


class RadiocomTransmissionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(source='programme.synopsis')
    start = DateTimeFieldTz()
    end = DateTimeFieldTz()
    programme_url = AbsoluteURLField()
    logo_url = AbsoluteURLField(source='programme.photo.url', read_only=True)
    type = serializers.CharField(max_length=1, source='schedule.type')
    rss_url = AbsoluteURLField(source='slug', reverse_url='programmes:rss')


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


class RadiocomConfigurationSerializer(serializers.Serializer):
    icon_url = serializers.CharField(source='big_icon_url')
    big_icon_url = serializers.CharField()
    station_photos = serializers.SerializerMethodField()
    facebook_url = serializers.SerializerMethodField()
    twitter_url = serializers.SerializerMethodField()

    def get_station_photos(self, obj):
        return filter(lambda x: bool(x), [image_url.strip() for image_url in obj.station_photos.split(',')])

    def get_facebook_url(self, obj):
        return SiteConfiguration.objects.get().facebook_address

    def get_twitter_url(self, obj):
        return SiteConfiguration.objects.get().twitter_address

    class Meta:
        model = Episode
        fields = ('station_name', 'big_icon_url', 'history', 'latitude', 'longitude', 'news_rss', 'stream_url')
