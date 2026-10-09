from django.contrib.auth import SESSION_KEY
from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase, override_settings
from django.urls import reverse

from .models import Profile

@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class TestCase(DjangoTestCase):
    pass

PASSWORD = 'Str0ng-Pass!234'
NEW_PASSWORD = 'An0ther-Str0ng!567'


def registration_data(**overrides):
    """Valid registration form data; override any field per test."""
    data = {
        'username': 'timi',
        'first_name': 'Timi',
        'last_name': 'Alegbeleye',
        'email': 'timi@example.com',
        'phone': '08012345678',
        'password1': PASSWORD,
        'password2': PASSWORD,
    }
    data.update(overrides)
    return data


def is_logged_in(client):
    return SESSION_KEY in client.session


class RegistrationTests(TestCase):
    def test_register_page_loads(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)

    def test_registration_creates_user_and_profile(self):
        response = self.client.post(reverse('accounts:register'), registration_data())

        self.assertRedirects(response, reverse('home'))
        user = User.objects.get(username='timi')
        self.assertEqual(user.email, 'timi@example.com')
        self.assertEqual(user.first_name, 'Timi')
        self.assertTrue(user.check_password(PASSWORD))
        self.assertFalse(user.is_staff)
        self.assertEqual(Profile.objects.filter(user=user).count(), 1)
        self.assertEqual(user.profile.phone, '08012345678')

    def test_registration_logs_the_new_user_in(self):
        self.client.post(reverse('accounts:register'), registration_data())
        self.assertTrue(is_logged_in(self.client))

    def test_phone_is_optional(self):
        response = self.client.post(reverse('accounts:register'), registration_data(phone=''))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(User.objects.get(username='timi').profile.phone, '')

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user('existing', 'timi@example.com', PASSWORD)

        response = self.client.post(reverse('accounts:register'), registration_data())

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email',
                             'An account with this email already exists.')
        self.assertFalse(User.objects.filter(username='timi').exists())
        self.assertFalse(is_logged_in(self.client))

    def test_duplicate_email_check_ignores_case(self):
        User.objects.create_user('existing', 'timi@example.com', PASSWORD)

        response = self.client.post(
            reverse('accounts:register'), registration_data(email='TIMI@Example.COM'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.context['form'].errors)
        self.assertFalse(User.objects.filter(username='timi').exists())

    def test_duplicate_username_is_rejected(self):
        User.objects.create_user('timi', 'someone@example.com', PASSWORD)

        response = self.client.post(reverse('accounts:register'), registration_data())

        self.assertEqual(response.status_code, 200)
        self.assertIn('username', response.context['form'].errors)
        self.assertEqual(User.objects.filter(username='timi').count(), 1)

    def test_mismatched_passwords_are_rejected(self):
        response = self.client.post(
            reverse('accounts:register'), registration_data(password2='Different-Pass!999'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('password2', response.context['form'].errors)
        self.assertFalse(User.objects.filter(username='timi').exists())

    def test_weak_password_is_rejected(self):
        response = self.client.post(
            reverse('accounts:register'), registration_data(password1='12345', password2='12345'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertFalse(User.objects.filter(username='timi').exists())

    def test_required_fields_are_enforced(self):
        for field in ('first_name', 'last_name', 'email'):
            with self.subTest(field=field):
                response = self.client.post(
                    reverse('accounts:register'), registration_data(**{field: ''}))
                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context['form'].errors)
                self.assertFalse(User.objects.filter(username='timi').exists())

    def test_logged_in_user_is_redirected_away_from_register(self):
        User.objects.create_user('timi', 'timi@example.com', PASSWORD)
        self.client.login(username='timi', password=PASSWORD)

        response = self.client.get(reverse('accounts:register'))

        self.assertRedirects(response, reverse('home'))


class ProfileSignalTests(TestCase):
    def test_every_new_user_gets_a_profile(self):
        user = User.objects.create_user('someone', 'someone@example.com', PASSWORD)
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_saving_an_existing_user_does_not_create_a_second_profile(self):
        user = User.objects.create_user('someone', 'someone@example.com', PASSWORD)
        user.first_name = 'Changed'
        user.save()
        self.assertEqual(Profile.objects.filter(user=user).count(), 1)

    def test_deleting_a_user_deletes_the_profile(self):
        user = User.objects.create_user('someone', 'someone@example.com', PASSWORD)
        user.delete()
        self.assertEqual(Profile.objects.count(), 0)


class LoginLogoutTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('timi', 'timi@example.com', PASSWORD)

    def test_login_page_loads(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_with_correct_details_works(self):
        response = self.client.post(
            reverse('accounts:login'), {'username': 'timi', 'password': PASSWORD})

        self.assertRedirects(response, reverse('home'))
        self.assertTrue(is_logged_in(self.client))
        self.assertEqual(int(self.client.session[SESSION_KEY]), self.user.pk)

    def test_login_with_wrong_password_fails(self):
        response = self.client.post(
            reverse('accounts:login'), {'username': 'timi', 'password': 'wrong-password'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertFalse(is_logged_in(self.client))

    def test_login_with_unknown_user_fails(self):
        response = self.client.post(
            reverse('accounts:login'), {'username': 'nobody', 'password': PASSWORD})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(is_logged_in(self.client))

    def test_login_respects_next_parameter(self):
        url = reverse('accounts:login') + '?next=' + reverse('accounts:profile')
        response = self.client.post(url, {'username': 'timi', 'password': PASSWORD})
        self.assertRedirects(response, reverse('accounts:profile'))

    def test_logout_with_post_logs_the_user_out(self):
        self.client.login(username='timi', password=PASSWORD)

        response = self.client.post(reverse('accounts:logout'))

        self.assertRedirects(response, reverse('home'))
        self.assertFalse(is_logged_in(self.client))

    def test_logout_requires_post(self):
        self.client.login(username='timi', password=PASSWORD)

        response = self.client.get(reverse('accounts:logout'))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(is_logged_in(self.client))


class ProfileTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            'timi', 'timi@example.com', PASSWORD, first_name='Timi', last_name='Alegbeleye')
        cls.user.profile.phone = '08012345678'
        cls.user.profile.address = '1 Marina Road, Lagos'
        cls.user.profile.save()

    def setUp(self):
        self.client.login(username='timi', password=PASSWORD)

    def test_profile_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:profile'))
        expected = reverse('accounts:login') + '?next=' + reverse('accounts:profile')
        self.assertRedirects(response, expected)

    def test_profile_edit_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:profile_edit'))
        expected = reverse('accounts:login') + '?next=' + reverse('accounts:profile_edit')
        self.assertRedirects(response, expected)

    def test_user_can_view_their_profile(self):
        response = self.client.get(reverse('accounts:profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'timi')
        self.assertContains(response, 'timi@example.com')
        self.assertContains(response, '08012345678')
        self.assertContains(response, '1 Marina Road, Lagos')

    def test_profile_only_shows_the_logged_in_users_details(self):
        other = User.objects.create_user('other', 'other@example.com', PASSWORD)
        other.profile.phone = '09099999999'
        other.profile.save()

        response = self.client.get(reverse('accounts:profile'))

        self.assertNotContains(response, 'other@example.com')
        self.assertNotContains(response, '09099999999')

    def test_edit_page_is_prefilled(self):
        response = self.client.get(reverse('accounts:profile_edit'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['u_form'].instance, self.user)
        self.assertEqual(response.context['p_form'].instance, self.user.profile)
        self.assertContains(response, 'timi@example.com')

    def test_user_can_update_their_profile(self):
        response = self.client.post(reverse('accounts:profile_edit'), {
            'first_name': 'Timilehin',
            'last_name': 'A.',
            'email': 'new@example.com',
            'phone': '08111111111',
            'address': '5 New Street, Abuja',
        })

        self.assertRedirects(response, reverse('accounts:profile'))
        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Timilehin')
        self.assertEqual(self.user.last_name, 'A.')
        self.assertEqual(self.user.email, 'new@example.com')
        self.assertEqual(self.user.profile.phone, '08111111111')
        self.assertEqual(self.user.profile.address, '5 New Street, Abuja')

    def test_update_does_not_change_the_username(self):
        self.client.post(reverse('accounts:profile_edit'), {
            'first_name': 'Timi', 'last_name': 'A', 'email': 'timi@example.com',
            'phone': '', 'address': '', 'username': 'hacked',
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'timi')

    def test_invalid_update_is_rejected_and_nothing_changes(self):
        response = self.client.post(reverse('accounts:profile_edit'), {
            'first_name': 'Timi',
            'last_name': 'A',
            'email': 'not-an-email',
            'phone': '08111111111',
            'address': 'Somewhere else',
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.context['u_form'].errors)
        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.email, 'timi@example.com')
        self.assertEqual(self.user.profile.phone, '08012345678')


class PasswordChangeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('timi', 'timi@example.com', PASSWORD)

    def setUp(self):
        self.client.login(username='timi', password=PASSWORD)

    def change_password_data(self, **overrides):
        data = {
            'old_password': PASSWORD,
            'new_password1': NEW_PASSWORD,
            'new_password2': NEW_PASSWORD,
        }
        data.update(overrides)
        return data

    def test_password_change_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:password_change'))
        expected = reverse('accounts:login') + '?next=' + reverse('accounts:password_change')
        self.assertRedirects(response, expected)

    def test_password_change_page_loads(self):
        response = self.client.get(reverse('accounts:password_change'))
        self.assertEqual(response.status_code, 200)

    def test_user_can_change_their_password(self):
        response = self.client.post(
            reverse('accounts:password_change'), self.change_password_data())

        self.assertRedirects(response, reverse('accounts:profile'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))
        self.assertFalse(self.user.check_password(PASSWORD))

    def test_user_stays_logged_in_after_changing_password(self):
        self.client.post(reverse('accounts:password_change'), self.change_password_data())
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)

    def test_user_can_log_in_with_the_new_password(self):
        self.client.post(reverse('accounts:password_change'), self.change_password_data())
        self.client.logout()

        self.assertTrue(self.client.login(username='timi', password=NEW_PASSWORD))
        self.assertFalse(self.client.login(username='timi', password=PASSWORD))

    def test_wrong_old_password_is_rejected(self):
        response = self.client.post(
            reverse('accounts:password_change'),
            self.change_password_data(old_password='not-my-password'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('old_password', response.context['form'].errors)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD))

    def test_mismatched_new_passwords_are_rejected(self):
        response = self.client.post(
            reverse('accounts:password_change'),
            self.change_password_data(new_password2='Different-Pass!999'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('new_password2', response.context['form'].errors)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD))


class AdminAccessTests(TestCase):
    """The admin dashboard and registered-user list are for staff only."""

    @classmethod
    def setUpTestData(cls):
        cls.customer = User.objects.create_user(
            'customer', 'customer@example.com', PASSWORD, first_name='Cora', last_name='Customer')
        cls.staff = User.objects.create_user(
            'staffer', 'staff@example.com', PASSWORD, is_staff=True)

    PROTECTED = ('accounts:admin_dashboard', 'accounts:admin_user_list',
                    'accounts:admin_password_change')

    def assert_sent_to_admin_login(self, response, url_name):
        expected = reverse('accounts:admin_login') + '?next=' + reverse(url_name)
        self.assertRedirects(response, expected)

    def test_anonymous_users_are_sent_to_admin_login(self):
        for url_name in self.PROTECTED:
            with self.subTest(url=url_name):
                response = self.client.get(reverse(url_name))
                self.assert_sent_to_admin_login(response, url_name)

    def test_non_staff_users_cannot_access_admin_pages(self):
        self.client.login(username='customer', password=PASSWORD)
        for url_name in self.PROTECTED:
            with self.subTest(url=url_name):
                response = self.client.get(reverse(url_name))
                self.assert_sent_to_admin_login(response, url_name)

    def test_staff_can_open_the_dashboard(self):
        self.client.login(username='staffer', password=PASSWORD)
        response = self.client.get(reverse('accounts:admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_staff_can_open_the_registered_user_list(self):
        self.client.login(username='staffer', password=PASSWORD)
        response = self.client.get(reverse('accounts:admin_user_list'))
        self.assertEqual(response.status_code, 200)

    def test_staff_can_open_the_admin_password_change_page(self):
        self.client.login(username='staffer', password=PASSWORD)
        response = self.client.get(reverse('accounts:admin_password_change'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_counts_customers_but_not_staff(self):
        User.objects.create_user('second', 'second@example.com', PASSWORD)
        self.client.login(username='staffer', password=PASSWORD)

        response = self.client.get(reverse('accounts:admin_dashboard'))

        self.assertEqual(response.context['users_count'], 2)

    def test_user_list_shows_customers_and_hides_staff(self):
        self.client.login(username='staffer', password=PASSWORD)

        response = self.client.get(reverse('accounts:admin_user_list'))

        self.assertContains(response, 'customer@example.com')
        self.assertNotContains(response, 'staff@example.com')

    def test_user_list_shows_newest_users_first(self):
        User.objects.create_user('newest', 'newest@example.com', PASSWORD)
        self.client.login(username='staffer', password=PASSWORD)

        response = self.client.get(reverse('accounts:admin_user_list'))

        usernames = [u.username for u in response.context['page_obj']]
        self.assertEqual(usernames, ['newest', 'customer'])

    def test_user_list_is_paginated_by_ten(self):
        for i in range(12):
            User.objects.create_user(f'bulk{i}', f'bulk{i}@example.com', PASSWORD)
        self.client.login(username='staffer', password=PASSWORD)

        page_one = self.client.get(reverse('accounts:admin_user_list'))
        page_two = self.client.get(reverse('accounts:admin_user_list') + '?page=2')

        # 13 customers in total: 10 on page one, 3 on page two.
        self.assertEqual(len(page_one.context['page_obj']), 10)
        self.assertEqual(len(page_two.context['page_obj']), 3)

    def test_admin_logout_requires_post(self):
        self.client.login(username='staffer', password=PASSWORD)
        response = self.client.get(reverse('accounts:admin_logout'))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(is_logged_in(self.client))

    def test_admin_logout_with_post_logs_staff_out(self):
        self.client.login(username='staffer', password=PASSWORD)

        response = self.client.post(reverse('accounts:admin_logout'))

        self.assertRedirects(response, reverse('accounts:admin_login'))
        self.assertFalse(is_logged_in(self.client))


class AdminLoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = User.objects.create_user('customer', 'customer@example.com', PASSWORD)
        cls.staff = User.objects.create_user(
            'staffer', 'staff@example.com', PASSWORD, is_staff=True)

    def test_admin_login_page_loads(self):
        response = self.client.get(reverse('accounts:admin_login'))
        self.assertEqual(response.status_code, 200)

    def test_staff_can_log_in_and_reach_the_dashboard(self):
        response = self.client.post(
            reverse('accounts:admin_login'), {'username': 'staffer', 'password': PASSWORD})

        self.assertRedirects(response, reverse('accounts:admin_dashboard'))
        self.assertTrue(is_logged_in(self.client))

    def test_non_staff_account_is_rejected(self):
        response = self.client.post(
            reverse('accounts:admin_login'), {'username': 'customer', 'password': PASSWORD})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'does not have administrator access')
        self.assertFalse(is_logged_in(self.client))

    def test_non_staff_account_cannot_reach_dashboard_after_a_rejected_login(self):
        self.client.post(
            reverse('accounts:admin_login'), {'username': 'customer', 'password': PASSWORD})

        response = self.client.get(reverse('accounts:admin_dashboard'))

        self.assertEqual(response.status_code, 302)

    def test_wrong_password_is_rejected_for_staff(self):
        response = self.client.post(
            reverse('accounts:admin_login'), {'username': 'staffer', 'password': 'wrong'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertFalse(is_logged_in(self.client))