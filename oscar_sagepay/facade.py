"""
This module provides simple APIs that accept Oscar objects as parameters. It
decomposes these into dictionaries of data that are passed to the fine-grained
APIs of the gateway module.
"""
from oscar.apps.payment import exceptions as oscar_exceptions

from . import gateway, exceptions, models


def _get_bankcard_params(bankcard):
    """
    Extract the bankcard details from the bankcard obejct, and create a params
    dictionary
    """
    if hasattr(bankcard, 'number'):
        bankcard_number = bankcard.number
    else:
        bankcard_number = bankcard.card_number
    if hasattr(bankcard, 'name'):
        card_holder_name = bankcard.name
    else:
        card_holder_name = bankcard.card_holder_name
    if hasattr(bankcard, 'expiry_month'):
        bankcard_expiry = bankcard.expiry_month('%m%y')
    else:
        bankcard_expiry = bankcard.expiry_date.strftime('%m%y')

    params = {
        'bankcard_number': bankcard_number,
        'bankcard_cv2': getattr('bankcard', 'ccv', ''),
        'bankcard_name': card_holder_name,
        'bankcard_expiry': bankcard_expiry,
    }

    return params


def _get_country_code(country):
    if hasattr(country, 'code'):
        country_code = country.code
    else:
        country_code = country.iso_3166_1_a2

    return country_code


def authenticate(amount, currency, bankcard, shipping_address, billing_address,
                 description=None, order_number=None):
    """
    Perform an AUTHENTICATE request and return the TX ID if successful.
    """
    # Requests require a non-empty description
    if description is None:
        description = "<no description>"

    # Decompose Oscar objects into a dict of data to pass to gateway
    params = {
        'amount': amount,
        'currency': currency,
        'description': description,
    }

    params.update(_get_bankcard_params(bankcard))

    if order_number is not None:
        params['reference'] = order_number
    if shipping_address:
        params.update({
            'delivery_surname': shipping_address.last_name,
            'delivery_first_names': shipping_address.first_name,
            'delivery_address1': shipping_address.line1,
            'delivery_address2': shipping_address.line2,
            'delivery_city': shipping_address.line4,
            'delivery_postcode': shipping_address.postcode,
            'delivery_country': _get_country_code(shipping_address.country),
            'delivery_state': shipping_address.state,
            'delivery_phone': shipping_address.phone_number,
        })
    if billing_address:
        params.update({
            'billing_surname': billing_address.last_name,
            'billing_first_names': billing_address.first_name,
            'billing_address1': billing_address.line1,
            'billing_address2': billing_address.line2,
            'billing_city': billing_address.line4,
            'billing_postcode': billing_address.postcode,
            'billing_country': _get_country_code(billing_address.country),
            'billing_state': billing_address.state,
        })

    try:
        response = gateway.authenticate(**params)
    except exceptions.GatewayError as e:
        # Translate Sagepay gateway exceptions into Oscar checkout ones
        raise oscar_exceptions.PaymentError(e.message)

    # Check if the transaction was successful (need to distinguish between
    # customer errors and system errors).
    if not response.is_registered:
        raise oscar_exceptions.PaymentError(
            response.status_detail)

    return response.tx_id


def authorise(tx_id, amount=None, description=None, order_number=None):
    """
    Perform an AUTHORISE request against a previous transaction
    """
    try:
        txn = models.RequestResponse.objects.get(
            tx_id=tx_id)
    except models.RequestResponse.DoesNotExist:
        raise oscar_exceptions.PaymentError(
            "No historic transaction found with ID %s" % tx_id)

    # Marshall data for passing to gateway
    previous_txn = gateway.PreviousTxn(
        vendor_tx_code=txn.vendor_tx_code,
        tx_id=txn.tx_id,
        tx_auth_num=txn.tx_auth_num,
        security_key=txn.security_key)
    if amount is None:
        amount = txn.amount
    if description is None:
        description = "Authorise TX ID %s" % tx_id
    params = {
        'previous_txn': previous_txn,
        'amount': amount,
        'currency': txn.currency,
        'description': description,
    }
    if order_number is not None:
        params['reference'] = order_number
    try:
        response = gateway.authorise(**params)
    except exceptions.GatewayError as e:
        raise oscar_exceptions.PaymentError(e.message)
    if not response.is_ok:
        raise oscar_exceptions.PaymentError(
            response.status_detail)
    return response.tx_id


def refund(tx_id, amount=None, description=None, order_number=None):
    """
    Perform a REFUND request against a previous transaction. The passed tx_id
    should be from the AUTHORISE request that you want to refund against.
    """
    try:
        authorise_txn = models.RequestResponse.objects.get(
            tx_id=tx_id, tx_type=gateway.TXTYPE_AUTHORISE, status='OK'
        )
    except models.RequestResponse.DoesNotExist:
        raise oscar_exceptions.PaymentError((
            "No successful AUTHORISE transaction found with "
            "ID %s") % tx_id)

    previous_txn = gateway.PreviousTxn(
        vendor_tx_code=authorise_txn.vendor_tx_code,
        tx_id=authorise_txn.tx_id,
        tx_auth_num=authorise_txn.tx_auth_num,
        security_key=authorise_txn.security_key)
    if amount is None:
        amount = authorise_txn.amount
    if description is None:
        description = "Refund TX ID %s" % tx_id
    params = {
        'previous_txn': previous_txn,
        'amount': amount,
        'currency': authorise_txn.currency,
        'description': description,
    }
    if order_number is not None:
        params['reference'] = order_number
    try:
        response = gateway.refund(**params)
    except exceptions.GatewayError as e:
        raise oscar_exceptions.PaymentError(e.message)
    if not response.is_ok:
        raise oscar_exceptions.PaymentError(
            response.status_detail)
    return response.tx_id


def void(tx_id, order_number=None):
    """
    Cancel an existing transaction
    """
    try:
        authorise_txn = models.RequestResponse.objects.get(
            tx_id=tx_id, tx_type=gateway.TXTYPE_AUTHORISE, status='OK'
        )
    except models.RequestResponse.DoesNotExist:
        raise oscar_exceptions.PaymentError((
            "No successful AUTHORISE transaction found with "
            "ID %s") % tx_id)

    previous_txn = gateway.PreviousTxn(
        vendor_tx_code=authorise_txn.vendor_tx_code,
        tx_id=authorise_txn.tx_id,
        tx_auth_num=authorise_txn.tx_auth_num,
        security_key=authorise_txn.security_key)
    params = {
        'previous_txn': previous_txn,
    }
    if order_number is not None:
        params['reference'] = order_number
    try:
        response = gateway.void(**params)
    except exceptions.GatewayError as e:
        raise oscar_exceptions.PaymentError(e.message)
    if not response.is_ok:
        raise oscar_exceptions.PaymentError(
            response.status_detail)
    return response.tx_id
