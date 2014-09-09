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

    @property
    def is_error(self):
        return not self.is_successful and not self.is_registered
