import csv
from multiprocessing import AuthenticationError
import os
import random
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from .models import UserProfile
from django.contrib import messages
from .models import UserProfile, Building, Tank, Sensor, Reading
from datetime import datetime
from django.db.models import OuterRef, Subquery
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseNotFound
from django.utils import timezone
from django.urls import reverse
from django.utils.timezone import localtime
from django.contrib.auth import logout
from django.shortcuts import redirect

from collections import defaultdict
from django.db.models import Prefetch
from django.utils.dateformat import DateFormat
from django.utils.timezone import localtime
from django.shortcuts import render
from .models import Building, Tank, Sensor, Reading
import json
from django.core.serializers.json import DjangoJSONEncoder
# SmartWaterTankAdmin ----->12345

def base_page(request):
    return render(request, 'adminpanel/base.html')

def is_admin(user):
    return user.is_staff

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            request.session['is_admin_logged_in'] = True
            return redirect('adminpage') 
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'adminpanel/adminlogin.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            # Get user from custom model
            user = UserProfile.objects.get(username=username)

            # Compare plain-text password
            if user.password == password:
                # Simulate login by storing user info in session
                request.session['user_id'] = user.user_id

                request.session['username'] = user.username
                return redirect('user_page')  # Replace with your actual page name
            else:
                error = 'Invalid username or password'
        except UserProfile.DoesNotExist:
            error = 'Invalid username or password'

        return render(request, 'adminpanel/userlogin.html', {
            'error': error
        })

    return render(request, 'adminpanel/userlogin.html')

def user_page(request):
    user_id = request.session.get('user_id')

    if not user_id:
        # If no user is logged in, redirect to login
        return redirect('user_login')

    user = get_object_or_404(UserProfile, user_id=user_id)
    tanks = Tank.objects.filter(user=user)

    return render(request, 'adminpanel/userpage.html', {
        'user': user,
        'tanks': tanks
    })

def admin_page(request):
    if not request.session.get('is_admin_logged_in'):
        return redirect('admin_login')  # kick them back to login

    return render(request, 'adminpanel/adminpage.html')
# ----------------------------
# USER MANAGEMENT VIEWS
# ----------------------------
# Show all users
def user_list(request):
   
    users = UserProfile.objects.all().order_by('user_id') 
    return render(request, 'adminpanel/user_list.html', {'users': users})

# Add a new user
def add_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        user_id = request.POST['user_id']
        created_date = request.POST['created_date']

        UserProfile.objects.create(
            username=username,
            email=email,
            password=password,
            user_id=user_id,
            created_date=created_date
        )
        messages.success(request, 'User added successfully!')
        return redirect('user_list')
    return render(request, 'adminpanel/add_user.html')

# Edit user
def edit_user(request, user_id):
    user = get_object_or_404(UserProfile, user_id=user_id)

    if request.method == 'POST':
        user.username = request.POST['username']
        user.email = request.POST['email']
        user.password = request.POST['password']
        user.user_id = request.POST['user_id']
        user.created_date = request.POST['created_date']
        user.save()
        messages.success(request, 'User updated successfully!')
        return redirect('user_list')
    return render(request, 'adminpanel/edit_user.html', {'user': user})

# Delete user
def delete_user(request, user_id):
    user = get_object_or_404(UserProfile, user_id=user_id)
    user.delete()
    messages.success(request, 'User deleted successfully!')
    return redirect('user_list')



# ----------------------------
# BUILDING MANAGEMENT VIEWS
# ----------------------------
#Building
def building_list(request):
    buildings = Building.objects.all()
    return render(request, 'adminpanel/building_list.html', {'buildings': buildings})
#tank

def tank_list(request, building_id):
    building = get_object_or_404(Building, building_id=building_id)
    tanks = Tank.objects.filter(building=building)
    users = UserProfile.objects.all()

    for tank in tanks:
        sensor = Sensor.objects.filter(tank=tank).first()
        if sensor:
            readings = list(Reading.objects.filter(sensor=sensor))
            latest_reading = random.choice(readings) if readings else None

            if latest_reading:
                tank.latest_reading_value = latest_reading.reading
                tank.latest_reading_date = localtime(latest_reading.sensor_reading_last_modified_date).strftime("%d-%m-%Y %H:%M")

                try:
                    percent = (latest_reading.reading / tank.capacity) * 100
                    tank.visual_level = max(0, min(percent, 100))

                    # Color class assignment
                    if tank.visual_level < 30:
                        tank.color_class = 'low'
                    elif tank.visual_level < 70:
                        tank.color_class = 'medium'
                    else:
                        tank.color_class = 'high'
                except (ZeroDivisionError, TypeError):
                    tank.visual_level = None
                    tank.color_class = ''
            else:
                tank.latest_reading_value = None
                tank.latest_reading_date = None
                tank.visual_level = None
                tank.color_class = ''
        else:
            tank.latest_reading_value = None
            tank.latest_reading_date = None
            tank.visual_level = None
            tank.color_class = ''

    context = {
        'building': building,
        'tanks': tanks,
        'users': users,
    }
    return render(request, 'adminpanel/tank_list.html', context)

def show_sensor_csv_data(request, tank_id):
    tank = get_object_or_404(Tank, tank_id=tank_id)
    sensor = Sensor.objects.filter(tank=tank).first()

    reading = None
    if sensor:
        readings = list(Reading.objects.filter(sensor=sensor))
        if readings:
            reading = random.choice(readings)  # this is now a single object!

    # DEBUG
    print("Building name from Tank ID:", tank.building.building_name)


    if reading:
        print("Selected Reading:", reading)
        print("Reading Value:", reading.reading)
        print("Timestamp from DB:", reading.sensor_reading_last_modified_date)
    else:
        print("No reading found.")


    return render(request, 'adminpanel/reading_display.html', {
        'tank': tank,
        'reading': reading,
    })
    
def view_readings(request, tank_id):
    if not request.session.get('user_id'):
        return redirect('user_login')

    user = get_object_or_404(UserProfile, user_id=request.session.get('user_id'))
    tank = get_object_or_404(Tank, tank_id=tank_id, user=user)

    # Always get fresh readings
    readings = list(Reading.objects.filter(sensor__tank=tank).order_by('-sensor_reading_last_modified_date'))

    import random
    if readings:
        random_reading = random.choice(readings)
        percentage = round((random_reading.reading / tank.capacity) * 100)
    else:
        random_reading = None
        percentage = 0

    # Determine color class
    if percentage < 30:
        color_class = 'low'
    elif percentage < 70:
        color_class = 'medium'
    else:
        color_class = 'high'

    context = {
        'tank': tank,
        'random_reading': random_reading,
        'percentage': percentage,
        'color_class': color_class
    }
    return render(request, 'adminpanel/user_tank_readings.html', context)



def add_tank(request, building_id):
    building = get_object_or_404(Building, building_id=building_id)

    if request.method == "POST":
        tank_id = request.POST.get("tank_id", "").strip()
        capacity = request.POST.get("capacity")
        user_id = request.POST.get("user_id")

        # Check for duplicate tank ID
        if Tank.objects.filter(tank_id=tank_id).exists():
            messages.error(request, f"Tank ID '{tank_id}' already exists.")
            return redirect('add_tank', building_id=building_id)

        try:
            user = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            messages.error(request, "Selected user does not exist.")
            return redirect('add_tank', building_id=building_id)

        # Create tank
        tank = Tank.objects.create(
            tank_id=tank_id,
            building=building,
            capacity=float(capacity),  # assume frontend ensures it's a number
            user=user,
            tank_created_date=timezone.now(),
            tank_last_modified_date=timezone.now()
        )

        messages.success(request, "Tank added successfully.")
        return redirect('add_tank', building_id=building_id)

    users = UserProfile.objects.all()
    return render(request, 'adminpanel/add_tank.html', {
        'building': building,
        'users': users
    })

def logout_view(request):
    logout(request)
    return redirect('admin_login')  # Redirect to login or home page

def reading_history_view(request):
    buildings = Building.objects.all().prefetch_related(
        Prefetch('tank_set', queryset=Tank.objects.select_related('sensor'))
    )

    monthly_data = defaultdict(lambda: defaultdict(float))  # {month: {building_name: total_usage}}

    for building in buildings:
        tanks = building.tank_set.all()
        for tank in tanks:
            sensor = getattr(tank, 'sensor', None)
            if not sensor:
                continue

            readings = Reading.objects.filter(sensor=sensor).order_by('sensor_reading_last_modified_date')

            previous_value = None
            previous_date = None

            for reading in readings:
                current_value = reading.reading
                current_date = localtime(reading.sensor_reading_last_modified_date)

                if previous_value is not None:
                    usage = max(0, previous_value - current_value)

                    month_str = DateFormat(current_date).format('Y-m')  # e.g., "2025-05"
                    monthly_data[month_str][building.building_name] += usage

                previous_value = current_value
                previous_date = current_date

    # Convert defaultdict to list format for frontend
    chart_data = []
    for month, buildings_dict in monthly_data.items():
        data = {
            'month': month,
            'buildings': [
                {'building_name': name, 'total_usage': round(usage, 2)}
                for name, usage in buildings_dict.items()
            ]
        }
        chart_data.append(data)

    return render(request, 'adminpanel/reading_history.html', {
        'monthly_data': json.dumps(chart_data, cls=DjangoJSONEncoder)
    })