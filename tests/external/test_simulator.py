from decimal import Decimal as D
import datetime
import random

import pytest
from oscar.apps.payment import models as payment_models

from oscar_sagepay import gateway

BANKCARD = payment_models.Bankcard(
    name='Barry Chuckle', number='4111111111111111',
    expiry_date=datetime.date.today(), ccv='123')
AMT, CURRENCY = D('10.00'), 'GBP'


@pytest.mark.django_db
def test_multiple_transactions():
    # Authenticate transaction
    response = gateway.authenticate(
        BANKCARD, AMT, CURRENCY)
    assert response.is_registered

    # Authorise (part 1)
    txn = gateway.PreviousTxn(
        response.vendor_tx_code,
        response.tx_id,
        response.tx_auth_num,
        response.security_key)
    auth_response_1 = gateway.authorise(
        txn, amount=D('8.00'), description="Test first auth")
    assert auth_response_1.is_successful, auth_response_1.status_detail

    # Authorise (part 2)
    auth_response_2 = gateway.authorise(
        txn, amount=D('2.00'), description="Test second auth")
    assert auth_response_2.is_successful, auth_response_2.status_detail

    # Refund last authorise
    txn = gateway.PreviousTxn(
        auth_response_2.vendor_tx_code,
        auth_response_2.tx_id,
        auth_response_2.tx_auth_num,
        auth_response_2.security_key)
    refund_response = gateway.refund(
        txn, amount=D('2.00'), currency='GBP', description="Test refund")
    assert refund_response.is_successful, refund_response.status_detail
