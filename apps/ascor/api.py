'''
Created on 5 nov. 2018

@author: ClementTurbelin
'''

from base64 import  b64decode, b64encode
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from django.conf import settings
from binascii import hexlify

class AscorAPI:

    ACTION_HANDSHAKE = 'sym_key_exchange'


    def __init__(self):
        pass

    def load_private_key(self):
        f = open(settings.ASCOR_RSA_PRIVATE_KEY, 'r')
        return RSA.importKey(f)

    def handshake(self, data):

        text = b64decode(str(data))

        print data
        print hexlify(text)

        print len(text)

        pkey = self.load_private_key()

        cipher = PKCS1_OAEP.new(pkey)

        payload = cipher.decrypt(text)

        print payload
        return payload