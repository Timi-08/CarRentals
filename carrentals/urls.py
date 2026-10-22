from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('vehicles/', include('vehicles.urls')),
    path('bookings/', include('bookings.urls')),
    path('contact/', include('contact.urls')),
    path('testimonials/', include('testimonials.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)