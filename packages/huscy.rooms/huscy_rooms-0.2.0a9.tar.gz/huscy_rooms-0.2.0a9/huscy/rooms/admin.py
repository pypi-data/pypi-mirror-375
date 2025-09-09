from django.contrib import admin

from huscy.rooms import models


admin.site.register(models.Building)
admin.site.register(models.Floor)
admin.site.register(models.Room)
