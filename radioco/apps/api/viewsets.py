from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

# TODO: remame class
class ModelViewSetWithoutCreate(mixins.UpdateModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.ListModelMixin,
                                GenericViewSet):
    """
    A viewset that provides default `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass
