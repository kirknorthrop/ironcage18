from django.test import TestCase

from . import factories
from tickets.tests.factories import create_confirmed_order_for_self


class ProfileTests(TestCase):
    def test_get_profile_when_not_authenticated(self):
        rsp = self.client.get('/profile/', follow=True)
        self.assertRedirects(rsp, '/accounts/login/?next=/profile/')

    def test_get_profile_for_user_with_empty_profile(self):
        self.client.force_login(factories.create_user(email_addr='alice@example.com'))
        rsp = self.client.get('/profile/')
        for k, v in [
            ['Name', 'Alice'],
            ['Email', 'alice@example.com'],
            ['Company', 'None'],
            ['Twitter', 'None'],
            ['Pronoun', 'None'],
            ['Accessibility', 'unknown'],
            ['Childcare', 'unknown'],
            ['Dietary', 'unknown'],
            ['Year of birth', 'unknown'],
            ['Gender', 'unknown'],
            ['Ethnicity', 'unknown'],
            ['Nationality', 'unknown'],
            ['Country of residence', 'unknown'],
        ]:
            self.assertContains(rsp, f'<div class="col-4 field-name">{k}</div><div class="col-8">{v}</div>', html=True)
        self.assertNotContains(rsp, 'You have opted not to share demographic information with us')

    def test_get_profile_for_user_with_full_profile(self):
        self.client.force_login(factories.create_user_with_full_profile(email_addr='alice@example.com'))
        rsp = self.client.get('/profile/')
        for k, v in [
            ['Name', 'Alice'],
            ['Email', 'alice@example.com'],
            ['Company', 'MegaCorp'],
            ['Twitter', '@alice'],
            ['Pronoun', 'she/her'],
            ['Accessibility', 'none'],
            ['Childcare', 'none'],
            ['Dietary', 'Vegan'],
            ['Year of birth', '1985'],
            ['Gender', 'Female'],
            ['Ethnicity', 'White and Black Caribbean'],
            ['Nationality', 'British'],
            ['Country of residence', 'United Kingdom'],
        ]:
            self.assertContains(rsp, f'<div class="col-4 field-name">{k}</div><div class="col-8">{v}</div>', html=True)
        self.assertNotContains(rsp, 'You have opted not to share demographic information with us')

    def test_get_profile_for_user_with_dont_ask_demographics_set(self):
        self.client.force_login(factories.create_user_with_dont_ask_demographics_set())
        rsp = self.client.get('/profile/')
        self.assertContains(rsp, 'You have opted not to share demographic information with us')

    def test_get_snake_allocated(self):
        alice = factories.create_user()
        self.client.force_login(alice)

        self.client.get('/profile/')

        alice.refresh_from_db()

        self.assertTrue(alice.badge_snake_colour in ['red', 'blue', 'orange', 'yellow', 'green', 'purple'])
        self.assertTrue(alice.badge_snake_extras in ['deerstalker', 'glasses', 'mortar', 'astronaut', 'crown', 'dragon'])


class EditProfileTests(TestCase):
    def test_post_update(self):
        alice = factories.create_user(year_of_birth='1985')
        self.client.force_login(alice)

        data = {
            'name': 'Alice',
            'email_addr': 'alice@example.com',
            'year_of_birth': '1986',
            'gender': 'agender',
            'ethnicity': 'Any other ethnic group, please describe',
            'ethnicity_free_text': 'Abkhazian',
            'country_of_residence': 'Abkhazia',
            'nationality': 'Abkhazian',
        }
        self.client.post('/profile/edit/', data, follow=True)
        alice.refresh_from_db()

        self.assertEqual(alice.year_of_birth, '1986')
        self.assertEqual(alice.gender, 'agender')
        self.assertEqual(alice.ethnicity, 'Any other ethnic group, please describe')
        self.assertEqual(alice.ethnicity_free_text, 'Abkhazian')
        self.assertEqual(alice.country_of_residence, 'Abkhazia')
        self.assertEqual(alice.nationality, 'Abkhazian')
        self.assertEqual(alice.dont_ask_demographics, False)

    def test_post_dont_ask_demographics(self):
        alice = factories.create_user(year_of_birth='1985')
        self.client.force_login(alice)

        data = {
            'name': 'Alice',
            'email_addr': 'alice@example.com',
            'year_of_birth': '1986',
            'gender': 'agender',
            'ethnicity': 'Any other ethnic group, please describe',
            'ethnicity_free_text': 'Abkhazian',
            'country_of_residence': 'Abkhazia',
            'nationality': 'Abkhazian',
            'dont_ask_demographics': 'on',
        }
        self.client.post('/profile/edit/', data, follow=True)
        alice.refresh_from_db()

        self.assertIsNone(alice.year_of_birth)
        self.assertIsNone(alice.gender)
        self.assertIsNone(alice.ethnicity)
        self.assertIsNone(alice.ethnicity_free_text)
        self.assertIsNone(alice.country_of_residence)
        self.assertIsNone(alice.nationality)
        self.assertEqual(alice.dont_ask_demographics, True)

    def test_post_update_after_dont_ask_again(self):
        alice = factories.create_user_with_dont_ask_demographics_set(year_of_birth='1985')
        self.client.force_login(alice)

        data = {
            'name': 'Alice',
            'email_addr': 'alice@example.com',
            'year_of_birth': '1986',
            'gender': 'agender',
            'ethnicity': 'Any other ethnic group, please describe',
            'ethnicity_free_text': 'Abkhazian',
            'country_of_residence': 'Abkhazia',
            'nationality': 'Abkhazian',
        }
        self.client.post('/profile/edit/', data, follow=True)
        alice.refresh_from_db()

        self.assertEqual(alice.year_of_birth, '1986')
        self.assertEqual(alice.gender, 'agender')
        self.assertEqual(alice.ethnicity, 'Any other ethnic group, please describe')
        self.assertEqual(alice.ethnicity_free_text, 'Abkhazian')
        self.assertEqual(alice.country_of_residence, 'Abkhazia')
        self.assertEqual(alice.nationality, 'Abkhazian')
        self.assertEqual(alice.dont_ask_demographics, False)

    def test_post_update_to_snake(self):
        alice = factories.create_user()
        self.client.force_login(alice)

        data = {
            'name': 'Alice',
            'email_addr': 'alice@example.com',
            'badge_company': 'BigCorp',
            'badge_snake_colour': 'red',
            'badge_snake_extras': 'deerstalker',
            'badge_twitter': '@notalice',
            'badge_pronoun': 'they/them',
        }
        self.client.post('/profile/edit/', data, follow=True)
        alice.refresh_from_db()

        self.assertEqual(alice.badge_company, 'BigCorp')
        self.assertEqual(alice.badge_snake_colour, 'red')
        self.assertEqual(alice.badge_snake_extras, 'deerstalker')
        self.assertEqual(alice.badge_twitter, '@notalice')
        self.assertEqual(alice.badge_pronoun, 'they/them')

    def test_get_snake_allocated(self):
        alice = factories.create_user()
        self.client.force_login(alice)

        data = {
            'name': 'Alice Wonderland',
            'email_addr': 'alice@example.com',
        }
        self.client.post('/profile/edit/', data, follow=True)
        alice.refresh_from_db()

        self.assertEqual(alice.name, 'Alice Wonderland')
        self.assertTrue(alice.badge_snake_colour in ['red', 'blue', 'orange', 'yellow', 'green', 'purple'])
        self.assertTrue(alice.badge_snake_extras in ['deerstalker', 'glasses', 'mortar', 'astronaut', 'crown', 'dragon'])

    def test_get_company_is_billing_name(self):
        alice = factories.create_user()
        create_confirmed_order_for_self(user=alice, rate='corporate')
        self.client.force_login(alice)

        data = {
            'name': 'Alice',
            'email_addr': 'alice@example.com',
        }
        self.client.post('/profile/edit/', data, follow=True)
        alice.refresh_from_db()

        self.assertEqual(alice.badge_company, 'Sirius Cybernetics Corp.')

    def test_corp_cant_change_company_name(self):
        alice = factories.create_user()
        create_confirmed_order_for_self(user=alice, rate='corporate')
        self.client.force_login(alice)

        data = {
            'name': 'Alice',
            'email_addr': 'alice@example.com',
            'badge_company': 'Alice Personal Development Co.'
        }
        self.client.post('/profile/edit/', data, follow=True)
        alice.refresh_from_db()

        self.assertEqual(alice.badge_company, 'Sirius Cybernetics Corp.')


class LoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = factories.create_user(email_addr='alice@example.com', password='Pa55w0rd')

    def test_get(self):
        rsp = self.client.get('/accounts/login/?next=/tickets/orders/new/')
        self.assertContains(rsp, '<input type="hidden" name="next" value="/tickets/orders/new/" />', html=True)

    def test_post_success(self):
        data = {
            'username': 'alice@example.com',
            'password': 'Pa55w0rd',
        }
        rsp = self.client.post('/accounts/login/', data, follow=True)
        self.assertContains(rsp, 'Hello, Alice')

    def test_post_failure_wrong_password(self):
        data = {
            'username': 'alice@example.com',
            'password': 'password',
        }
        rsp = self.client.post('/accounts/login/', data, follow=True)
        self.assertContains(rsp, "Your email address and password didn't match")

    def test_post_redirect(self):
        data = {
            'username': 'alice@example.com',
            'password': 'Pa55w0rd',
            'next': '/tickets/orders/new/'
        }
        rsp = self.client.post('/accounts/login/', data, follow=True)
        self.assertRedirects(rsp, '/tickets/orders/new/')


class RegisterTests(TestCase):
    def test_get(self):
        rsp = self.client.get('/accounts/register/?next=/tickets/orders/new/')
        self.assertContains(rsp, '<input type="hidden" name="next" value="/tickets/orders/new/" />', html=True)

    def test_post_fails_if_terms_not_accepted(self):
        data = {
            'name': 'Alice',
            'email_addr': 'alice@example.com',
            'password1': 'Pa55w0rd',
            'password2': 'Pa55w0rd',
        }
        rsp = self.client.post('/accounts/register/', data, follow=True)
        self.assertContains(rsp, 'This field is required.')

    def test_post_success(self):
        data = {
            'name': 'Alice',
            'email_addr': 'alice@example.com',
            'password1': 'Pa55w0rd',
            'password2': 'Pa55w0rd',
            'agree_terms': True,
        }
        rsp = self.client.post('/accounts/register/', data, follow=True)
        self.assertContains(rsp, 'Hello, Alice')

    def test_post_failure_password_mismatch(self):
        data = {
            'name': 'Alice',
            'email_addr': 'alice@example.com',
            'password1': 'Pa55w0rd',
            'password2': 'Pa55wOrd',
            'agree_terms': True,
        }
        rsp = self.client.post('/accounts/register/', data, follow=True)
        self.assertContains(rsp, "The two password fields didn&#39;t match")

    def test_post_failure_password_too_short(self):
        data = {
            'name': 'Alice',
            'email_addr': 'alice@example.com',
            'password1': 'pw',
            'password2': 'pw',
            'agree_terms': True,
        }
        rsp = self.client.post('/accounts/register/', data, follow=True)
        self.assertContains(rsp, 'This password is too short')

    def test_post_failure_email_taken(self):
        factories.create_user(email_addr='alice@example.com')
        data = {
            'name': 'Alice',
            'email_addr': 'alice@example.com',
            'password1': 'Pa55w0rd',
            'password2': 'Pa55w0rd',
            'agree_terms': True,
        }
        rsp = self.client.post('/accounts/register/', data, follow=True)
        self.assertContains(rsp, 'That email address has already been registered')

    def test_post_redirect(self):
        data = {
            'name': 'Alice',
            'email_addr': 'alice@example.com',
            'password1': 'Pa55w0rd',
            'password2': 'Pa55w0rd',
            'agree_terms': True,
            'next': '/tickets/orders/new/'
        }
        rsp = self.client.post('/accounts/register/', data, follow=True)
        self.assertRedirects(rsp, '/tickets/orders/new/')
