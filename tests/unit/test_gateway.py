from decimal import Decimal as D

import pytest
import mock

from oscar_sagepay import gateway, models
from tests import responses

AMT, CURRENCY = D('10.00'), 'GBP'

pytestmark = pytest.mark.django_db


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
def test_register_payment_returns_response_obj():
    return
    response = gateway.register_payment(AMT, CURRENCY)
    assert isinstance(response, gateway.Response)


@mock_orm()
@stub_response(status_code=500)
def test_exception_raised_for_non_200_response():
    with pytest.raises(Exception) as e:
        gateway.register_payment(AMT, CURRENCY)
    assert '500' in e.exconly()
