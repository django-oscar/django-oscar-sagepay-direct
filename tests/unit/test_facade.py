import datetime
from decimal import Decimal as D

from oscar.apps.payment import (
    models as payment_models, exceptions as payment_exceptions)
from oscar.core import prices
import mock
import pytest

from oscar_sagepay import facade, exceptions
from tests import factories


BANKCARD = payment_models.Bankcard(
    name='Barry Chuckle', number='4111111111111111',
    expiry_date=datetime.date.today(), ccv='123')
AMT = prices.Price('GBP', D('10.00'), D('10.00'))


@mock.patch('oscar_sagepay.gateway.authenticate')
class TestAuthenticate:

    def test_extracts_bankcard_info(self, gateway_authenticate):
        facade.authenticate(AMT, BANKCARD)
        __, kwargs = gateway_authenticate.call_args
        for key in ('amount', 'currency', 'bankcard_number', 'bankcard_cv2',
                    'bankcard_name', 'bankcard_expiry'):
            assert key in kwargs

    def test_extracts_shipping_address_info(self, gateway_authenticate):
        addr = factories.ShippingAddress.build()

        facade.authenticate(AMT, BANKCARD, shipping_address=addr)
        __, kwargs = gateway_authenticate.call_args
        for key in ('delivery_surname', 'delivery_first_names',
                    'delivery_address1', 'delivery_address2', 'delivery_city',
                    'delivery_postcode', 'delivery_country', 'delivery_state',
                    'delivery_phone'):
            assert key in kwargs

    def test_extracts_billing_address_info(self, gateway_authenticate):
        shipping_addr = factories.ShippingAddress()
        billing_addr = factories.BillingAddress()

        facade.authenticate(AMT, BANKCARD, shipping_address=shipping_addr,
                            billing_address=billing_addr)
        __, kwargs = gateway_authenticate.call_args
        for key in ('billing_surname', 'billing_first_names',
                    'billing_address1', 'billing_address2', 'billing_city',
                    'billing_postcode', 'billing_country', 'billing_state',):
            assert key in kwargs

    def test_raises_payment_error_if_gateway_problem(self, gateway_authenticate):
        gateway_authenticate.side_effect = exceptions.GatewayError
        with pytest.raises(payment_exceptions.PaymentError):
            facade.authenticate(AMT, BANKCARD)

    def test_raises_unable_to_pay_if_response_not_ok(self, gateway_authenticate):
        gateway_authenticate.return_value = mock.Mock(is_successful=False)
        with pytest.raises(payment_exceptions.UnableToTakePayment):
            facade.authenticate(AMT, BANKCARD)

    def test_returns_tx_id_if_successful(self, gateway_authenticate):
        gateway_authenticate.return_value = mock.Mock(tx_id='123xxx')
        tx_id = facade.authenticate(AMT, BANKCARD)
        assert tx_id == '123xxx'
