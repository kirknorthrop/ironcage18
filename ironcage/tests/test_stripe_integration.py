import stripe

from django.test import TestCase

from tickets.tests import factories
from . import utils

from ironcage import stripe_integration


class StripeIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.order = factories.create_pending_order_for_self()

    def setUp(self):
        self.order.refresh_from_db()

    def test_create_charge_for_order_with_successful_charge(self):
        token = 'tok_abcdefghijklmnopqurstuvwx'
        with utils.patched_charge_creation_success():
            charge = stripe_integration.create_charge_for_order(self.order, token)
        self.assertEqual(charge.id, 'ch_abcdefghijklmnopqurstuvw')

    def test_create_charge_for_order_with_unsuccessful_charge(self):
        token = 'tok_abcdefghijklmnopqurstuvwx'
        with self.assertRaises(stripe.error.CardError):
            with utils.patched_charge_creation_failure():
                stripe_integration.create_charge_for_order(self.order, token)

    def test_refund_charge(self):
        with utils.patched_refund_creation() as mock:
            stripe_integration.refund_charge('ch_abcdefghijklmnopqurstuvw')
        mock.assert_called_with(charge='ch_abcdefghijklmnopqurstuvw')

    def test_refund_item(self):
        factories.confirm_order(self.order)
        with utils.patched_refund_creation() as mock:
            stripe_integration.refund_item(self.order.all_tickets()[0])
        mock.assert_called_with(charge='ch_abcdefghijklmnopqurstuvw', amount=15000)
