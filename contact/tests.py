"""
Tests for the contact app (Person 2): Contact Us, subscribers, page content
and contact details.

Run them with:
    python manage.py test contact
"""
from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Contact, ContactDetails, PageContent, Subscriber

QUERY = {'name': 'Ada', 'email': 'ada@example.com', 'message': 'Do you rent vans?'}


class ContactUsTests(TestCase):
    url = reverse('contact:contact_us')

    def test_page_loads_for_guests(self):
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_valid_message_is_saved(self):
        response = self.client.post(self.url, QUERY, follow=True)

        self.assertRedirects(response, self.url)
        query = Contact.objects.get()
        self.assertEqual((query.name, query.email, query.message),
                         ('Ada', 'ada@example.com', 'Do you rent vans?'))
        self.assertFalse(query.is_read)
        self.assertContains(response, 'Thank you for contacting us')

    def test_each_required_field_is_enforced(self):
        for field in QUERY:
            with self.subTest(field=field):
                response = self.client.post(self.url, {**QUERY, field: ''})
                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context['form'].errors)
                self.assertFalse(Contact.objects.exists())

    def test_invalid_email_is_rejected(self):
        response = self.client.post(self.url, {**QUERY, 'email': 'not-an-email'})
        self.assertIn('email', response.context['form'].errors)
        self.assertFalse(Contact.objects.exists())

    def test_form_is_prefilled_for_logged_in_users(self):
        user = User.objects.create_user('timi', 'timi@example.com', 'x', first_name='Timi', last_name='A')
        self.client.force_login(user)
        form = self.client.get(self.url).context['form']
        self.assertEqual(form.initial['name'], 'Timi A')
        self.assertEqual(form.initial['email'], 'timi@example.com')

    def test_page_shows_the_contact_details(self):
        ContactDetails.objects.create(
            address='1 Marina Road, Lagos', phone='0800 123 4567',
            email='hello@fastcars.test', working_hours='Mon-Sat 8am-6pm')
        response = self.client.get(self.url)
        for text in ('1 Marina Road, Lagos', '0800 123 4567', 'hello@fastcars.test',
                     'Mon-Sat 8am-6pm'):
            self.assertContains(response, text)

    def test_page_loads_before_any_details_are_entered(self):
        self.assertEqual(self.client.get(self.url).status_code, 200)


class SubscribeTests(TestCase):
    url = reverse('contact:subscribe')

    def test_subscribing_requires_post(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_valid_email_is_saved(self):
        response = self.client.post(self.url, {'email': 'ada@example.com'}, follow=True)

        self.assertRedirects(response, reverse('home'))
        self.assertEqual(Subscriber.objects.get().email, 'ada@example.com')
        self.assertContains(response, 'Thank you for subscribing')

    def test_email_is_stored_in_lower_case(self):
        self.client.post(self.url, {'email': 'Ada@Example.COM'})
        self.assertEqual(Subscriber.objects.get().email, 'ada@example.com')

    def test_duplicate_email_is_rejected(self):
        Subscriber.objects.create(email='ada@example.com')

        response = self.client.post(self.url, {'email': 'ada@example.com'}, follow=True)

        self.assertEqual(Subscriber.objects.count(), 1)
        self.assertContains(response, 'already subscribed')

    def test_duplicate_check_ignores_case(self):
        Subscriber.objects.create(email='ada@example.com')
        self.client.post(self.url, {'email': 'ADA@example.com'})
        self.assertEqual(Subscriber.objects.count(), 1)

    def test_invalid_email_is_rejected(self):
        response = self.client.post(self.url, {'email': 'nope'}, follow=True)
        self.assertFalse(Subscriber.objects.exists())
        self.assertEqual(response.status_code, 200)

    def test_missing_email_is_rejected(self):
        self.client.post(self.url, {})
        self.assertFalse(Subscriber.objects.exists())

    def test_redirects_back_to_the_page_it_came_from(self):
        response = self.client.post(
            self.url, {'email': 'ada@example.com', 'next': reverse('contact:contact_us')})
        self.assertRedirects(response, reverse('contact:contact_us'))

    def test_never_redirects_to_another_website(self):
        response = self.client.post(
            self.url, {'email': 'ada@example.com', 'next': 'https://evil.example.com/'})
        self.assertRedirects(response, reverse('home'))


class PageContentTests(TestCase):
    def test_page_shows_its_title_and_text(self):
        PageContent.objects.create(slug='about-us', title='About Us', body='We rent cars.\n\nSince 2020.')

        response = self.client.get(reverse('contact:page', args=['about-us']))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'About Us')
        self.assertContains(response, 'We rent cars.')
        self.assertContains(response, 'Since 2020.')

    def test_edited_text_is_shown(self):
        page = PageContent.objects.create(slug='about-us', title='About Us', body='Old text')
        page.body = 'New text'
        page.save()
        response = self.client.get(reverse('contact:page', args=['about-us']))
        self.assertContains(response, 'New text')
        self.assertNotContains(response, 'Old text')

    def test_unknown_page_returns_404(self):
        self.assertEqual(self.client.get(reverse('contact:page', args=['nope'])).status_code, 404)

    def test_html_in_the_body_is_escaped(self):
        PageContent.objects.create(slug='x', title='X', body='<script>alert(1)</script>')
        response = self.client.get(reverse('contact:page', args=['x']))
        self.assertNotContains(response, '<script>alert(1)</script>')


class ContactDetailsTests(TestCase):
    def test_load_creates_the_single_row(self):
        details = ContactDetails.load()
        self.assertEqual(details.pk, 1)
        self.assertEqual(ContactDetails.objects.count(), 1)

    def test_there_is_only_ever_one_row(self):
        ContactDetails.objects.create(phone='111')
        ContactDetails(phone='222').save()
        self.assertEqual(ContactDetails.objects.count(), 1)
        self.assertEqual(ContactDetails.load().phone, '222')

    def test_admin_cannot_add_a_second_set_of_details(self):
        model_admin = admin.site._registry[ContactDetails]
        request = type('R', (), {'user': None})()
        self.assertTrue(model_admin.has_add_permission(request))
        ContactDetails.load()
        self.assertFalse(model_admin.has_add_permission(request))


class AdminRegistrationTests(TestCase):
    def test_models_are_registered_in_django_admin(self):
        for model in (Contact, Subscriber, PageContent, ContactDetails):
            with self.subTest(model=model.__name__):
                self.assertIn(model, admin.site._registry)

    def test_contact_queries_cannot_be_added_in_the_admin(self):
        model_admin = admin.site._registry[Contact]
        self.assertFalse(model_admin.has_add_permission(None))


class DashboardIntegrationTests(TestCase):
    """The accounts admin dashboard counts these models by name, so check it sees them."""

    def test_dashboard_counts_subscribers_and_queries(self):
        Subscriber.objects.create(email='a@example.com')
        Subscriber.objects.create(email='b@example.com')
        Contact.objects.create(**QUERY)
        staff = User.objects.create_user('staffer', 's@example.com', 'x', is_staff=True)
        self.client.force_login(staff)

        response = self.client.get(reverse('accounts:admin_dashboard'))

        self.assertEqual(response.context['subscribers_count'], 2)
        self.assertEqual(response.context['queries_count'], 1)
