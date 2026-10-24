from django.urls import path
from . import views

app_name = 'testimonials'

# Public page for browsing approved reviews and adding a new one.
urlpatterns = [
    path('', views.testimonial_list, name='list'),
    path('new/', views.testimonial_create, name='create'),
]