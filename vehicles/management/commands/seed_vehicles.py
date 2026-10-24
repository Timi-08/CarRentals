from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from vehicles.models import Brand, Vehicle
from seed_data import BRANDS, VEHICLE_IMAGES, VEHICLES


# Seed the database with demo cars and the associated brand catalog used by the app.
class Command(BaseCommand):
    help = ('Add the sample brands and vehicles to the database. '
            'Safe to run more than once: existing records are left untouched.')

    @transaction.atomic
    def handle(self, *args, **options):
        brands = {}
        new_brands = 0
        for name in BRANDS:
            # Ensure each brand exists once, even if the command is run repeatedly.
            brand, created = Brand.objects.get_or_create(name=name)
            brands[name] = brand
            new_brands += created

        new_vehicles = 0
        for brand_name, name, price, seats, fuel, available, featured, description in VEHICLES:
            image_path = VEHICLE_IMAGES.get((brand_name, name), '')
            vehicle, created = Vehicle.objects.get_or_create(
                brand=brands[brand_name],
                name=name,
                defaults={
                    'price_per_day': Decimal(price),
                    'seats': seats,
                    'fuel_type': fuel,
                    'is_available': available,
                    'is_featured': featured,
                    'description': description,
                    'image': image_path,
                },
            )
            new_vehicles += created
            if not created and image_path and not vehicle.image:
                # Backfill missing images for any vehicles already imported manually.
                vehicle.image = image_path
                vehicle.save(update_fields=['image'])

        self.stdout.write(self.style.SUCCESS(
            f'Added {new_brands} new brand(s) and {new_vehicles} new vehicle(s). '
            f'Totals: {Brand.objects.count()} brands, {Vehicle.objects.count()} vehicles.'))
