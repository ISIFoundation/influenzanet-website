'''
Created on 5 nov. 2018

@author: ClementTurbelin
'''

from base64 import  b64decode
from binascii import hexlify
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import AES
from apps.sw_auth.models import EpiworkUser
from django.conf import settings
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256, HMAC

AES_KEY_LENGTH = 32
HMAC_KEY_LENGTH = 32
IV_LENGTH = 16

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
    def __init__(self, aesKey, hmacKey, login): # , IV=0
        self.aesKey = aesKey
        self.hmacKey = hmacKey
        self.login = login
        #self.IV = IV


    def to_json(self):
        return {
        'aes': hexlify(self.aesKey),
        'hmac': hexlify(self.hmacKey),
        'login': self.login,
        #'IV' : self.IV
    }


class AscorAPI:

    ACTION_HANDSHAKE = 'sym_key_exchange_auth'

    def __init__(self):
        pass

    def load_private_key(self):

        f = open(settings.ASCOR_RSA_PRIVATE_KEY, 'r')
        return RSA.importKey(f)


    def AES256BCB(self, msg, keys, iv):
        cipher = AES.new(keys.aesKey, AES.MODE_CBC, iv)
        msgEnc = cipher.encrypt(msg)

        return msgEnc

    def hash_hmac(self, msg):
        sha_hash = SHA256.new(msg)
        hashmsg = sha_hash.hexdigest()
        return hashmsg

    def _decodeHandshake(self, data):

        # Encrypted text
        cftext = b64decode(str(data))

        pkey = self.load_private_key()

        cipher = PKCS1_OAEP.new(pkey)

        text = cipher.decrypt(cftext)

        #Obsolete?
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

        #random IV generation
        IV = get_random_bytes(IV_LENGTH)

        #hash calculation
        hashmsg_dec = self.hash_hmac(data)

        # Format response
        resMSG = {
            'login' : login,
            'hash' : hashmsg_dec
            }

        # AES encryption of the response
        resMsgEnc = self.AES256CBC(resMSG, hs, IV)
        #cipher = AES.new(hs.aesKey, AES.MODE_CBC)
        #resMsgEnc = cipher.encrypt(resMSG)

        HmacObject = HMAC.new(hs.hmacKey, resMsgEnc+IV , "SHA256")

        response = {
            'body' : {
                'MSG_ENC' : resMsgEnc
            },
            'IV' : IV,
            'Hmac' : HmacObject.hexdigest()
        }

        return response

    def auth(self, data):
        #TODO : recuperation BDD?Cookies? valeurs handshakes + valeurs retournees par client API
        r= {}

        hashmsg_dec = self.hash_hmac(data)
        if not hashmsg_dec == data.Hmac:
            raise APIError("Bad hash, expect %s got %s " % (data.Hmac,hashmsg_dec) )

        IV = get_random_bytes(IV_LENGTH)


        aes = AES.new(data.msg, AES.MODE_CBC, data.iv)
        decd = aes.decrypt(data.msg)


        return r

