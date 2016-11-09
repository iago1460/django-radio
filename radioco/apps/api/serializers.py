from radioco.apps.radio.tz_utils import transform_datetime_tz
from radioco.apps.programmes.models import Programme, Episode
from radioco.apps.schedules.models import Schedule, ScheduleBoard
from rest_framework import serializers


class DateTimeFieldTz(serializers.DateTimeField): # TODO: DateTimeFieldTz and TimezoneSerializer not necessary

    def to_representation(self, date, tz):
        # date_in_new_tz = tz.normalize(date.astimezone(tz)) # FIXME

        # from dateutil.tz import tzoffset
        # from radioco.apps.radio.tz_utils import get_timezone_offset
        # date_in_new_tz = date.astimezone(tzoffset(None, get_timezone_offset(tz)))  # FIXME: fullcalendar needs a fix timezone how to get this

        # date_in_new_tz = transform_datetime_tz(date)
        date_in_new_tz = date

        return super(DateTimeFieldTz, self).to_representation(date_in_new_tz)


class TimezoneSerializer(serializers.Serializer):
    """
    Same as Serializer but it will store a timezone and it will send it to DateTimeFieldTz fields
    """
    timezone = None

    def __init__(self, *args, **kwargs):
        if 'timezone' in kwargs:
            self.timezone = kwargs.pop('timezone')
        super(TimezoneSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = serializers.OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except serializers.SkipField:
                continue

            if attribute is None:
                # We skip `to_representation` for `None` values so that
                # fields do not have to explicitly deal with that case.
                ret[field.field_name] = None
            elif type(field) is DateTimeFieldTz:
                ret[field.field_name] = field.to_representation(attribute, self.timezone)
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret


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
    start = serializers.DateTimeField(source='start_dt')
    runtime = serializers.ReadOnlyField()

    class Meta:
        model = Schedule
        fields = (
            'id', 'programme', 'schedule_board', 'start', 'runtime', 'title', 'type', 'source'
        )

    def get_title(self, schedule):
        return schedule.programme.name


class TransmissionSerializer(TimezoneSerializer):
    id = serializers.IntegerField(source='schedule.id')
    name = serializers.CharField(max_length=100)
    slug = serializers.SlugField(max_length=100)
    start = DateTimeFieldTz()
    end = DateTimeFieldTz()
    schedule = serializers.IntegerField(source='schedule.id')
    url = serializers.URLField()
    type = serializers.CharField(max_length=1, source='schedule.type')
    source = serializers.IntegerField(source='schedule.source')


class TransmissionSerializerLight(serializers.Serializer):  # WARNING: Hack to save changes
    id = serializers.IntegerField(source='schedule.id')
    start = serializers.DateTimeField()
    new_start = serializers.DateTimeField(allow_null=True)
