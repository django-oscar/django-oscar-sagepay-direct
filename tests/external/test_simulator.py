from decimal import Decimal as D
import datetime

import pytest
import oscar
from oscar.apps.payment import models as payment_models

from oscar_sagepay import facade
from tests import factories

bankcard_kwargs = {
    'name': 'Barry Chuckle',
    'number': '4111111111111111',
    'expiry_date': datetime.date.today(),
}
if oscar.VERSION[1] >= 6:
    bankcard_kwargs['ccv'] = '123'

BANKCARD = payment_models.Bankcard(**bankcard_kwargs)
AMT = D('10.00')
CURRENCY = 'GBP'
SHIPPING_ADDRESS = factories.ShippingAddress()
BILLING_ADDRESS = factories.BillingAddress()


@pytest.mark.django_db
def test_multiple_transactions():
    # Authenticate transaction
    authenticate_tx_id = facade.authenticate(
        AMT, CURRENCY, BANKCARD, SHIPPING_ADDRESS, BILLING_ADDRESS)

    # Authorise (in two parts)
    facade.authorise(
        tx_id=authenticate_tx_id, amount=D('8.00'))
    auth_tx_id = facade.authorise(
        tx_id=authenticate_tx_id, amount=D('2.00'))

    # Refund last authorise
    facade.refund(auth_tx_id)
