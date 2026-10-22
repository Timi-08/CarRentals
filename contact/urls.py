from django.urls import path

from . import views

app_name = 'contact'

urlpatterns = [
    path('', views.contact_us, name='contact_us'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('pages/<slug:slug>/', views.page_detail, name='page'),
]
