from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")  # Redirect to dashboard after login
        else:
            return render(request, "login.html", {"error": "Invalid credentials!"})

    return render(request, "login.html")

# Admin Logout View
def logout_view(request):
    logout(request)
    return redirect("login")

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import User

# Dashboard View
@login_required
def dashboard_view(request):
    users = User.objects.all()  # Fetch all registered users
    return render(request, "dashboard.html", {"users": users})  # Pass users to template

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to home after login
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


def user_logout(request):
    logout(request)
    return redirect('login')  # Redirect back to login page after logout