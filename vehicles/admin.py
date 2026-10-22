from django.contrib import admin
from .models import Brand, Vehicle


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'price_per_day', 'seats', 'fuel_type', 'available', 'featured')
    list_filter = ('brand', 'fuel_type', 'available', 'featured')
    search_fields = ('name', 'brand__name', 'description')
    list_editable = ('available', 'featured')
    autocomplete_fields = ('brand',)
