from django.urls import path

from . import views

app_name = 'contact'

# Contact page routes: message form, newsletter signup, and editable static content.
urlpatterns = [
    path('', views.contact_us, name='contact_us'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('pages/<slug:slug>/', views.page_detail, name='page'),
]
