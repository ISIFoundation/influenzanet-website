
from django.utils.http import int_to_base36, base36_to_int
from datetime import date
from random import choice
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail

from crypto import AES256
             
TOKEN_ACTIVATE = 1
TOKEN_PASSWORD = 2


class EpiworkToken:
    """
    Token management class 
    """
    def __init__(self, token=None):
        if not token is None:
            self.set_token(token)

    def set_token(self, token):
        try:
            ts36, r = token.split("-")
            self.random = r
            self.timestamp = base36_to_int(ts36)
        except ValueError:
            self.random = token
            self.timestamp = None
    
    def as_token(self):
        if self.timestamp is None:
            raise TokenException('Invalid timestamp token')
        if self.random is None:
            raise TokenException('Invalid random token')
        ts36 = int_to_base36(self.timestamp)
        token = ts36 + '-' + self.random
        return token
    
    def get_age(self):
        if self.timestamp is None:
            return None
        now = get_timestamp()
        return now - self.timestamp
    
    def is_empty(self):
        return bool(self.random is None or self.random == '')
    
    def validate(self, delay):
        age = self.get_age()
        if age is None:
            raise TokenException('Invalid token')
        if age > delay:
            raise TokenException('Token too old')
        return True 
    
    def renew(self):
        self.timestamp = get_timestamp()
        self.random = random_string(32)


class TokenException(Exception):
    pass             
             
def get_timestamp():
    tm = date.today() - date(2001, 1, 1)
    return tm.days

def random_string(length, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
    return ''.join([choice(allowed_chars) for i in range(length)])

def create_token():
    timestamp = get_timestamp()
    ts36 = int_to_base36(timestamp)
    token = ts36 + '-' + random_string(32)
    return token


def send_activation_email(user, site, renew=True, skip_younger=None):
    """
    Send activation email for a user
    renew : if False, check if the user already has a token and reuse it if possible
    skip_younger : Number of days, skip the user if the token is younger than that number
    """
    delay = settings.ACCOUNT_ACTIVATION_DAYS
    if renew:
        token = user.create_token_activate()
    else:
        create = False # should we recreate the token?
        token = user.get_token(TOKEN_ACTIVATE)
        if token.is_empty() :
            create = True
        else:
            age = token.get_age()
            if age >= delay:
                create = True
            if skip_younger is not None and age <= skip_younger:
                return False 
        if create:
            # recreate the token
            token = user.create_token_activate()
        else:
            # reuse the old token
            token = token.as_token()
            
    ctx_dict = { 
        'activation_key': token,
        'expiration_days': delay,
        'site': site 
    }
    subject = render_to_string('sw_auth/activation_email_subject.txt', ctx_dict)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    message = render_to_string('sw_auth/activation_email.txt', ctx_dict)
    
    send_mail(subject, message, None, [user.email])
    return True


"""
Cipher Config
SWAUTH_AES_KEY should contains a base64 encoded 32bytes (256bits) key used to encrypt username using AES256 algorithm
"""

def get_encryption_key():
    if not hasattr(settings,'SWAUTH_AES_KEY'):
        raise Exception("Encryption key not defined in settings")
    return settings.SWAUTH_AES_KEY
  
def encrypt_user(username):
    key = get_encryption_key()
    aes = AES256(key)
    return aes.encrypt(username)

"""
Decrypt username
""" 
def decrypt_user(username):
    key = get_encryption_key()
    aes = AES256(key)
    return aes.decrypt(username)