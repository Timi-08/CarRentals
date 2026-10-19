from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Booking(models.Model):
    """A customer's request to rent one vehicle for a date range."""
    PENDING = 'Pending'
    CONFIRMED = 'Confirmed'
    CANCELLED = 'Cancelled'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (CANCELLED, 'Cancelled'),
    ]
    # Only these statuses block other bookings for the same vehicle (BKG-05)
    BLOCKING_STATUSES = (PENDING, CONFIRMED)

    customer = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE,
                                 related_name='bookings')
    vehicle = models.ForeignKey('vehicles.Vehicle',
                                on_delete=models.CASCADE,
                                related_name='bookings')
    pickup_date = models.DateField()
    return_date = models.DateField()
    location = models.CharField(max_length=100)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer} - {self.vehicle} ({self.pickup_date} to {self.return_date})"

    @property
    def days(self):
        """Number of rental days (return date minus pickup date)."""
        return (self.return_date - self.pickup_date).days

    @property
    def can_customer_cancel(self):
        """Customers may cancel only while Pending (BKG-09)."""
        return self.status == self.PENDING

    def clean(self):
        """Validation rules BKG-03, BKG-04, BKG-05."""
        errors = {}

        if self.pickup_date and self.return_date:
            # BKG-03: return must be after pickup
            if self.return_date <= self.pickup_date:
                errors['return_date'] = "Return date must be after the pickup date."
            # BKG-03: pickup cannot be in the past (new bookings only)
            if self._state.adding and self.pickup_date < timezone.localdate():
                errors['pickup_date'] = "Pickup date cannot be in the past."

        if self.vehicle_id:
            # BKG-04: vehicle must be available (new bookings only)
            if self._state.adding and not self.vehicle.is_available:
                errors['vehicle'] = "This vehicle is not available for booking."

            # BKG-05: no overlap with Pending/Confirmed bookings of same vehicle.
            # Back-to-back is allowed (return day = next pickup day).
            if (self.pickup_date and self.return_date
                    and 'return_date' not in errors
                    and self.status in self.BLOCKING_STATUSES):
                overlap = Booking.objects.filter(
                    vehicle=self.vehicle,
                    status__in=self.BLOCKING_STATUSES,
                    pickup_date__lt=self.return_date,
                    return_date__gt=self.pickup_date,
                ).exclude(pk=self.pk).exists()
                if overlap:
                    errors['__all__'] = "This vehicle is already booked for those dates."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """BKG-06: total price = days x price per day."""
        if self.pickup_date and self.return_date and self.vehicle_id:
            self.total_price = self.days * self.vehicle.price_per_day
        super().save(*args, **kwargs)