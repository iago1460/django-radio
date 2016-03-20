from apps.programmes.models import Programme
from rest_framework import serializers


class ProgrammeSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='programmes:detail',
        lookup_field='slug')

    class Meta:
        model = Programme
        fields = (
            'url', 'slug', 'name', 'synopsis', 'photo', 'language', 'category')
