from django.conf import settings


VPS_PROTOCOL = getattr(settings, 'OSCAR_SAGEPAY_VPS_PROTOCOL', '3.0')
VENDOR = settings.OSCAR_SAGEPAY_VENDOR

TEST_MODE = getattr(settings, 'OSCAR_SAGEPAY_TEST_MODE', True)
if TEST_MODE:
    VPS_REGISTER_URL = 'https://test.sagepay.com/Simulator/VSPDirectGateway.asp'
    VPS_AUTHORISE_URL = 'https://test.sagepay.com/Simulator/VSPServerGateway.asp?Service=VendorAuthoriseTx'
    VPS_REFUND_URL = 'https://test.sagepay.com/Simulator/VSPServerGateway.asp?Service=VendorRefundTx'
    VPS_VOID_URL = 'https://test.sagepay.com/Simulator/VSPServerGateway.asp?Service=VendorVoidTx'
else:
    VPS_REGISTER_URL = 'https://live.sagepay.com/gateway/service/vspdirect-register.vsp'
    VPS_AUTHORISE_URL = VPS_REFUND_URL = VPS_REGISTER_URL = VPS_VOID_URL

VENDOR_TX_CODE_PREFIX = getattr(settings, "OSCAR_SAGEOAY_TX_CODE_PREFIX",
                                "oscar_sagepay_")
