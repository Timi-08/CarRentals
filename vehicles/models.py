"""Vehicle catalog rules and inventory information for the rental app."""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Brand(models.Model):
    """The make of a vehicle, for example Toyota."""
    name = models.CharField(max_length=100, unique=True)

    # Sort brands alphabetically so lists and filters stay predictable.
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    # Supported fuel options used in filters, forms, and the booking engine.
    PETROL = 'petrol'
    DIESEL = 'diesel'
    ELECTRIC = 'electric'
    HYBRID = 'hybrid'
    FUEL_CHOICES = [
        (PETROL, 'Petrol'),
        (DIESEL, 'Diesel'),
        (ELECTRIC, 'Electric'),
        (HYBRID, 'Hybrid'),
    ]

    name = models.CharField(max_length=150)
    # PROTECT: a brand that still has vehicles cannot be deleted by accident.
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='vehicles')
    price_per_day = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))])
    seats = models.PositiveSmallIntegerField(default=4, validators=[MinValueValidator(1)])
    fuel_type = models.CharField(max_length=10, choices=FUEL_CHOICES, default=PETROL)
    image = models.ImageField(upload_to='vehicles/', blank=True)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(
        default=False, help_text='Show this vehicle on the home page.')
    created_at = models.DateTimeField(auto_now_add=True)

    # Present vehicles in a consistent, brand-first order for all listing screens.
    class Meta:
        ordering = ['brand__name', 'name', 'pk']

    def __str__(self):
        return f'{self.brand} {self.name}'
