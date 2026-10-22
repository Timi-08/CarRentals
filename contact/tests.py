from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Contact, SiteContent, Subscriber


class ContactTests(TestCase):
    def test_guest_can_submit_contact_message(self):
        response = self.client.post(
            reverse('contact:contact'),
            {
                'name': 'Guest Driver',
                'email': 'guest@example.com',
                'subject': 'Rental question',
                'message': 'Can I rent a car next week?',
            },
        )

        self.assertRedirects(response, reverse('contact:contact'))
        message = Contact.objects.get()
        self.assertIsNone(message.user)
        self.assertEqual(message.status, Contact.Status.NEW)

    def test_authenticated_message_is_linked_to_user_and_contact_details_are_shown(self):
        user = User.objects.create_user(username='driver', email='driver@example.com')
        self.client.force_login(user)
        SiteContent.objects.create(pk=1, contact_phone='+1 555 0100')

        response = self.client.get(reverse('contact:contact'))

        self.assertContains(response, '+1 555 0100')
        self.assertContains(response, 'driver@example.com')

        self.client.post(
            reverse('contact:contact'),
            {
                'name': 'Driver',
                'email': 'driver@example.com',
                'subject': 'Question',
                'message': 'Please contact me.',
            },
        )
        self.assertEqual(Contact.objects.get().user, user)

    def test_subscriber_email_is_normalized_and_duplicate_is_rejected(self):
        response = self.client.post(
            reverse('contact:subscribe'), {'email': 'Driver@Example.com'}
        )

        self.assertRedirects(response, reverse('contact:contact'))
        self.assertEqual(Subscriber.objects.get().email, 'driver@example.com')

        response = self.client.post(
            reverse('contact:subscribe'), {'email': 'DRIVER@example.com'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already subscribed')
        self.assertEqual(Subscriber.objects.count(), 1)

    def test_staff_can_edit_site_content_in_admin(self):
        staff = User.objects.create_superuser(
            username='siteadmin', email='admin@example.com', password='admin-password'
        )
        SiteContent.objects.create(pk=1)
        self.client.force_login(staff)

        url = reverse('admin:contact_sitecontent_change', args=[1])
        response = self.client.post(
            url,
            {
                'homepage_title': 'Drive with us',
                'homepage_intro': 'Updated home page copy.',
                'contact_email': 'help@example.com',
                'contact_phone': '+1 555 0100',
                'contact_address': '1 Main Street',
                '_save': 'Save',
            },
        )

        self.assertRedirects(response, reverse('admin:contact_sitecontent_changelist'))
        content = SiteContent.objects.get(pk=1)
        self.assertEqual(content.homepage_title, 'Drive with us')
        self.assertEqual(content.contact_email, 'help@example.com')
