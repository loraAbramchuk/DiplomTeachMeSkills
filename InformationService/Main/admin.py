from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.Country)
admin.site.register(models.Genre)
admin.site.register(models.Movie)
admin.site.register(models.Serial)

