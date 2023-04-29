from django.contrib import admin

#Register your models here.
from .models import Forecast, Vote

admin.site.register(Forecast)
admin.site.register(Vote)
