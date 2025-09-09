from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions

from huscy.rooms import serializer, services


class BuildingViewSet(viewsets.ModelViewSet):
    queryset = services.get_buildings()
    serializer_class = serializer.BuildingSerializer
    permission_classes = (DjangoModelPermissions, )


class FloorViewSet(viewsets.ModelViewSet):
    queryset = services.get_floors()
    serializer_class = serializer.FloorSerializer
    permission_classes = (DjangoModelPermissions, )


class RoomViewSet(viewsets.ModelViewSet):
    queryset = services.get_rooms()
    serializer_class = serializer.RoomSerializer
    permission_classes = (DjangoModelPermissions, )
