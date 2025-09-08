from rest_framework import viewsets
from rest_framework.views import APIView

from .exceptions import SerializerNotFoundError


class ActionSerializerMixin:
    """
    Selects serializer based on action and HTTP method.
    Works with:
        - ModelViewSet
        - GenericViewSet + mixins
        - APIView
    """

    # Fallback serializers
    read_serializer_class = None
    write_serializer_class = None
    serializer_class = None

    # Action-based serializers
    list_serializer_class = None
    retrieve_serializer_class = None
    create_serializer_class = None
    update_serializer_class = None
    partial_update_serializer_class = None
    destroy_serializer_class = None

    def get_action_serializer_attr(self):
        action_attr_map = {
            "list": "list_serializer_class",
            "retrieve": "retrieve_serializer_class",
            "create": "create_serializer_class",
            "update": "update_serializer_class",
            "partial_update": "partial_update_serializer_class",
            "destroy": "destroy_serializer_class",
        }
        return action_attr_map.get(getattr(self, "action", None), None)

    def get_serializer_class(self):
        attr_name = self.get_action_serializer_attr()
        if attr_name:
            serializer = getattr(self, attr_name, None)
            if serializer:
                return serializer

        method = getattr(self.request, "method", "GET").upper()
        if method in ["GET", "HEAD", "OPTIONS"]:
            if getattr(self, "read_serializer_class", None):
                return self.read_serializer_class
        else:
            if getattr(self, "write_serializer_class", None):
                return self.write_serializer_class

        if getattr(self, "serializer_class", None):
            return self.serializer_class

        raise SerializerNotFoundError(
            f"No serializer found for action '{getattr(self, 'action', None)}' "
            f"and method '{method}'"
        )


class ActionSerializerModelViewSet(ActionSerializerMixin, viewsets.ModelViewSet):
    """ModelViewSet with action-based serializer support."""

    pass


class ActionSerializerGenericViewSet(ActionSerializerMixin, viewsets.GenericViewSet):
    """GenericViewSet with action-based serializer support."""

    pass


class ActionSerializerAPIView(ActionSerializerMixin, APIView):
    """APIView with action-based serializer support."""

    pass
