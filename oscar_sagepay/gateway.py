import httplib

import requests
from oscar.apps.payment import bankcards

from . import models, exceptions, config

# TxType
TXTYPE_PAYMENT = 'PAYMENT'
TXTYPE_DEFERRED = 'DEFERRED'
TXTYPE_AUTHENTICATE = 'AUTHENTICATE'


__all__ = ['payment', 'authenticate', 'authorize', 'cancel', 'refund']


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
        return self.param('Status', '')

    @property
    def status_detail(self):
        return self.param('StatusDetail', '')

    @property
    def tx_id(self):
        return self.param('VPSTxId', '')

    @property
    def security_key(self):
        return self.param('SecurityKey', '')

    @property
    def is_successful(self):
        return self.status in (self.OK, self.OK_REPEATED)


def _card_type(bankcard):
    """
    Convert card-number into appropriate card type that Sagepay will
    recognise.
    """
    # Oscar provides a function to do the card-type recognition but we need to
    # map into the values that Sagepay accepts.
    oscar_type = bankcards.bankcard_type(bankcard.number)
    mapping = {
        bankcards.VISA: 'VISA',
        bankcards.VISA_ELECTRON: 'UKE',
        bankcards.MASTERCARD: 'MC',
        bankcards.MAESTRO: 'MAESTRO',
        bankcards.AMEX: 'AMEX',
        bankcards.DINERS_CLUB: 'DC',
        bankcards.LASER: 'LASER',
        bankcards.JCB: 'JCB',
    }
    return mapping.get(oscar_type, '')


def _register_payment(tx_type, bankcard, amount, currency, description='',
                      **kwargs):
    # Create model first to get unique ID for VendorExCode
    rr = models.RequestResponse.objects.create()

    params = {
        # VENDOR DETAILS
        'VPSProtocol': config.VPS_PROTOCOL,
        'Vendor': config.VENDOR,
        'TxType': tx_type,
        # This should be unique per txn
        'VendorTxCode': rr.vendor_tx_code,
        # TXN DETAILS
        'Amount': str(amount),
        'Currency': currency,
        'Description': description,
        # BANKCARD DETAILS
        'CardType': _card_type(bankcard),
        'CardNumber': bankcard.number,
        'CV2': bankcard.ccv,
        'CardHolder': bankcard.name,
        'ExpiryDate': bankcard.expiry_month('%m%y'),
        # BILLING DETAILS
        'BillingSurname': kwargs.get('billing_surname', ''),
        'BillingFirstnames': kwargs.get('billing_first_names', ''),
        'BillingAddress1': kwargs.get('billing_address1', ''),
        'BillingAddress2': kwargs.get('billing_address2', ''),
        'BillingCity': kwargs.get('billing_city', ''),
        'BillingPostCode': kwargs.get('billing_postcode', ''),
        'BillingCountry': kwargs.get('billing_country', ''),
        'BillingState': kwargs.get('billing_state', ''),
        'BillingPhone': kwargs.get('billing_phone', ''),
        # DELIVERY DETAILS
        'DeliverySurname': kwargs.get('delivery_surname', ''),
        'DeliveryFirstnames': kwargs.get('delivery_first_names', ''),
        'DeliveryAddress1': kwargs.get('delivery_address1', ''),
        'DeliveryAddress2': kwargs.get('delivery_address2', ''),
        'DeliveryCity': kwargs.get('delivery_city', ''),
        'DeliveryPostCode': kwargs.get('delivery_postcode', ''),
        'DeliveryCountry': kwargs.get('delivery_country', ''),
        'DeliveryState': kwargs.get('delivery_state', ''),
        'DeliveryPhone': kwargs.get('delivery_phone', ''),
    }

    # Update audit model with request info
    rr.record_request(params)
    rr.save()

    try:
        http_response = requests.post(config.VPS_URL, params)
    except requests.exceptions.RequestException as e:
        raise exceptions.GatewayError(
            "HTTP error: %s" % e.message)
    if http_response.status_code != httplib.OK:
        # Sagepay seem to return a status 200 even for bad requests
        raise exceptions.GatewayError(
            "Sagepay server returned a %s response with content %s" % (
                http_response.status_code, http_response.content))
    sp_response = Response(http_response.content)

    # Update audit model with response info
    rr.record_response(sp_response)
    rr.save()

    return sp_response


def payment(*args, **kwargs):
    """
    Authorize a transaction (1 stage payment processing)
    """
    return _register_payment(TXTYPE_PAYMENT, *args, **kwargs)


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
