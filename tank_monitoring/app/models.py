from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    created_date = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",
        blank=True
    )


# Building Model
class Building(models.Model):
    name = models.CharField(max_length=255, unique=True)

# WaterTank Model
class WaterTank(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    capacity = models.FloatField()  # In liters

# Sensor Model
class Sensor(models.Model):
    tank = models.ForeignKey(WaterTank, on_delete=models.CASCADE)

# Sensor Readings
class SensorReading(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    water_level = models.FloatField()