from django.conf import settings

if not hasattr(settings, 'ASCOR_RSA_PRIVATE_KEY'):
    raise Exception("Ascor config: missing private key configuration")

if not hasattr(settings, 'ASCOR_RSA_PUBLIC_KEY'):
    raise Exception("Ascor config: missing private key configuration")

ASCOR_DEBUG = getattr(settings, 'ASCOR_DEBUG', False)