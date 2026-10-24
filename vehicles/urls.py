from django.urls import path

from . import views

app_name = 'vehicles'

# Routes for the public vehicle catalogue and detail pages.
urlpatterns = [
    path('', views.car_list, name='car_list'),
    path('<int:pk>/', views.car_detail, name='car_detail'),
]
