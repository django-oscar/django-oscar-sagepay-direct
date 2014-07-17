import httplib

import requests
from django.conf import settings

from . import models, exceptions

TEST_URL = 'https://test.sagepay.com/gateway/service/vspdirect-register.vsp'

# TxType
TXTYPE_PAYMENT = 'PAYMENT'
TXTYPE_DEFERRED = 'DEFERRED'
TXTYPE_AUTHENTICATE = 'AUTHENTICATE'

# Card types
CARDTYPE_VISA = 'VISA'
CARDTYPE_MASTERCARD = 'MC'
CARDTYPE_MASTERCARD_DEBIT = 'MCDEBIT'
CARDTYPE_DELTA = 'DELTA'
CARDTYPE_MAESTRO = 'MAESTRO'
CARDTYPE_UKE = 'UKE'
CARDTYPE_DC = 'DC'
CARDTYPE_JCB = 'JCB'
CARDTYPE_LASER = 'LASER'
CARDTYPE_PAYPAL = 'PAYPAL'

VENDOR = 'tangentsnowball'


__all__ = ['register_payment', 'authenticate', 'authorize', 'cancel', 'refund']


class Response(object):
    # Statuses
    OK = 'OK'
    OK_REPEATED = 'OK REPEATED'
    MALFORMED = 'MALFORMED'
    INVALID = 'INVALID'
    ERROR = 'ERROR'

    def __init__(self, response_content):
        self._params = dict(
            line.split('=', 1) for line in
            response_content.strip().split("\r\n"))

    def __str__(self):
        return '<Response status="%s" msg="%s">' % (
            self.status, self.status_detail)

    def param(self, key, default=None):
        """
        Extract a parameter from the response
        """
        return self._params.get(key, default)

    @property
    def status(self):
        return self.param('Status')

    @property
    def status_detail(self):
        return self.param('StatusDetail')

    @property
    def is_successful(self):
        return self.status in (self.OK, self.OK_REPEATED)


def register_payment(amount, currency):
    # Create model first to get unique ID for VendorExCode
    rr = models.RequestResponse.objects.create()

    params = {
        'VPSProtocol': '3.0',
        'TxType': TXTYPE_PAYMENT,
        'Vendor': settings.OSCAR_SAGEPAY_VENDOR,
        # This should be unique per txn
        'VendorTxCode': '1',
        'Amount': str(amount),
        'Currency': currency,
        'Description': 'This is a test',
        'CardType': CARDTYPE_VISA,
        'CardNumber': '4929000000006',
        'CardHolder': 'Barry',
        # Format MMYY
        'ExpiryDate': '0114',
    }

    # Update audit model with request info
    rr.record_request(params)
    rr.save()

    # Sagepay seem to return a status 200 even for errors
    try:
        http_response = requests.post(TEST_URL, params)
    except requests.exceptions.RequestException as e:
        raise exceptions.GatewayError(
            "HTTP error: %s" % e.message)
    if http_response.status_code != httplib.OK:
        raise exceptions.GatewayError(
            "Sagepay server returned a %s response with content %s" % (
                http_response.status_code, http_response.content))
    sp_response = Response(http_response.content)

    # Update audit model with response info
    rr.record_response(sp_response)
    rr.save()

    return sp_response


def authenticate(amount, currency):
    """
    First part of 2-stage payment processing.

    Successful requests will get a status of REGISTERED
    """


def authorize():
    """
    Second step of 2-stage payment processing

    Notes:
        - You can AUTHORIZE up to 115% of the original AUTHENTICATE request
        amount.
        - You have to AUTHORIZE within 90 days
    """


def cancel():
    """
    Cancel an existing card authentication

    This happens automatically after 90 days.
    """


def refund():
    """
    Refund a txn

    Notes:
        - You can send multiple refunds as long as the totals don't exceed the
        original amount.
    """
