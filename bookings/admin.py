from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'vehicle', 'pickup_date',
                    'return_date', 'total_price', 'status')
    list_filter = ('status', 'vehicle')
    search_fields = ('customer__username', 'vehicle__name')
    readonly_fields = ('total_price', 'created_at')
    actions = ['confirm_bookings', 'cancel_bookings']

    @admin.action(description="Confirm selected Pending bookings")
    def confirm_bookings(self, request, queryset):
        queryset.filter(status=Booking.PENDING).update(status=Booking.CONFIRMED)

    @admin.action(description="Cancel selected Pending bookings")
    def cancel_bookings(self, request, queryset):
        queryset.filter(status=Booking.PENDING).update(status=Booking.CANCELLED)