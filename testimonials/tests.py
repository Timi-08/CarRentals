from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Testimonial


# Faster password hashing, for tests only
@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class TestimonialTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('alice', password='pass12345!')
        self.admin = User.objects.create_superuser('boss', 'b@x.com', 'pass12345!')

    def test_guest_redirected_to_login(self):  # TST-01
        url = reverse('testimonials:create')
        resp = self.client.get(url)
        self.assertRedirects(resp, f"{reverse('accounts:login')}?next={url}")

    def test_customer_can_post_and_it_starts_inactive(self):  # TST-01, TST-03
        self.client.login(username='alice', password='pass12345!')
        self.client.post(reverse('testimonials:create'), {'message': 'Great service'})
        t = Testimonial.objects.get()
        self.assertEqual(t.user, self.user)
        self.assertFalse(t.is_active)

    def test_only_active_testimonials_are_public(self):  # TST-02, TST-03
        Testimonial.objects.create(user=self.user, message='Visible one', is_active=True)
        Testimonial.objects.create(user=self.user, message='Hidden one', is_active=False)
        resp = self.client.get(reverse('testimonials:list'))
        self.assertContains(resp, 'Visible one')
        self.assertNotContains(resp, 'Hidden one')

    def test_admin_can_activate_and_deactivate(self):  # TST-03
        t = Testimonial.objects.create(user=self.user, message='Hello')
        self.client.login(username='boss', password='pass12345!')
        url = reverse('admin:testimonials_testimonial_changelist')
        self.client.post(url, {'action': 'activate', '_selected_action': [t.pk]})
        t.refresh_from_db()
        self.assertTrue(t.is_active)
        self.client.post(url, {'action': 'deactivate', '_selected_action': [t.pk]})
        t.refresh_from_db()
        self.assertFalse(t.is_active)

    def test_list_is_paginated(self):  # NFR-04
        for i in range(8):
            Testimonial.objects.create(user=self.user, message=f'Review {i}', is_active=True)
        url = reverse('testimonials:list')
        self.assertEqual(len(self.client.get(url).context['testimonials']), 6)
        self.assertEqual(len(self.client.get(url + '?page=2').context['testimonials']), 2)