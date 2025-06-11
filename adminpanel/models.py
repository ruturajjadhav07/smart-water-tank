from django.db import models
from django.utils import timezone
import uuid
import random

# Admin Page Visit
class AdminPageVisit(models.Model):
    ip_address = models.GenericIPAddressField()
    visited_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Visited from {self.ip_address} at {self.visited_at}"

# User Profile
class UserProfile(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100, primary_key=True) 
    created_date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.username

# Building
class Building(models.Model):
    building_id = models.CharField(max_length=100, primary_key=True)
    building_name = models.CharField(max_length=100)
    building_created_date = models.DateTimeField()  
    last_modified_date = models.DateTimeField()     

    def __str__(self):
        return self.building_name

# Tank
class Tank(models.Model):
    tank_id = models.CharField(max_length=100, primary_key=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    capacity = models.FloatField()
    user = models.ForeignKey(UserProfile, to_field='user_id', on_delete=models.CASCADE)
    tank_created_date = models.DateTimeField()      
    tank_last_modified_date = models.DateTimeField() 

    def __str__(self):
        return self.tank_id

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            sensor_id = str(uuid.uuid4())[:8]
            sensor = Sensor.objects.create(
                sensor_id=sensor_id,
                tank=self,
                date_time=timezone.now(),
                sensor_last_modified_date=timezone.now()
            )
            # Create 10 dummy readings
            for i in range(10):
                Reading.objects.create(
                    reading_id=str(uuid.uuid4())[:8],
                    sensor=sensor,
                    reading=round(random.uniform(0, self.capacity), 2),
                    sensor_reading_last_modified_date=timezone.now()
                )

# Sensor
class Sensor(models.Model):
    sensor_id = models.CharField(max_length=100, primary_key=True)
    tank = models.OneToOneField(Tank, on_delete=models.CASCADE)
    date_time = models.DateTimeField()              
    sensor_last_modified_date = models.DateTimeField() 

    def __str__(self):
        return self.sensor_id

# Reading
class Reading(models.Model):
    reading_id = models.CharField(max_length=100, primary_key=True)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    reading = models.FloatField()
    sensor_reading_last_modified_date = models.DateTimeField()

    def __str__(self):
        return self.reading_id
