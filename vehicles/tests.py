"""
Tests for the vehicles app (Person 2).

Run them with:
    python manage.py test vehicles
"""
import io
import tempfile
from decimal import Decimal

from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import ProtectedError
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Brand, Vehicle


def make_vehicle(brand, name, price='50000', seats=4, fuel=Vehicle.PETROL,
                 available=True, featured=False, **extra):
    return Vehicle.objects.create(
        name=name, brand=brand, price_per_day=Decimal(price), seats=seats,
        fuel_type=fuel, is_available=available, is_featured=featured, **extra)


def tiny_image():
    buffer = io.BytesIO()
    Image.new('RGB', (10, 10), 'red').save(buffer, format='PNG')
    return SimpleUploadedFile('car.png', buffer.getvalue(), content_type='image/png')


class ModelTests(TestCase):
    def test_brand_and_vehicle_strings(self):
        brand = Brand.objects.create(name='Toyota')
        vehicle = make_vehicle(brand, 'Camry')
        self.assertEqual(str(brand), 'Toyota')
        self.assertEqual(str(vehicle), 'Toyota Camry')

    def test_brand_names_are_unique(self):
        Brand.objects.create(name='Toyota')
        from django.db import IntegrityError, transaction
        with self.assertRaises(IntegrityError), transaction.atomic():
            Brand.objects.create(name='Toyota')

    def test_vehicle_defaults_to_available_and_not_featured(self):
        vehicle = make_vehicle(Brand.objects.create(name='Toyota'), 'Camry')
        vehicle.refresh_from_db()
        self.assertTrue(vehicle.is_available)
        self.assertFalse(vehicle.is_featured)

    def test_a_brand_with_vehicles_cannot_be_deleted(self):
        brand = Brand.objects.create(name='Toyota')
        make_vehicle(brand, 'Camry')
        with self.assertRaises(ProtectedError):
            brand.delete()
        self.assertTrue(Brand.objects.filter(pk=brand.pk).exists())

    def test_a_brand_without_vehicles_can_be_deleted(self):
        brand = Brand.objects.create(name='Toyota')
        brand.delete()
        self.assertFalse(Brand.objects.exists())

    def test_price_must_be_positive(self):
        from django.core.exceptions import ValidationError
        vehicle = Vehicle(name='Free car', brand=Brand.objects.create(name='Toyota'),
                          price_per_day=Decimal('0'), seats=4)
        with self.assertRaises(ValidationError):
            vehicle.full_clean()


class AdminRegistrationTests(TestCase):
    def test_models_are_registered_in_django_admin(self):
        self.assertIn(Brand, admin.site._registry)
        self.assertIn(Vehicle, admin.site._registry)


class CarListTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.toyota = Brand.objects.create(name='Toyota')
        cls.honda = Brand.objects.create(name='Honda')
        cls.camry = make_vehicle(cls.toyota, 'Camry', price='40000', seats=5)
        cls.hiace = make_vehicle(cls.toyota, 'Hiace', price='90000', seats=14, fuel=Vehicle.DIESEL)
        cls.civic = make_vehicle(cls.honda, 'Civic', price='35000', seats=5, available=False)
        cls.url = reverse('vehicles:car_list')

    def names(self, response):
        return [v.name for v in response.context['page_obj']]

    def test_guests_can_see_the_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(sorted(self.names(response)), ['Camry', 'Civic', 'Hiace'])

    def test_unavailable_vehicles_are_listed_but_marked(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Currently unavailable')

    def test_empty_list_shows_a_message(self):
        Vehicle.objects.all().delete()
        response = self.client.get(self.url)
        self.assertContains(response, 'No vehicles match your search')

    def test_filter_by_brand(self):
        response = self.client.get(self.url, {'brand': self.honda.pk})
        self.assertEqual(self.names(response), ['Civic'])

    def test_filter_by_min_price(self):
        response = self.client.get(self.url, {'min_price': '50000'})
        self.assertEqual(self.names(response), ['Hiace'])

    def test_filter_by_max_price(self):
        response = self.client.get(self.url, {'max_price': '40000'})
        self.assertEqual(sorted(self.names(response)), ['Camry', 'Civic'])

    def test_filter_by_price_range(self):
        response = self.client.get(self.url, {'min_price': '36000', 'max_price': '50000'})
        self.assertEqual(self.names(response), ['Camry'])

    def test_filter_by_seats_means_at_least(self):
        response = self.client.get(self.url, {'seats': '10'})
        self.assertEqual(self.names(response), ['Hiace'])

    def test_filter_available_only(self):
        response = self.client.get(self.url, {'available_only': 'on'})
        self.assertEqual(sorted(self.names(response)), ['Camry', 'Hiace'])

    def test_search_by_vehicle_name(self):
        response = self.client.get(self.url, {'q': 'civ'})
        self.assertEqual(self.names(response), ['Civic'])

    def test_search_by_brand_name(self):
        response = self.client.get(self.url, {'q': 'toyota'})
        self.assertEqual(sorted(self.names(response)), ['Camry', 'Hiace'])

    def test_filters_can_be_combined(self):
        response = self.client.get(
            self.url, {'brand': self.toyota.pk, 'seats': '5', 'available_only': 'on'})
        self.assertEqual(sorted(self.names(response)), ['Camry', 'Hiace'])

    def test_invalid_filter_values_do_not_crash(self):
        for params in ({'min_price': 'abc'}, {'seats': '-3'}, {'brand': '9999'},
                       {'min_price': '90000', 'max_price': '10000'}):
            with self.subTest(params=params):
                response = self.client.get(self.url, params)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context['form'].errors)

    def test_bad_page_numbers_do_not_crash(self):
        for page in ('abc', '999', '0'):
            with self.subTest(page=page):
                self.assertEqual(self.client.get(self.url, {'page': page}).status_code, 200)


class PaginationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        brand = Brand.objects.create(name='Toyota')
        for i in range(11):
            make_vehicle(brand, f'Car {i:02d}')
        cls.url = reverse('vehicles:car_list')

    def test_nine_vehicles_per_page(self):
        page_one = self.client.get(self.url)
        page_two = self.client.get(self.url, {'page': 2})
        self.assertEqual(len(page_one.context['page_obj']), 9)
        self.assertEqual(len(page_two.context['page_obj']), 2)

    def test_pages_do_not_overlap(self):
        first = {v.pk for v in self.client.get(self.url).context['page_obj']}
        second = {v.pk for v in self.client.get(self.url, {'page': 2}).context['page_obj']}
        self.assertFalse(first & second)

    def test_pagination_links_keep_the_filters(self):
        response = self.client.get(self.url, {'q': 'car', 'page': 1})
        self.assertContains(response, '?q=car&amp;page=2')


class CarDetailTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.brand = Brand.objects.create(name='Toyota')

    def test_guests_can_see_a_detail_page(self):
        vehicle = make_vehicle(self.brand, 'Camry', price='40000.50', seats=5,
                               description='Comfortable sedan.')
        response = self.client.get(reverse('vehicles:car_detail', args=[vehicle.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Toyota Camry')
        self.assertContains(response, '40000.50')
        self.assertContains(response, 'Comfortable sedan.')
        self.assertContains(response, 'Petrol')

    def test_unavailable_vehicle_is_marked_unavailable(self):
        vehicle = make_vehicle(self.brand, 'Camry', available=False)
        response = self.client.get(reverse('vehicles:car_detail', args=[vehicle.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Currently unavailable')

    def test_unknown_vehicle_returns_404(self):
        self.assertEqual(self.client.get(reverse('vehicles:car_detail', args=[999])).status_code, 404)

    def test_uploaded_image_is_saved_and_shown(self):
        with tempfile.TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            vehicle = make_vehicle(self.brand, 'Camry', image=tiny_image())
            response = self.client.get(reverse('vehicles:car_detail', args=[vehicle.pk]))
            self.assertTrue(vehicle.image.name.startswith('vehicles/'))
            self.assertContains(response, vehicle.image.url)


class HomePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        brand = Brand.objects.create(name='Toyota')
        cls.featured = make_vehicle(brand, 'Camry', featured=True)
        make_vehicle(brand, 'Corolla', featured=False)
        make_vehicle(brand, 'Avalon', featured=True, available=False)

    def test_home_page_loads(self):
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)

    def test_only_available_featured_vehicles_are_shown(self):
        response = self.client.get(reverse('home'))
        names = [v.name for v in response.context['featured_vehicles']]
        self.assertEqual(names, ['Camry'])

    def test_featured_partial_renders_the_vehicles_it_is_given(self):
        # Checks the partial itself, so this does not depend on Daniel's home.html.
        from django.template.loader import render_to_string
        from .views import featured_vehicles

        html = render_to_string(
            'vehicles/_featured_vehicles.html', {'featured_vehicles': featured_vehicles()})

        self.assertIn('Toyota Camry', html)
        self.assertNotIn('Corolla', html)
        self.assertNotIn('Avalon', html)

    def test_at_most_six_featured_vehicles(self):
        brand = Brand.objects.get(name='Toyota')
        for i in range(8):
            make_vehicle(brand, f'Extra {i}', featured=True)
        response = self.client.get(reverse('home'))
        self.assertEqual(len(response.context['featured_vehicles']), 6)

    def test_home_page_works_with_no_featured_vehicles(self):
        Vehicle.objects.update(is_featured=False)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['featured_vehicles']), 0)
