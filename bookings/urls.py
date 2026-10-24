from django.urls import path
from . import views

app_name = 'bookings'

# Booking routes cover both the customer's self-service flows and the admin management screens.
urlpatterns = [
    path('', views.my_bookings, name='my_bookings'),
    path('new/', views.create_booking, name='create'),
    path('<int:pk>/confirmation/', views.booking_confirmation, name='confirmation'),
    path('<int:pk>/cancel/', views.cancel_booking, name='cancel'),
    path('manage/', views.manage_bookings, name='manage'),
    path('manage/<int:pk>/<str:action>/', views.admin_update_booking, name='admin_update'),
]