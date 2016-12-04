from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class UpdateOnlyModelViewSet(mixins.UpdateModelMixin, GenericViewSet):
    """
    A viewset that provides a update action.
    """
    pass
