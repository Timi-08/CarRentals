from django.contrib import admin

from .models import Brand, Vehicle


# Brand admin keeps the fleet sorted and makes total counts visible.
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'vehicle_count')
    search_fields = ('name',)

    @admin.display(description='Vehicles')
    def vehicle_count(self, obj):
        return obj.vehicles.count()


# Vehicle admin gives staff a quick overview of stock, pricing, and visibility.
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'price_per_day', 'seats', 'fuel_type',
                    'is_available', 'is_featured')
    list_editable = ('is_available', 'is_featured')
    list_filter = ('brand', 'fuel_type', 'is_available', 'is_featured')
    search_fields = ('name', 'brand__name')
    list_select_related = ('brand',)
