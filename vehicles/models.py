from django.core.validators import MinValueValidator
from django.db import models


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    class StockImage(models.TextChoices):
        TOYOTA_COROLLA = 'usnpx-2026toyotacorolla-angularfront-zd.webp', 'Toyota Corolla'
        HYUNDAI_ELANTRA = '2018_hyundai_elantra_sedan_eco_fq_oem_1_815x543.jpg', 'Hyundai Elantra'
        TOYOTA_CAMRY = '2027_toyota_camry_sedan_nightshade_fq_oem_1_600.avif', 'Toyota Camry'
        KIA_SPORTAGE = '2026-kia-sportage-front-angle-view-ak.webp', 'Kia Sportage'
        LEXUS_RX = '2026-lexus-rx-350-premiumawd-copper-6.webp', 'Lexus RX'
        HONDA_ACCORD = 'usnpx-2026hondaaccord-angularfront-zd1.webp', 'Honda Accord'
        NISSAN_ALTIMA = '01-usnpx-nissanaltima-angularfront-jms.webp', 'Nissan Altima'
        HONDA_SEDAN = 'images.jpg', 'Honda sedan'

    class FuelType(models.TextChoices):
        PETROL = 'petrol', 'Petrol'
        DIESEL = 'diesel', 'Diesel'
        HYBRID = 'hybrid', 'Hybrid'
        ELECTRIC = 'electric', 'Electric'

    name = models.CharField(max_length=150)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='vehicles')
    price_per_day = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    seats = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    fuel_type = models.CharField(max_length=10, choices=FuelType.choices)
    image = models.ImageField(upload_to='vehicles/', blank=True)
    stock_image = models.CharField(
        max_length=100, choices=StockImage.choices, blank=True
    )
    available = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ('brand__name', 'name')

    def __str__(self):
        return f'{self.brand} {self.name}'
