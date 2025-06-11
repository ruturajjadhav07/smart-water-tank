from django.urls import path
from . import views

urlpatterns = [
    path('', views.base_page, name='base'),
    path('login/user/', views.user_login, name='user_login'),
    path('login/admin/', views.admin_login, name='admin_login'),
    path('userpage/', views.user_page, name='user_page'),
    path('adminpage/', views.admin_page, name='adminpage'),

    # User Management
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),

    # Building Management
    path('buildings/', views.building_list, name='building_list'),
    

    # Reading Management
    path('tanks/<str:tank_id>/reading-preview/', views.show_sensor_csv_data, name='sensor_readings'),
    path('tanks/<str:tank_id>/readings/', views.view_readings, name='view_readings'),

    # Add tank
     

    # In urls.py    
    
    path('buildings/<building_id>/tanks/', views.tank_list, name='tank_list'),

    
    path('buildings/<str:building_id>/tanks/add/', views.add_tank, name='add_tank'),


    path('logout/', views.logout_view, name='logout'),

     path('dashboard/reading-history/', views.reading_history_view, name='reading_history_view')


]
