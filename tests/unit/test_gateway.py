from decimal import Decimal as D
import datetime

import pytest
import mock
from oscar.apps.payment import models as payment_models

from oscar_sagepay import gateway, models, wrappers
from tests import responses

# Fixtures
BANKCARD = payment_models.Bankcard(
    name='Barry Chuckle', number='4111111111111111',
    expiry_date=datetime.date.today(), ccv='123')
AMT, CURRENCY = D('10.00'), 'GBP'


def stub_sagepay_response(content=responses.MALFORMED, status_code=200):
    return mock.patch(
        'requests.post', new=mock.MagicMock(
            **{
                'return_value.content': content,
                'return_value.status_code': status_code
            }))


def stub_orm_create():
    return mock.patch(
        'oscar_sagepay.models.RequestResponse',
        new=mock.MagicMock())


@stub_orm_create()
@stub_sagepay_response()
def test_authenticate_returns_response_obj():
    response = gateway.authenticate(AMT, CURRENCY)
    assert isinstance(response, wrappers.Response)


@stub_orm_create()
@stub_sagepay_response(status_code=500)
def test_exception_raised_for_non_200_response():
    with pytest.raises(Exception) as e:
        gateway.authenticate(AMT, CURRENCY)
    assert '500' in e.exconly()


@stub_orm_create()
def test_fields_are_truncated_to_fit_sagepay():
    with mock.patch('requests.post') as post:
        post.return_value = mock.MagicMock(
            content=responses.MALFORMED,
            status_code=200)
        gateway.authenticate(
            AMT, CURRENCY,
            delivery_city="This is too long for Sagepay as they only allow 40"
        )
        args, __ = post.call_args
        assert len(args[1]['DeliveryCity']) == 40


@stub_sagepay_response()
def test_audit_model_is_called_with_request_params():
    patch_kwargs = {
        'target': 'oscar_sagepay.models.RequestResponse',
    }
    with mock.patch(**patch_kwargs) as rr:
        gateway.authenticate(AMT, CURRENCY)
        call_params = rr.new.call_args[0][0]

    for key in ('VPSProtocol', 'Vendor', 'TxType'):
        assert key in call_params
