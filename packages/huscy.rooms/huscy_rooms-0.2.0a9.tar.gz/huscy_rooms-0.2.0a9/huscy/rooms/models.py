from django.db import models


class Building(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Floor(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    level = models.SmallIntegerField()

    def __str__(self):
        return f'{self.building}-{self.level}'


class Room(models.Model):
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)

    def __str__(self):
        return f'{self.floor}{self.name}'
