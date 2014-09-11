from oscar_sagepay import models


def test_audit_model_records_key_request_params_as_fields():
    instance = models.RequestResponse()
    params = {
        'VPSProtocol': '3.0',
        'TxType': 'PAYMENT',
        'Vendor': 'oscar',
        'VendorTxCode': 'req_1',
        'Amount': '10.99',
        'Currency': 'GBP',
    }
    instance.record_request(params)
    assert instance.protocol == params['VPSProtocol']
    assert instance.tx_type == params['TxType']
    assert instance.vendor == params['Vendor']
    assert instance.amount == params['Amount']
    assert instance.currency == params['Currency']


def test_audit_model_records_raw_request_params():
    instance = models.RequestResponse()
    params = {
        'VPSProtocol': '3.0',
        'TxType': 'PAYMENT',
        'Vendor': 'oscar',
        'VendorTxCode': 'req_1',
        'Amount': '10.99',
        'Currency': 'GBP',
    }
    instance.record_request(params)
    assert isinstance(instance.raw_request, dict)
    assert 'Vendor' in instance.raw_request


def test_audit_model_obscures_cardholder_data():
    instance = models.RequestResponse()
    params = {
        'VPSProtocol': '3.0',
        'TxType': 'PAYMENT',
        'Vendor': 'oscar',
        'VendorTxCode': 'req_1',
        'Amount': '10.99',
        'Currency': 'GBP',
        'CardHolder': 'Barry Chuckle',
        'CardNumber': '4111111111111111',
        'ExpiryDate': '0216',
        'CV2': '123',
        'CardType': 'VISA',
    }
    instance.record_request(params)
    assert instance.raw_request['CardHolder'] == '<removed>'
    assert instance.raw_request['CardNumber'] == '<removed>'
    assert instance.raw_request['ExpiryDate'] == '<removed>'
    assert instance.raw_request['CV2'] == '<removed>'
    assert instance.raw_request['CardType'] == '<removed>'
