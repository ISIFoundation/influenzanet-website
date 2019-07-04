# -*- coding: utf-8 -*-
'''
Created on 5 nov. 2018

@author: ClementTurbelin
'''

from base64 import  b64decode
from binascii import hexlify, unhexlify
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP,AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256, HMAC

from django.conf import settings
from django.contrib import auth

from apps.sw_auth.models import EpiworkUser


import json

AES_KEY_LENGTH = 32 # #Valeurs a mettre en brut?
HMAC_KEY_LENGTH = 32
IV_LENGTH = 16

BLOCK_SIZE = 16  # Bytes
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * \
                chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]


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
    def __init__(self, aesKey, hmacKey):
        self.aesKey = aesKey
        self.hmacKey = hmacKey

    def to_json(self):
        return {
        'aes': hexlify(self.aesKey),
        'hmac': hexlify(self.hmacKey),
    }


class AuthData:
    def __init__(self, enc, IV, Hmac):
        self.enc = enc
        self.IV = IV
        self.Hmac = Hmac

    def to_json(self):
        return {
        'ENC': hexlify(self.enc),
        'IV': hexlify(self.IV),
        'HMAC': hexlify(self.Hmac)
    }

class AscorAPI:

    ACTION_HANDSHAKE = 'sym_key_exchange_auth'

    ACTION_SURVEY ='show_survey_list'

    def __init__(self):
        pass

    def load_private_key(self):
        f = open(settings.ASCOR_RSA_PRIVATE_KEY, 'r')
        return RSA.importKey(f)


    def AES256CBC(self, msg, key, iv):
        cipher = AES.new(key, AES.MODE_CBC, iv)
        msg_pad = pad(msg)
        msgEnc = cipher.encrypt(msg_pad)
        return msgEnc

    def hash_hmac(self, msg):
        sha_hash = SHA256.new(msg)
        hashmsg = sha_hash.hexdigest()
        return hashmsg

    def _decodeHandshake(self, data):
        cftext = b64decode(str(data))
        pkey = self.load_private_key()
        cipher = PKCS1_OAEP.new(pkey)
        text = cipher.decrypt(cftext)
        payload = [text[:int(AES_KEY_LENGTH*2)], text[int(HMAC_KEY_LENGTH*2):]]

        # Voir pour + de verifications
        if len(text) != (len(payload[0])+len(payload[1])) :
            print("Unable to parse payload")
            raise APIError("Unable to parse payload")

        hsd = HandshakeData(payload[0], payload[1])
        return hsd

    def handshake(self,request, data):
        hs = self._decodeHandshake(data['RSA4096'])
        #print("hs : "+str(hs))
        aesKeyBin = unhexlify(hs.aesKey)
        HMACkeyBin = unhexlify(hs.hmacKey)

        if not len(aesKeyBin) == AES_KEY_LENGTH:
            print("Bad AES key length, expect %d got %d " % (AES_KEY_LENGTH, len(aesKeyBin), ), hs)
            raise APIError("Bad AES key length, expect %d got %d " % (AES_KEY_LENGTH,len(aesKeyBin), ), hs)

        if not len(HMACkeyBin) == HMAC_KEY_LENGTH:
            print("Bad HMAC key length, expect %d got %d " % (HMAC_KEY_LENGTH, len(HMACkeyBin), ), hs)
            raise APIError("Bad HMAC key length, expect %d got %d " % (HMAC_KEY_LENGTH, len(HMACkeyBin), ), hs)

        AES256 = data['AES256']

        hmac_cree = HMAC.new(hs.hmacKey, digestmod=SHA256.new())
        hmac_cree.update(AES256['IV']+AES256['ENC'])
        hmac_hexa = hmac_cree.hexdigest()

        if hmac_hexa == AES256['HMAC']:
            iv_bin = unhexlify(AES256['IV'])
            if not len(iv_bin) == IV_LENGTH:
                print("Bad IV  length, expect %d got %d " % (IV_LENGTH,len(AES256['IV'])))

            AESCipher = AES.new(aesKeyBin, AES.MODE_CBC, iv_bin)
            msg_decrypt = unpad(AESCipher.decrypt(b64decode(AES256['ENC'])))
            msg_decrypt_json = json.loads(msg_decrypt)

            #authentification a verifier
            login = msg_decrypt_json['login']
            password = msg_decrypt_json['password']

        try:
            user = auth.authenticate(username=login, password=password)
            if user is None :
                print("Bad login user")
                raise APIError("Bad login")
            auth.login(request, user)
            print("session key :" + str(request.session._session_key))
            #print("Apres : "+str(vars(request.session)))
            id_session = request.session._session_key
        except EpiworkUser.DoesNotExist:
            raise APIError("Bad login")

        #random IV generation
        IV = get_random_bytes(IV_LENGTH)

        #hash calculation
        hashmsg_dec = self.hash_hmac(data['RSA4096'])

        # Format response, TODO :fournir un token utilisateur
        resMSG = {
            'token' : id_session,  #Il faut que
            'hash' : hashmsg_dec,
            }

        # AES encryption of the response
        resMSGjson = json.dumps(resMSG)
        resMsgEnc = self.AES256CBC(resMSGjson, aesKeyBin, IV)
        #HmacObject = HMAC.new(HMACkeyBin, resMsgEnc+IV , "SHA256")
        HmacObject = HMAC.new(hs.hmacKey, digestmod=SHA256.new())
        HmacObject.update(hexlify(IV)+hexlify(resMsgEnc))
        HmacObject_hex = HmacObject.hexdigest()

        res = {
            'ENC' : hexlify(resMsgEnc),
            'IV' : hexlify(IV),
            'HMAC': HmacObject_hex,
        }
        return(res)
