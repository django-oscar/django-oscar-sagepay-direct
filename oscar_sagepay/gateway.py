import httplib
import collections

import requests
from oscar.apps.payment import bankcards

from . import models, exceptions, config

# TxType
TXTYPE_PAYMENT = 'PAYMENT'
TXTYPE_DEFERRED = 'DEFERRED'
TXTYPE_AUTHENTICATE = 'AUTHENTICATE'
TXTYPE_AUTHORISE = 'AUTHORISE'
TXTYPE_REFUND = 'REFUND'


__all__ = ['PreviousTxn', 'payment', 'authenticate',
           'authorise', 'cancel', 'refund']


class Response(object):
    """
    Response object wrapping providing easy access to the returned parameters
    """
    # Statuses
    OK = 'OK'
    OK_REPEATED = 'OK REPEATED'
    MALFORMED = 'MALFORMED'
    INVALID = 'INVALID'
    ERROR = 'ERROR'
    REGISTERED = 'REGISTERED'

    def __init__(self, vendor_tx_code, response_content):
        # We pass in the vendor tx code as it's required in several places as a
        # parameter to subsequent payment calls but is missing from the
        # response params.
        self.vendor_tx_code = vendor_tx_code
        self.raw = response_content
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

    # Syntactic sugar

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
    def tx_auth_num(self):
        return self.param('TxAuthNo', '')

    @property
    def security_key(self):
        return self.param('SecurityKey', '')

    # Predicates

    @property
    def is_successful(self):
        return self.status in (self.OK, self.OK_REPEATED)

    @property
    def is_registered(self):
        return self.status == self.REGISTERED


# Datastructure for wrapping up details of a previous transaction
PreviousTxn = collections.namedtuple(
    'PreviousTxn', ('vendor_tx_code', 'tx_id', 'tx_auth_num', 'security_key'))


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


def _request(url, tx_type, params):
    # Create audit model
    rr = models.RequestResponse.objects.create()

    vendor_tx_code = rr.vendor_tx_code
    request_params = {
        'VPSProtocol': config.VPS_PROTOCOL,
        'Vendor': config.VENDOR,
        'TxType': tx_type,
        'VendorTxCode': vendor_tx_code,
    }
    request_params.update(params)

    # Update audit model with request info
    rr.record_request(request_params)
    rr.save()

    try:
        http_response = requests.post(url, request_params)
    except requests.exceptions.RequestException as e:
        raise exceptions.GatewayError(
            "HTTP error: %s" % e.message)
    if http_response.status_code != httplib.OK:
        # Sagepay seem to return a status 200 even for bad requests
        raise exceptions.GatewayError(
            "Sagepay server returned a %s response with content %s" % (
                http_response.status_code, http_response.content))
    sp_response = Response(vendor_tx_code, http_response.content)

    # Update audit model with response info
    rr.record_response(sp_response)
    rr.save()

    return sp_response


def payment(*args, **kwargs):
    """
    Authorise a transaction (1 stage payment processing)
    """
    params = {}
    return _request(config.VPS_REGISTER_URL, TXTYPE_AUTHENTICATE, params)


def authenticate(bankcard, amount, currency, *args, **kwargs):
    """
    First part of 2-stage payment processing.

    Successful requests will get a status of REGISTERED
    """
    params = {
        # TXN DETAILS
        'Amount': str(amount),
        'Currency': currency,
        'Description': kwargs.get('description', ''),
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
        # TOKENS
        'CreateToken': kwargs.get('create_token', 0),
        'StoreToken': kwargs.get('create_token', 0),
        # Misc
        'CustomerEMail': kwargs.get('customer_email', ''),
        'Basket': kwargs.get('basket_html', ''),
    }
    return _request(config.VPS_REGISTER_URL, TXTYPE_AUTHENTICATE, params)


def authorise(previous_txn, amount, description, **kwargs):
    """
    Second step of 2-stage payment processing

    Notes:
        - You can AUTHORIZE up to 115% of the original AUTHENTICATE request
        amount.
        - You have to AUTHORIZE within 90 days
    """
    params = {
        'Amount': str(amount),
        'Description': description,
        'RelatedVPSTxId': previous_txn.tx_id,
        'RelatedVendorTxCode': previous_txn.vendor_tx_code,
        'RelatedTxAuthNo': previous_txn.tx_auth_num,
        'RelatedSecurityKey': previous_txn.security_key,
        'ApplyAVSCV2': kwargs.get('avs_cv2', '0'),
    }
    return _request(config.VPS_AUTHORISE_URL, TXTYPE_AUTHORISE, params)


def cancel():
    """
    Cancel an existing card authentication

    This happens automatically after 90 days.
    """


def refund(previous_txn, amount, currency, description, **kwargs):
    """
    Refund a txn

    Notes:
        - You can send multiple refunds as long as the totals don't exceed the
        original amount.
    """
    params = {
        'Amount': str(amount),
        'Currency': currency,
        'Description': description,
        'RelatedVPSTxId': previous_txn.tx_id,
        'RelatedVendorTxCode': previous_txn.vendor_tx_code,
        'RelatedTxAuthNo': previous_txn.tx_auth_num,
        'RelatedSecurityKey': previous_txn.security_key,
    }
    return _request(config.VPS_REFUND_URL, TXTYPE_REFUND, params)
