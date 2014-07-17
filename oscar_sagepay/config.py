from django.conf import settings


VPS_PROTOCOL = getattr(settings, 'OSCAR_SAGEPAY_VPS_PROTOCOL', '3.0')
VENDOR = settings.OSCAR_SAGEPAY_VENDOR

TEST_MODE = getattr(settings, 'OSCAR_SAGEPAY_TEST_MODE', True)
if TEST_MODE:
    VPS_URL = 'https://test.sagepay.com/gateway/service/vspdirect-register.vsp'
else:
    VPS_URL = 'https://live.sagepay.com/gateway/service/vspdirect-register.vsp'
