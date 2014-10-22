import httplib
import collections
import random
import logging

import requests
from oscar.apps.payment import bankcards

from . import models, exceptions, config, wrappers

logger = logging.getLogger('oscar.sagepay')

# TxTypes
TXTYPE_PAYMENT = 'PAYMENT'
TXTYPE_DEFERRED = 'DEFERRED'
TXTYPE_AUTHENTICATE = 'AUTHENTICATE'
TXTYPE_AUTHORISE = 'AUTHORISE'
TXTYPE_REFUND = 'REFUND'
TXTYPE_VOID = 'VOID'


__all__ = ['PreviousTxn', 'authenticate', 'authorise', 'void', 'refund']


# Datastructure for wrapping up details of a previous transaction
PreviousTxn = collections.namedtuple(
    'PreviousTxn', ('vendor_tx_code', 'tx_id', 'tx_auth_num', 'security_key'))


def _card_type(bankcard_number):
    """
    Convert card-number into appropriate card type that Sagepay will
    recognise.
    """
    # Oscar provides a function to do the card-type recognition but we need to
    # map into the values that Sagepay accepts.
    oscar_type = bankcards.bankcard_type(bankcard_number)
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


def _vendor_tx_code(reference):
    return u'%s-%s-%0.6d' % (
        config.VENDOR_TX_CODE_PREFIX,
        reference, random.randint(0, 1000000))


def _request(url, tx_type, params, reference):
    vendor_tx_code = _vendor_tx_code(reference)
    request_params = {
        'VPSProtocol': config.VPS_PROTOCOL,
        'Vendor': config.VENDOR,
        'TxType': tx_type,
        'VendorTxCode': vendor_tx_code,
    }
    request_params.update(params)

    # Create an audit model with request info
    rr = models.RequestResponse.new(reference, request_params)

    logger.info("Vendor TX code: %s, making %s request to %s",
                vendor_tx_code, tx_type, url)
    try:
        http_response = requests.post(url, request_params)
    except requests.exceptions.RequestException as e:
        logger.error("Vendor TX code: %s, HTTP connection error: %s",
                     vendor_tx_code, e.message)
        raise exceptions.GatewayError(
            "HTTP error: %s" % e.message)

    if http_response.status_code != httplib.OK:
        # Sagepay seem to return a status 200 even for bad requests
        logger.error("Vendor TX code: %s, HTTP response error: %s - %s",
                     vendor_tx_code, http_response.status_code,
                     http_response.content)
        raise exceptions.GatewayError(
            "Sagepay server returned a %s response with content %s" % (
                http_response.status_code, http_response.content))

    sp_response = wrappers.Response(vendor_tx_code, http_response.content)
    logger.info("Vendor TX code: %s, Response status %s - %s",
                vendor_tx_code, sp_response.status, sp_response.status_detail)

    # Update audit model with response info
    rr.record_response(sp_response)
    rr.save()

    return sp_response


def authenticate(amount, currency, reference='', **kwargs):
    """
    First part of 2-stage payment processing.

    Successful requests will get a status of REGISTERED
    """
    # Ensure no None values in kwargs
    for k, v in kwargs.items():
        if v is None:
            kwargs[k] = ''

    bankcard_number = kwargs.get('bankcard_number', '')
    params = {
        # TXN DETAILS
        'Amount': str(amount),
        'Currency': currency,
        'Description': kwargs.get('description', ''),
        # BANKCARD DETAILS
        'CardType': _card_type(bankcard_number),
        'CardNumber': bankcard_number,
        'CV2': kwargs.get('bankcard_ccv', ''),
        # Required field, that is not documented, if not set it the request
        # returns the error: '5017 : The Security Code(CV2) is required.'
        'ApplyAVSCV2': '2',
        'CardHolder': kwargs.get('bankcard_name', ''),
        'ExpiryDate': kwargs.get('bankcard_expiry', ''),
        # BILLING DETAILS
        'BillingSurname': kwargs.get('billing_surname', '')[:20],
        'BillingFirstnames': kwargs.get('billing_first_names', '')[:20],
        'BillingAddress1': kwargs.get('billing_address1', '')[:100],
        'BillingAddress2': kwargs.get('billing_address2', '')[:100],
        'BillingCity': kwargs.get('billing_city', '')[:40],
        'BillingPostCode': kwargs.get('billing_postcode', '')[:10],
        'BillingCountry': kwargs.get('billing_country', '')[:2],
        'BillingState': kwargs.get('billing_state', '')[:2],
        'BillingPhone': kwargs.get('billing_phone', '')[:20],
        # DELIVERY DETAILS
        'DeliverySurname': kwargs.get('delivery_surname', '')[:20],
        'DeliveryFirstnames': kwargs.get('delivery_first_names', '')[:20],
        'DeliveryAddress1': kwargs.get('delivery_address1', '')[:100],
        'DeliveryAddress2': kwargs.get('delivery_address2', '')[:100],
        'DeliveryCity': kwargs.get('delivery_city', '')[:40],
        'DeliveryPostCode': kwargs.get('delivery_postcode', '')[:10],
        'DeliveryCountry': kwargs.get('delivery_country', '')[:2],
        'DeliveryState': kwargs.get('delivery_state', '')[:2],
        'DeliveryPhone': kwargs.get('delivery_phone', '')[:20],
        # TOKENS
        'CreateToken': kwargs.get('create_token', 0),
        'StoreToken': kwargs.get('create_token', 0),
        # Misc
        'CustomerEMail': kwargs.get('customer_email', ''),
        'Basket': kwargs.get('basket_html', ''),
    }
    return _request(config.VPS_REGISTER_URL, TXTYPE_AUTHENTICATE, params,
                    reference)


def authorise(previous_txn, amount, currency, description,
              reference='', **kwargs):
    """
    Second step of 2-stage payment processing

    Notes:
        - You can AUTHORIZE up to 115% of the original AUTHENTICATE request
        amount.
        - You have to AUTHORIZE within 90 days
    """
    params = {
        'Amount': str(amount),
        'Currency': currency,
        'Description': description,
        'RelatedVPSTxId': previous_txn.tx_id,
        'RelatedVendorTxCode': previous_txn.vendor_tx_code,
        'RelatedTxAuthNo': previous_txn.tx_auth_num,
        'RelatedSecurityKey': previous_txn.security_key,
        'ApplyAVSCV2': kwargs.get('avs_cv2', '0'),
    }
    return _request(config.VPS_AUTHORISE_URL, TXTYPE_AUTHORISE, params,
                    reference)


def refund(previous_txn, amount, currency, description, reference='',
           **kwargs):
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
    return _request(config.VPS_REFUND_URL, TXTYPE_REFUND, params, reference)


def void(previous_txn, reference=''):
    """
    Cancel an AUTHORISED transaction (before it settles)

    This can only be done before the end of the day that the AUTHORISE request
    takes place. After that, a REFUND is required.
    """
    params = {
        'VPSTxId': previous_txn.tx_id,
        'VendorTxCode': previous_txn.vendor_tx_code,
        'TxAuthNo': previous_txn.tx_auth_num,
        'SecurityKey': previous_txn.security_key,
    }
    return _request(config.VPS_VOID_URL, TXTYPE_VOID, params, reference)
