"""Tests for the sample-data command: python manage.py seed_vehicles"""
from decimal import Decimal
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from vehicles.models import Brand, Vehicle
from seed_data import BRANDS, VEHICLE_IMAGES, VEHICLES


def run_seed():
    out = StringIO()
    call_command('seed_vehicles', stdout=out)
    return out.getvalue()


class SeedVehiclesTests(TestCase):
    def test_creates_ten_brands_and_thirty_vehicles(self):
        run_seed()
        self.assertEqual(Brand.objects.count(), 10)
        self.assertEqual(Vehicle.objects.count(), 30)

    def test_every_brand_has_at_least_one_vehicle(self):
        run_seed()
        for brand in Brand.objects.all():
            with self.subTest(brand=brand.name):
                self.assertTrue(brand.vehicles.exists())

    def test_every_vehicle_passes_model_validation(self):
        run_seed()
        for vehicle in Vehicle.objects.all():
            with self.subTest(vehicle=str(vehicle)):
                vehicle.full_clean()

    def test_all_four_fuel_types_are_used(self):
        run_seed()
        fuels = set(Vehicle.objects.values_list('fuel_type', flat=True))
        self.assertEqual(fuels, {'petrol', 'diesel', 'electric', 'hybrid'})

    def test_no_more_featured_vehicles_than_the_home_page_shows(self):
        run_seed()
        featured = Vehicle.objects.filter(is_featured=True, is_available=True).count()
        self.assertEqual(featured, 6)

    def test_some_vehicles_are_unavailable_to_show_that_state(self):
        run_seed()
        self.assertTrue(Vehicle.objects.filter(is_available=False).exists())

    def test_seeded_vehicle_images_exist(self):
        run_seed()
        for (brand_name, vehicle_name), image_path in VEHICLE_IMAGES.items():
            with self.subTest(vehicle=vehicle_name):
                vehicle = Vehicle.objects.get(brand__name=brand_name, name=vehicle_name)
                self.assertEqual(vehicle.image.name, image_path)
                self.assertTrue((Path(settings.MEDIA_ROOT) / image_path).is_file())

    def test_running_twice_does_not_create_duplicates(self):
        run_seed()
        output = run_seed()
        self.assertEqual(Brand.objects.count(), 10)
        self.assertEqual(Vehicle.objects.count(), 30)
        self.assertIn('Added 0 new brand(s) and 0 new vehicle(s)', output)

    def test_running_again_does_not_overwrite_admin_changes(self):
        run_seed()
        camry = Vehicle.objects.get(name='Camry')
        camry.price_per_day = Decimal('99999.00')
        camry.is_featured = False
        camry.save()

        run_seed()

        camry.refresh_from_db()
        self.assertEqual(camry.price_per_day, Decimal('99999.00'))
        self.assertFalse(camry.is_featured)

    def test_fills_in_only_what_is_missing(self):
        Brand.objects.create(name='Toyota')
        run_seed()
        self.assertEqual(Brand.objects.filter(name='Toyota').count(), 1)
        self.assertEqual(Vehicle.objects.count(), 30)

    def test_fills_missing_seed_images_without_overwriting_admin_images(self):
        run_seed()
        explorer = Vehicle.objects.get(brand__name='Ford', name='Explorer')
        explorer.image = 'vehicles/admin-upload.png'
        explorer.save(update_fields=['image'])

        ranger = Vehicle.objects.get(brand__name='Ford', name='Ranger')
        ranger.image = ''
        ranger.save(update_fields=['image'])

        run_seed()

        explorer.refresh_from_db()
        ranger.refresh_from_db()
        self.assertEqual(explorer.image.name, 'vehicles/admin-upload.png')
        self.assertEqual(ranger.image.name, VEHICLE_IMAGES[('Ford', 'Ranger')])

    def test_seed_data_has_no_duplicate_entries(self):
        self.assertEqual(len(BRANDS), len(set(BRANDS)))
        pairs = [(v[0], v[1]) for v in VEHICLES]
        self.assertEqual(len(pairs), len(set(pairs)))
        self.assertTrue(all(brand in BRANDS for brand, *_ in VEHICLES))
