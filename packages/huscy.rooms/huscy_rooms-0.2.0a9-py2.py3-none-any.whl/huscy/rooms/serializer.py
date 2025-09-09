from rest_framework import serializers

from huscy.rooms import models


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Building
        fields = (
            'id',
            'name',
        )


class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Floor
        fields = (
            'building',
            'id',
            'level',
        )

    def to_representation(self, floor):
        response = super().to_representation(floor)
        response['building'] = floor.building.name
        return response


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Room
        fields = (
            'floor',
            'id',
            'name',
        )

    def to_representation(self, room):
        response = super().to_representation(room)
        response['floor'] = dict(
            level=room.floor.level,
            building=room.floor.building.name,
        )
        return response
