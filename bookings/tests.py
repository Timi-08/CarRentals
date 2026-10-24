from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.db import IntegrityError, transaction

from vehicles.models import Vehicle
from .models import Booking

PASSWORD = 'pass12345!'


def future(days):
    """A date `days` from today."""
    return timezone.localdate() + timedelta(days=days)


# Faster password hashing, for tests only (the real site is unaffected)
@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class BookingBase(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user('alice', password=PASSWORD)
        self.bob = User.objects.create_user('bob', password=PASSWORD)
        self.admin = User.objects.create_user('boss', password=PASSWORD, is_staff=True)
        self.car = Vehicle.objects.create(
            name='Camry', price_per_day=Decimal('100.00'), is_available=True)

    def make(self, start=5, end=8, user=None, status=Booking.PENDING, vehicle=None):
        """Create a booking directly in the DB (skips form validation)."""
        return Booking.objects.create(
            customer=user or self.alice, vehicle=vehicle or self.car,
            pickup_date=future(start), return_date=future(end),
            location='Lagos', status=status)

    def candidate(self, start, end, vehicle=None):
        """An unsaved booking, used to test validation."""
        return Booking(customer=self.alice, vehicle=vehicle or self.car,
                       pickup_date=future(start), return_date=future(end),
                       location='Lagos')


class BookingModelTests(BookingBase):
    def test_total_price_is_days_times_rate(self):  # BKG-06
        self.assertEqual(self.make(5, 8).total_price, Decimal('300.00'))

    def test_new_booking_defaults_to_pending(self):  # BKG-07
        self.assertEqual(self.make().status, Booking.PENDING)

    def test_past_pickup_rejected(self):  # BKG-03
        with self.assertRaises(ValidationError):
            self.candidate(-1, 2).clean()

    def test_return_before_pickup_rejected(self):  # BKG-03
        with self.assertRaises(ValidationError):
            self.candidate(5, 3).clean()

    def test_same_day_return_rejected(self):  # BKG-03
        with self.assertRaises(ValidationError):
            self.candidate(5, 5).clean()

    def test_unavailable_vehicle_rejected(self):  # BKG-04
        self.car.is_available = False
        self.car.save()
        with self.assertRaises(ValidationError):
            self.candidate(5, 8).clean()

    def test_overlap_with_pending_rejected(self):  # BKG-05
        self.make(5, 8)
        with self.assertRaises(ValidationError):
            self.candidate(6, 9).clean()

    def test_overlap_with_confirmed_rejected(self):  # BKG-05
        self.make(5, 8, status=Booking.CONFIRMED)
        with self.assertRaises(ValidationError):
            self.candidate(4, 6).clean()

    def test_cancelled_booking_does_not_block(self):  # BKG-05
        self.make(5, 8, status=Booking.CANCELLED)
        self.candidate(5, 8).clean()  # should not raise

    def test_back_to_back_booking_allowed(self):  # BKG-05
        self.make(5, 8)
        self.candidate(8, 10).clean()  # pickup on the previous return day

    def test_same_dates_other_vehicle_allowed(self):  # BKG-05
        other = Vehicle.objects.create(
            name='Corolla', price_per_day=Decimal('80.00'), is_available=True)
        self.make(5, 8)
        self.candidate(5, 8, vehicle=other).clean()


class BookingViewTests(BookingBase):
    def login(self, name):
        self.client.login(username=name, password=PASSWORD)

    def test_guest_redirected_to_login(self):  # BKG-01
        url = reverse('bookings:create')
        resp = self.client.get(url)
        self.assertRedirects(resp, f"{reverse('accounts:login')}?next={url}")

    def test_customer_can_book(self):  # BKG-02, BKG-07
        self.login('alice')
        resp = self.client.post(reverse('bookings:create'), {
            'vehicle': self.car.pk,
            'pickup_date': future(5).isoformat(),
            'return_date': future(8).isoformat(),
            'location': 'Ikeja'})
        b = Booking.objects.get()
        self.assertRedirects(resp, reverse('bookings:confirmation', args=[b.pk]))
        self.assertEqual((b.customer, b.status, b.location),
                         (self.alice, Booking.PENDING, 'Ikeja'))

    def test_invalid_booking_not_saved(self):  # BKG-03
        self.login('alice')
        self.client.post(reverse('bookings:create'), {
            'vehicle': self.car.pk,
            'pickup_date': future(-2).isoformat(),
            'return_date': future(1).isoformat(),
            'location': 'Ikeja'})
        self.assertEqual(Booking.objects.count(), 0)

    def test_overlapping_booking_not_saved(self):  # BKG-05
        self.make(5, 8, user=self.bob)
        self.login('alice')
        self.client.post(reverse('bookings:create'), {
            'vehicle': self.car.pk,
            'pickup_date': future(6).isoformat(),
            'return_date': future(9).isoformat(),
            'location': 'Ikeja'})
        self.assertEqual(Booking.objects.count(), 1)

    def test_customer_sees_only_own_bookings(self):  # BKG-10
        self.make(5, 8, user=self.alice)
        self.make(10, 12, user=self.bob)
        self.login('alice')
        resp = self.client.get(reverse('bookings:my_bookings'))
        self.assertEqual(len(resp.context['bookings']), 1)
        self.assertEqual(resp.context['bookings'][0].customer, self.alice)

    def test_customer_cannot_open_another_users_confirmation(self):  # NFR-02
        b = self.make(user=self.bob)
        self.login('alice')
        resp = self.client.get(reverse('bookings:confirmation', args=[b.pk]))
        self.assertEqual(resp.status_code, 404)

    def test_customer_can_cancel_own_pending(self):  # BKG-09
        b = self.make()
        self.login('alice')
        self.client.post(reverse('bookings:cancel', args=[b.pk]))
        b.refresh_from_db()
        self.assertEqual(b.status, Booking.CANCELLED)

    def test_customer_cannot_cancel_confirmed(self):  # BKG-09
        b = self.make(status=Booking.CONFIRMED)
        self.login('alice')
        self.client.post(reverse('bookings:cancel', args=[b.pk]))
        b.refresh_from_db()
        self.assertEqual(b.status, Booking.CONFIRMED)

    def test_customer_cannot_cancel_another_users_booking(self):  # BKG-12
        b = self.make(user=self.bob)
        self.login('alice')
        resp = self.client.post(reverse('bookings:cancel', args=[b.pk]))
        self.assertEqual(resp.status_code, 404)
        b.refresh_from_db()
        self.assertEqual(b.status, Booking.PENDING)

    def test_customer_cannot_confirm_booking(self):  # BKG-12, ADM-07
        b = self.make()
        self.login('alice')
        self.client.post(reverse('bookings:admin_update', args=[b.pk, 'confirm']))
        b.refresh_from_db()
        self.assertEqual(b.status, Booking.PENDING)

    def test_customer_blocked_from_manage_page(self):  # ADM-07
        self.login('alice')
        resp = self.client.get(reverse('bookings:manage'))
        self.assertEqual(resp.status_code, 302)

    def test_guest_blocked_from_manage_page(self):  # ADM-07
        resp = self.client.get(reverse('bookings:manage'))
        self.assertEqual(resp.status_code, 302)

    def test_admin_sees_all_bookings(self):  # BKG-11
        self.make(5, 8, user=self.alice)
        self.make(10, 12, user=self.bob)
        self.login('boss')
        resp = self.client.get(reverse('bookings:manage'))
        self.assertEqual(len(resp.context['bookings']), 2)

    def test_admin_can_confirm_and_cancel(self):  # BKG-08
        b1, b2 = self.make(5, 8), self.make(10, 12)
        self.login('boss')
        self.client.post(reverse('bookings:admin_update', args=[b1.pk, 'confirm']))
        self.client.post(reverse('bookings:admin_update', args=[b2.pk, 'cancel']))
        b1.refresh_from_db(); b2.refresh_from_db()
        self.assertEqual(b1.status, Booking.CONFIRMED)
        self.assertEqual(b2.status, Booking.CANCELLED)

    def test_full_workflow(self):  # Acceptance criterion 3
        self.login('alice')
        self.client.post(reverse('bookings:create'), {
            'vehicle': self.car.pk,
            'pickup_date': future(5).isoformat(),
            'return_date': future(7).isoformat(),
            'location': 'Lekki'})
        b = Booking.objects.get()
        self.client.logout()
        self.login('boss')
        self.client.post(reverse('bookings:admin_update', args=[b.pk, 'confirm']))
        self.client.logout()
        self.login('alice')
        resp = self.client.get(reverse('bookings:my_bookings'))
        self.assertEqual(resp.context['bookings'][0].status, Booking.CONFIRMED)

    # ---- NEW tests (pagination and available-only vehicles) ----

    def test_unavailable_vehicle_not_offered_in_form(self):  # BKG-04
        gone = Vehicle.objects.create(
            name='Old Van', price_per_day=Decimal('50.00'), is_available=False)
        self.login('alice')
        resp = self.client.get(reverse('bookings:create'))
        choices = resp.context['form'].fields['vehicle'].queryset
        self.assertIn(self.car, choices)
        self.assertNotIn(gone, choices)

    def test_my_bookings_is_paginated(self):  # NFR-04
        for i in range(12):
            self.make(i * 3 + 1, i * 3 + 3)
        self.login('alice')
        url = reverse('bookings:my_bookings')
        self.assertEqual(len(self.client.get(url).context['bookings']), 10)
        self.assertEqual(len(self.client.get(url + '?page=2').context['bookings']), 2)

    def test_manage_bookings_is_paginated_and_filterable(self):  # NFR-04, BKG-11
        for i in range(12):
            self.make(i * 3 + 1, i * 3 + 3)
        self.make(50, 52, status=Booking.CANCELLED)
        self.login('boss')
        url = reverse('bookings:manage')
        self.assertEqual(len(self.client.get(url).context['bookings']), 10)
        cancelled = self.client.get(url + '?status=Cancelled')
        self.assertEqual(len(cancelled.context['bookings']), 1)

class BookingDatabaseRuleTests(BookingBase):
    def test_database_rejects_bad_date_range(self):  # NFR-06
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.make(8, 5)  # return before pickup, skips form validation