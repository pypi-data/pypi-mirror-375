from . import models


def get_buildings():
    return models.Building.objects.order_by('name')


def get_floors():
    qs = models.Floor.objects
    qs = qs.select_related('building')
    qs = qs.order_by('building__name', 'level')
    return qs


def get_rooms():
    qs = models.Room.objects
    qs = qs.select_related('floor__building')
    qs = qs.order_by('floor__building__name', 'floor__level', 'name')
    return qs
