import json

from django.db import models


class RequestResponse(models.Model):
    # Request fields
    protocol = models.CharField(max_length=12, blank=True)
    tx_type = models.CharField(max_length=64, blank=True)
    vendor = models.CharField(max_length=128, blank=True)
    amount = models.DecimalField(
        decimal_places=2, max_digits=12, blank=True, null=True)
    currency = models.CharField(max_length=3, blank=True)
    raw_request_json = models.TextField(blank=True)

    # Response fields
    status = models.CharField(max_length=128, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)

    @property
    def raw_request(self):
        return json.loads(self.raw_request_json)

    @property
    def vendor_tx_code(self):
        return 'request%s' % self.id

    def record_request(self, params):
        """
        Update fields based on request params
        """
        self.protocol = params['VPSProtocol']
        self.tx_type = params['TxType']
        self.vendor = params['Vendor']
        self.amount = params['Amount']
        self.currency = params['Currency']

        # Remove cardholder data so we can keep our PCI compliance level down
        sensitive_fields = (
            'CardHolder', 'CardNumber', 'ExpiryDate', 'CV2', 'CardType')
        safe_params = params.copy()
        for key in sensitive_fields:
            safe_params[key] = '<removed>'
        self.raw_request_json = json.dumps(safe_params)

    def record_response(self, response):
        """
        Update fields based on Response instance
        """
        self.status = response.status
