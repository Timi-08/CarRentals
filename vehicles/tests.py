from django.test import TestCase
from django.urls import reverse

from .models import Brand, Vehicle


class VehicleCatalogueTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.brand = Brand.objects.create(name='Honda')
        for number in range(21):
            Vehicle.objects.create(
                brand=cls.brand,
                name=f'Car {number:02}',
                price_per_day=100 + number,
                seats=5 if number % 2 == 0 else 2,
                fuel_type=Vehicle.FuelType.PETROL,
                available=number != 1,
                featured=number == 0,
                stock_image=Vehicle.StockImage.TOYOTA_COROLLA,
            )

    def test_listing_filters_and_preserves_filtered_pagination(self):
        response = self.client.get(
            reverse('vehicles:list'),
            {'brand': self.brand.pk, 'seats': 5, 'available': 'true'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.count, 11)
        self.assertContains(response, 'Car 00')
        self.assertNotContains(response, 'Car 01')
        self.assertContains(response, f'page=2&amp;q=&amp;brand={self.brand.pk}')

        next_page = self.client.get(
            reverse('vehicles:list'),
            {'page': 2, 'brand': self.brand.pk, 'seats': 5, 'available': 'true'},
        )
        self.assertEqual(next_page.context['page_obj'].number, 2)
        self.assertEqual(len(next_page.context['page_obj'].object_list), 2)

    def test_search_and_price_filters(self):
        response = self.client.get(
            reverse('vehicles:list'),
            {'q': 'Honda', 'min_price': '105', 'max_price': '108'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.count, 4)

    def test_detail_and_home_featured_cars_are_public(self):
        vehicle = Vehicle.objects.get(name='Car 00')
        detail = self.client.get(reverse('vehicles:detail', args=[vehicle.pk]))
        home = self.client.get(reverse('home'))

        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, 'Honda Car 00')
        self.assertContains(detail, 'src="/static/usnpx-2026toyotacorolla-angularfront-zd.webp"')
        self.assertEqual(home.status_code, 200)
        self.assertContains(home, 'Honda Car 00')
        self.assertContains(home, 'src="/static/usnpx-2026toyotacorolla-angularfront-zd.webp"')
