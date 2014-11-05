# -*- coding: utf-8 -*-
from decimal import Decimal as D
import datetime

import pytest
import mock
import oscar
from oscar.apps.payment import models as payment_models

from oscar_sagepay import gateway, models, wrappers
from tests import responses

# Fixtures
bankcard_kwargs = {
    'name': 'Barry Chuckle',
    'number': '4111111111111111',
    'expiry_date': datetime.date.today(),
}
if oscar.VERSION[1] >= 6:
    bankcard_kwargs['ccv'] = '123'

BANKCARD = payment_models.Bankcard(**bankcard_kwargs)
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


@stub_orm_create()
def test_fields_are_cleaned_to_match_sagepay_formats():
    with mock.patch('requests.post') as post:
        post.return_value = mock.MagicMock(status_code=200)
        gateway.authenticate(
            AMT, CURRENCY, delivery_surname="Name?"
        )
        args, __ = post.call_args
        assert args[1]['DeliverySurname'] == "Name"


@stub_orm_create()
def test_state_is_not_submitted_for_non_us_country():
    with mock.patch('requests.post') as post:
        post.return_value = mock.MagicMock(status_code=200)
        gateway.authenticate(
            AMT, CURRENCY, delivery_state="Somerset", delivery_country='GB'
        )
        args, __ = post.call_args
        assert args[1]['DeliveryState'] == ""


@stub_sagepay_response()
def test_audit_model_is_called_with_request_params():
    patch_kwargs = {
        'target': 'oscar_sagepay.models.RequestResponse',
    }
    with mock.patch(**patch_kwargs) as rr:
        gateway.authenticate(AMT, CURRENCY, reference='x')
        ref, call_params = rr.new.call_args[0]

    assert ref == 'x'
    for key in ('VPSProtocol', 'Vendor', 'TxType'):
        assert key in call_params


@pytest.mark.parametrize("raw, clean", [
    (u"Name?", u"Name"),
    (u"Name!", u"Name"),
    (u"&-.,1", u"&-.,1"),
    (u"dèjá vu", u"dèjá vu"),
])
def test_clean_name_strips_invalid_chars(raw, clean):
    assert gateway.clean_name(raw) == clean


@pytest.mark.parametrize("raw, clean", [
    (u"&-.,1+()", u"&-.,1+()"),
    (u"dèjá vu", u"dèjá vu"),
])
def test_clean_address_strips_invalid_chars(raw, clean):
    assert gateway.clean_address(raw) == clean


@pytest.mark.parametrize("raw, clean", [
    (u"N12 9ET", u"N12 9ET"),
    (u"N12.9ET", u"N129ET"),
])
def test_clean_postcode_strips_invalid_chars(raw, clean):
    assert gateway.clean_postcode(raw) == clean
