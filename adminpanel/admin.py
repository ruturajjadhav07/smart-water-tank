from django.contrib import admin
from adminpanel.models import UserProfile, Building, Tank, Sensor, Reading, AdminPageVisit

# Register your models here.
#User1-smartwatertank@2025
admin.site.register(UserProfile)

admin.site.register(Building)
admin.site.register(Tank)
admin.site.register(Sensor)
admin.site.register(Reading)

admin.site.register(AdminPageVisit)