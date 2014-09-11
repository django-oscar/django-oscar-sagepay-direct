import json

from django.db import models
from django.utils.timezone import now

from . import wrappers


class RequestResponse(models.Model):
    # Request fields
    protocol = models.CharField(max_length=12)
    tx_type = models.CharField(max_length=64)
    vendor = models.CharField(max_length=128)
    vendor_tx_code = models.CharField(max_length=128, db_index=True)

    amount = models.DecimalField(
        decimal_places=2, max_digits=12, blank=True, null=True)
    currency = models.CharField(max_length=3, blank=True)
    description = models.CharField(max_length=512, blank=True)

    raw_request_json = models.TextField(blank=True)
    request_datetime = models.DateTimeField(null=True, blank=True)

    # Response fields
    status = models.CharField(max_length=128, blank=True)
    status_detail = models.TextField(blank=True)
    tx_id = models.CharField(
        max_length=128, db_index=True, blank=True)
    tx_auth_num = models.CharField(max_length=32, blank=True)
    security_key = models.CharField(max_length=128, blank=True)

    raw_response = models.TextField(blank=True)
    response_datetime = models.DateTimeField(null=True, blank=True)

    related_tx_id = models.CharField(max_length=128, blank=True,
                                     db_index=True)

    class Meta:
        ordering = ('-request_datetime',)

    def __unicode__(self):
        return self.vendor_tx_code

    @classmethod
    def new(cls, params):
        instance = cls()
        instance.record_request(params)
        instance.save()
        return instance

    @property
    def raw_request(self):
        return json.loads(self.raw_request_json)

    def request_as_html(self):
        rows = []
        for k, v in sorted(self.raw_request.items()):
            rows.append(
                '<dt>%s</dt><dd>%s</dd>' % (k, v))
        return '<dl>%s</dl>' % ''.join(rows)
    request_as_html.allow_tags = True

    def record_request(self, params):
        """
        Update fields based on request params
        """
        self.protocol = params['VPSProtocol']
        self.tx_type = params['TxType']
        self.vendor = params['Vendor']
        self.vendor_tx_code = params['VendorTxCode']
        self.amount = params.get('Amount', None)
        self.currency = params.get('Currency', '')
        self.description = params.get('Description', '')

        # Where relevant, we keep a reference to the transaction that this one
        # is a follow-up to. We need to this to look up auth numbers before
        # doing refunds.
        self.related_tx_id = params.get('RelatedVPSTxId', '')

        # Remove cardholder data so we can keep our PCI compliance level down
        sensitive_fields = (
            'CardHolder', 'CardNumber', 'ExpiryDate', 'CV2', 'CardType')
        safe_params = params.copy()
        for key in sensitive_fields:
            if key in safe_params:
                safe_params[key] = '<removed>'
        if 'Amount' in safe_params:
            safe_params['Amount'] = str(safe_params['Amount'])
        self.raw_request_json = json.dumps(safe_params)
        self.request_datetime = now()

    def record_response(self, response):
        """
        Update fields based on Response instance
        """
        self.status = response.status
        self.status_detail = response.status_detail
        self.tx_id = response.tx_id
        self.tx_auth_num = response.tx_auth_num
        self.security_key = response.security_key
        self.raw_response = response.raw
        self.response_datetime = now()

    @property
    def response(self):
        try:
            response = wrappers.Response(
                self.vendor_tx_code, self.raw_response)
        except Exception:
            response = wrappers.EmptyResponse
        return response

    @property
    def is_error(self):
        return self.response.is_error

    @property
    def is_successful(self):
        return self.response.is_successful

    @property
    def response_time_as_ms(self):
        delta = self.response_datetime - self.request_datetime
        return 1000 * delta.seconds + delta.microseconds / 1000
