from decimal import Decimal as D
import datetime

import pytest
import mock
from oscar.apps.payment import models as payment_models

from oscar_sagepay import gateway, models
from tests import responses

# Fixtures
BANKCARD = payment_models.Bankcard(
    name='Barry Chuckle', number='4111111111111111',
    expiry_date=datetime.date.today(), ccv='123')
AMT, CURRENCY = D('10.00'), 'GBP'


def stub_response(content=responses.MALFORMED, status_code=200):
    return mock.patch(
        'requests.post', new=mock.MagicMock(
            **{
                'return_value.content': content,
                'return_value.status_code': status_code
            }))


def mock_orm():
    response = models.RequestResponse(id=1)
    response.save = mock.Mock()
    return mock.patch(
        'oscar_sagepay.models.RequestResponse.objects',
        new=mock.MagicMock(
            **{'create.return_value': response}))


@mock_orm()
@stub_response()
def test_payment_returns_response_obj():
    response = gateway.payment(BANKCARD, AMT, CURRENCY)
    assert isinstance(response, gateway.Response)


@mock_orm()
@stub_response(status_code=500)
def test_exception_raised_for_non_200_response():
    with pytest.raises(Exception) as e:
        gateway.payment(BANKCARD, AMT, CURRENCY)
    assert '500' in e.exconly()


@mock_orm()
@mock.patch('requests.post', **{'return_value.content': responses.MALFORMED,
                                'return_value.status_code': 200})
def test_params_are_passed_correctly(mocked_post):
    gateway.payment(BANKCARD, AMT, CURRENCY)
    passed_params = mocked_post.call_args[0][1]
    assert passed_params['ExpiryDate'] == BANKCARD.expiry_date.strftime('%m%y')
    assert passed_params['Amount'] == '10.00'
    assert passed_params['Currency'] == 'GBP'
    assert passed_params['CardHolder'] == BANKCARD.name
    assert passed_params['CV2'] == BANKCARD.ccv
    assert passed_params['CardType'] == 'VISA'  # Magic number looks like a VISA
