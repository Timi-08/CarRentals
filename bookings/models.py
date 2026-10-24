from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Booking(models.Model):
    """A customer's request to rent one vehicle for a date range."""
    # These are the statuses that prevent a vehicle from being offered again until the booking changes.
    PENDING = 'Pending'
    CONFIRMED = 'Confirmed'
    CANCELLED = 'Cancelled'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (CANCELLED, 'Cancelled'),
    ]
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
        constraints = [
            models.CheckConstraint(
                condition=models.Q(return_date__gt=models.F('pickup_date')),
                name='booking_return_after_pickup',
            ),
        ]

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
            if self.return_date <= self.pickup_date:
                errors['return_date'] = "Return date must be after the pickup date."
            if self._state.adding and self.pickup_date < timezone.localdate():
                errors['pickup_date'] = "Pickup date cannot be in the past."

        if self.vehicle_id:
            if self._state.adding and not self.vehicle.is_available:
                errors['vehicle'] = "This vehicle is not available for booking."

            # Prevent overlapping bookings for the same vehicle on the same dates.
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
        # Recalculate the rental total whenever a booking is saved with valid dates.
        if self.pickup_date and self.return_date and self.vehicle_id:
            self.total_price = self.days * self.vehicle.price_per_day
        super().save(*args, **kwargs)