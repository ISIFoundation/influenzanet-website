from django.contrib.auth.backends import ModelBackend

from .models import EpiworkUser, FakedUser
from django.contrib.auth.models import User as DjangoUser
from .logger import auth_notify
from apps.sw_auth.models import LoginToken

"""
 Customize Backend
 Real user identity is handled by EpiworkUser
"""

class EpiworkAuthBackend(ModelBackend):
    
    supports_object_permissions = False
    supports_anonymous_user = False

    def authenticate(self, username=None, password=None):
        try:
            auth_notify('authenticate', "check for %s" % username)
            user = EpiworkUser.objects.get(login=username)
            if user.check_password(password):
                try:
                    u = user.get_django_user()
                    # print u
                    auth_notify('auth_success',"success login '%s" % username )
                    u._epiwork_user = user # temporary store it in user
                    return u
                except DjangoUser.DoesNotExist:
                    return None
            else:
                auth_notify('auth_failure',"bad password for '%s'" % username)
              
        except EpiworkUser.DoesNotExist:
            auth_notify('auth_unknown',"user '%s' not found " % username)
            return None

    def get_user(self, user_id):
        """
         user_id is here the user if stored by django and refer to User of Django Model
        """
        try:
            return FakedUser.objects.get(pk=user_id)
        except FakedUser.DoesNotExist:
            return None

class EpiworkTokenBackend(ModelBackend):
    
    supports_object_permissions = False
    supports_anonymous_user = False

    def authenticate(self, login_token=None):
        """
        Authenticate
        use "login_token" name to be different from loginurl module
        """
        if login_token is None:
            return None
        try:
            auth_notify('authenticate', "check for %s" % login_token)
            token = LoginToken.objects.filter(key=login_token)
            if len(token) == 0:
                return None
    
            token = token[0]
            user = token.user
            if not token.is_valid():
                auth_notify('auth_failure',"expired token for '%s'" % user.login)
                return None
            
            u = user.get_django_user()
            auth_notify('auth_success',"success login '%s" % user.login )
            u._epiwork_user = user # temporary store it in user
            u._login_token = token
            return u
        except DjangoUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        """
         user_id is here the user if stored by django and refer to User of Django Model
        """
        try:
            return FakedUser.objects.get(pk=user_id)
        except FakedUser.DoesNotExist:
            return None
