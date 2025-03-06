from django.contrib import admin
from .models import User, Building, WaterTank, Sensor, SensorReading

admin.site.register(User)
admin.site.register(Building)
admin.site.register(WaterTank)
admin.site.register(Sensor)
admin.site.register(SensorReading)