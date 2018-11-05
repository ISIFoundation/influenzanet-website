'''
Created on 5 nov. 2018

@author: ClementTurbelin
'''

from base64 import  b64decode
from binascii import hexlify
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from apps.sw_auth.models import EpiworkUser
from django.conf import settings

AES_KEY_LENGTH = 32
HMAC_KEY_LENGTH = 32


class APIError(Exception):
    
    def __init__(self, message, data=None):
        super(APIError, self).__init__(message)
        self.data = data
        
    def to_json(self):
        if isinstance(self.data, HandshakeData):
            data = self.data.to_json()
        else:
            data = self.data
        return {
         'type': 'APIError',
         'message': self.message,
         'data': data
        }
    

class HandshakeData:
    def __init__(self, aesKey, hmacKey, login):
        self.aesKey = aesKey
        self.hmacKey = hmacKey
        self.login = login
    
    def to_json(self):
        return {
        'aes': hexlify(self.aesKey),
        'hmac': hexlify(self.hmacKey),
        'login': self.login
    }

class AscorAPI:

    ACTION_HANDSHAKE = 'sym_key_exchange'


    def __init__(self):
        pass

    def load_private_key(self):
        f = open(settings.ASCOR_RSA_PRIVATE_KEY, 'r')
        return RSA.importKey(f)

    def _decodeHandshake(self, data):
        
        # Encrypted text
        cftext = b64decode(str(data))

        pkey = self.load_private_key()

        cipher = PKCS1_OAEP.new(pkey)

        text = cipher.decrypt(cftext)

        payload = text.split(':::')
        
        if not isinstance(payload, list):
            raise APIError("Unable to parse payload")

        if len(payload) < 3:
            raise APIError("Bad payload count")

        hd = HandshakeData(payload[0], payload[1], payload[2])

        return hd

    def handshake(self, data):
        
        hs = self._decodeHandshake(data)

        
        if not len(hs.aesKey) == AES_KEY_LENGTH:
            raise APIError("Bad AES key length, expect %d got %d " % (AES_KEY_LENGTH,len(hs.aesKey), ), hs)
    
        if not len(hs.hmacKey) == HMAC_KEY_LENGTH:
            raise APIError("Bad HMAC key length, expect %d got %d " % (HMAC_KEY_LENGTH, len(hs.hmacKey), ), hs)
    
        login = hs.login

        
        try: 
            user = EpiworkUser.objects.get(login=login)
        except EpiworkUser.DoesNotExist:
            raise APIError("Bad login", hs)    

        return hs