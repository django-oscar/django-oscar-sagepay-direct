import datetime
from decimal import Decimal as D

from oscar.apps.payment import (
    models as payment_models, exceptions as payment_exceptions)
from oscar.core import prices
import mock
import pytest

from oscar_sagepay import facade, exceptions, models
from tests import factories


BANKCARD = payment_models.Bankcard(
    name='Barry Chuckle', number='4111111111111111',
    expiry_date=datetime.date.today(), ccv='123')
AMT = prices.Price('GBP', D('10.00'), D('10.00'))
SHIPPING_ADDRESS = factories.ShippingAddress()
BILLING_ADDRESS = factories.BillingAddress()


@mock.patch('oscar_sagepay.gateway.authenticate')
class TestAuthenticate:

    def test_extracts_bankcard_info(self, gateway_authenticate):
        facade.authenticate(AMT, BANKCARD, SHIPPING_ADDRESS, BILLING_ADDRESS)
        __, kwargs = gateway_authenticate.call_args
        for key in ('amount', 'currency', 'bankcard_number', 'bankcard_cv2',
                    'bankcard_name', 'bankcard_expiry'):
            assert key in kwargs

    def test_extracts_shipping_address_info(self, gateway_authenticate):
        facade.authenticate(AMT, BANKCARD, SHIPPING_ADDRESS, BILLING_ADDRESS)
        __, kwargs = gateway_authenticate.call_args
        for key in ('delivery_surname', 'delivery_first_names',
                    'delivery_address1', 'delivery_address2', 'delivery_city',
                    'delivery_postcode', 'delivery_country', 'delivery_state',
                    'delivery_phone'):
            assert key in kwargs

    def test_extracts_billing_address_info(self, gateway_authenticate):
        facade.authenticate(AMT, BANKCARD, SHIPPING_ADDRESS, BILLING_ADDRESS)
        __, kwargs = gateway_authenticate.call_args
        for key in ('billing_surname', 'billing_first_names',
                    'billing_address1', 'billing_address2', 'billing_city',
                    'billing_postcode', 'billing_country', 'billing_state',):
            assert key in kwargs

    def test_raises_payment_error_if_gateway_problem(self, gateway_authenticate):
        gateway_authenticate.side_effect = exceptions.GatewayError
        with pytest.raises(payment_exceptions.PaymentError):
            facade.authenticate(
                AMT, BANKCARD, SHIPPING_ADDRESS, BILLING_ADDRESS)

    def test_raises_payment_error_if_response_not_ok(self, gateway_authenticate):
        gateway_authenticate.return_value = mock.Mock(is_registered=False)
        with pytest.raises(payment_exceptions.PaymentError):
            facade.authenticate(
                AMT, BANKCARD, SHIPPING_ADDRESS, BILLING_ADDRESS)

    def test_returns_tx_id_if_successful(self, gateway_authenticate):
        gateway_authenticate.return_value = mock.Mock(tx_id='123xxx')
        tx_id = facade.authenticate(
            AMT, BANKCARD, SHIPPING_ADDRESS, BILLING_ADDRESS)
        assert tx_id == '123xxx'


@mock.patch('oscar_sagepay.models.RequestResponse.objects.get')
class TestAuthorise:

    def test_raises_payment_error_if_no_matching_audit_model(self, get):
        get.side_effect = models.RequestResponse.DoesNotExist
        with pytest.raises(payment_exceptions.PaymentError):
            facade.authorise(tx_id='123')

    def test_calls_gateway_with_correct_data(self, get):
        get.return_value = mock.MagicMock(
            vendor_tx_code='v1', tx_id='123', tx_auth_num='', security_key='xx')
        with mock.patch('oscar_sagepay.gateway.authorise') as authorise:
            facade.authorise(tx_id='123', amount=D('10.00'))
            kwargs = authorise.call_args[1]
        assert kwargs['previous_txn'].vendor_tx_code == 'v1'
        assert kwargs['previous_txn'].tx_id == '123'
        assert kwargs['previous_txn'].tx_auth_num == ''
        assert kwargs['previous_txn'].security_key == 'xx'
        assert kwargs['amount'] == D('10.00')
        assert 'description' in kwargs

    def test_defaults_to_previous_amount(self, get):
        get.return_value = mock.MagicMock(amount=D('1.99'))
        with mock.patch('oscar_sagepay.gateway.authorise') as authorise:
            facade.authorise(tx_id='123')
            kwargs = authorise.call_args[1]
        assert kwargs['amount'] == D('1.99')

    def test_gateway_error_raises_payment_error(self, get):
        get.return_value = mock.MagicMock()
        with mock.patch('oscar_sagepay.gateway.authorise') as authorise:
            authorise.side_effect = exceptions.GatewayError
            with pytest.raises(payment_exceptions.PaymentError):
                facade.authorise(tx_id='123')

    def test_not_ok_response_raises_payment_error(self, get):
        get.return_value = mock.MagicMock()
        with mock.patch('oscar_sagepay.gateway.authorise') as authorise:
            authorise.return_value = mock.MagicMock(is_ok=False)
            with pytest.raises(payment_exceptions.PaymentError):
                facade.authorise(tx_id='123')


@mock.patch('oscar_sagepay.models.RequestResponse.objects.get')
class TestRefund:

    def test_raises_payment_error_for_unknown_tx_id(self, get):
        get.side_effect = models.RequestResponse.DoesNotExist
        with pytest.raises(payment_exceptions.PaymentError):
            facade.refund(tx_id='123')

    def test_raises_payment_error_for_missing_related_txn(self, get):
        # Second call will raise exception
        get.side_effect = [
            mock.MagicMock(), models.RequestResponse.DoesNotExist]
        with pytest.raises(payment_exceptions.PaymentError):
            facade.refund(tx_id='123')

    def test_calls_gateway_with_correct_data(self, get):
        get.side_effect = [
            mock.MagicMock(vendor_tx_code='v1', tx_id='123',
                           tx_auth_num='', security_key='xx',
                           currency='GBP'),
            mock.MagicMock(vendor_tx_code='v2', tx_id='124',
                           tx_auth_num='999', security_key='xy')]
        with mock.patch('oscar_sagepay.gateway.refund') as refund:
            facade.refund(tx_id='123')
            kwargs = refund.call_args[1]
            assert kwargs['previous_txn'].vendor_tx_code == 'v2'
            assert kwargs['previous_txn'].tx_id == '124'
            assert kwargs['previous_txn'].tx_auth_num == '999'
            assert kwargs['previous_txn'].security_key == 'xy'
            assert kwargs['currency'] == 'GBP'

    def test_gateway_error_raises_payment_error(self, get):
        get.side_effect = [
            mock.MagicMock(vendor_tx_code='v1', tx_id='123',
                           tx_auth_num='', security_key='xx',
                           currency='GBP'),
            mock.MagicMock(vendor_tx_code='v2', tx_id='124',
                           tx_auth_num='999', security_key='xy')]
        with mock.patch('oscar_sagepay.gateway.refund') as refund:
            refund.side_effect = exceptions.GatewayError
            with pytest.raises(payment_exceptions.PaymentError):
                facade.refund(tx_id='123')

    def test_not_ok_response_raises_payment_error(self, get):
        get.side_effect = [
            mock.MagicMock(vendor_tx_code='v1', tx_id='123',
                           tx_auth_num='', security_key='xx',
                           currency='GBP'),
            mock.MagicMock(vendor_tx_code='v2', tx_id='124',
                           tx_auth_num='999', security_key='xy')]
        with mock.patch('oscar_sagepay.gateway.refund') as refund:
            refund.return_value = mock.MagicMock(is_ok=False)
            with pytest.raises(payment_exceptions.PaymentError):
                facade.refund(tx_id='123')
