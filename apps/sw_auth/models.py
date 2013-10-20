from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db import transaction
from django.contrib.auth.models import get_hexdigest, check_password, User, UNUSABLE_PASSWORD
from django.core.urlresolvers import reverse
from datetime import datetime
import utils
import random
import sys
from .utils import create_token, encrypt_user, decrypt_user, EpiworkToken
from .logger import auth_notify
from apps.survey.models import SurveyUser
from apps.partnersites.models import Site

# Connect to login_in signal
# This allow us to set the real user id in session
from django.contrib.auth import user_logged_in

# Connect to auth login signal
def login_handler(sender,**kwargs):
    auth_notify('login_handler','ok')
    user = kwargs['user']
    request = kwargs['request']
    epiwork_user = None
    if hasattr(user, '_epiwork_user' ):
        epiwork_user = user._epiwork_user
    else:
        if  user.is_staff:
            # Staff users should have same username
            epiwork_user = EpiworkUser.objects.get(login=user.username)
        
    if epiwork_user is not None:
        request.session['epiwork_user'] = epiwork_user # store real user in session

user_logged_in.connect(login_handler)
    
def get_random_user_id():
    """
    Try to set a random id for a user
    To limit collision, can try several times
    """
    # get a random int 
    i = 10 # try a maximum of 10 times
    while i > 0:
        id = random.randint(1, sys.maxint)
        try:
            u = EpiworkUser.objects.get(id=id)
        except EpiworkUser.DoesNotExist:
            return id
        --i
    return None

        

class EpiworkUserManager(models.Manager):

    @transaction.commit_manually()
    def create_user(self, login, email, password):
        user = EpiworkUser()
        user.id = get_random_user_id()
        if user.id is None:
            raise Exception('Unable to find user id')
        user.login = login
        user.email = email
        user.set_password(password)
        
        # Create a random username and a fake email
        dj_username = utils.random_string(30)
        dj_email = "%s@localhost" % (dj_username,)
        
        user.set_user(dj_username)
       
        try:
            django_user = User.objects.create_user(dj_username, dj_email)
            django_user.is_active = False
            django_user.save()
            user.save()
            transaction.commit()
        except:
            transaction.rollback()
            raise 
        return user
                   
class EpiworkUser(models.Model):
    """"
    Handle the identity of a user account
    It is linked to a "fake" django user account in the "user" field
    """
    
    id = models.BigIntegerField(primary_key=True)
    user = models.CharField(_('username'), max_length=255, unique=True) # encrypted user name in auth_user
    email = models.CharField(_('e-mail address'),max_length=255) # encrypted email
    login = models.CharField(_('username'),max_length=255, unique=True) # 
    password = models.CharField(_('password'), max_length=128) # sha1 hash
    token_password = models.CharField(max_length=40)
    token_activate = models.CharField(max_length=40)
    is_active = models.BooleanField(default=False)
    
    anonymize_warn = models.DateField(null=True) # Date of warning if account should be anonymized

    objects = EpiworkUserManager()
    
    # Get the user login
    def get_user(self):
        return decrypt_user(self.user)

    def set_user(self, username):
        self.user = encrypt_user(username)

    def set_password(self, raw_password):
        if raw_password is None:
            self.set_unusable_password()
        else:
            import random
            algo = 'sha1'
            salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
            hsh = get_hexdigest(algo, salt, raw_password)
            self.password = '%s$%s$%s' % (algo, salt, hsh)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
         
    def get_django_user(self):
        username = self.get_user()
        return User.objects.get(username=username)

    def get_fake_user(self):
        username = self.get_user()
        return FakedUser.objects.get(username=username)
    
    def create_token_password(self):
        token = create_token()
        self.token_password = token
        self.save()
        return token
    
    def create_token_activate(self):
        token = create_token()
        self.token_activate = token
        self.save()
        return token
    
    def get_token(self, token_type):
        if token_type == utils.TOKEN_ACTIVATE:
            return EpiworkToken(self.token_activate)
        elif token_type == utils.TOKEN_PASSWORD:
            return EpiworkToken(self.token_password)
        return None
    
    def create_login_token(self, usage_left=1, expires=None, next=None):
        login = LoginToken()
        login.key = create_token()
        login.user = self
        login.expires = expires
        login.next = next
        login.save()
        return login
    
    @transaction.commit_manually()
    def activate(self):
        self.is_active = True
        self.token_activate = ''
        dju = self.get_django_user()
        dju.is_active = True
        try:
            self.save()
            dju.save()
            transaction.commit()
            return True
        except:
            transaction.rollback()
            return False

    def personalize(self, user):
        user.username = self.login
        user.email = self.email
        
    def anonymize(self):
        # create a unique user name (not used)
        name = 'user'+str(self.id)+'-'+ utils.random_string(6)
        self.login = name
        self.email = name+'@'+'localhost'
        self.password = UNUSABLE_PASSWORD 
        self.is_active = False
        
        # get the django user
        user = self.get_django_user()
        # user = django user
        try:
            # remove participant info
            susers = SurveyUser.objects.filter(user=user)
            for su in susers:
                print " > anonymizing participant %d" % su.id
                su.name = 'part' + str(su.id) +'_'+ utils.random_string(4) # random tail to expect uniqueness
                su.save() 
            
            user.first_name = 'nobody'
            user.last_name = 'nobody'
            user.password = UNUSABLE_PASSWORD
            user.is_active = False
            user.save()
            self.save()
            transaction.commit()
            return True
        except Exception:
            transaction.rollback()
            raise
        
class AnonymizeLog(models.Model):
    
    EVENT_WARNING   = 1 # Anonymize Warning sent
    EVENT_DONE      = 2 # Account anonymized
    EVENT_MANUALLY  = 3 # Account anonymized by administrator
    EVENT_CANCELLED = 4 # Account anonymization cancelled by user login
    
    user = models.ForeignKey(EpiworkUser)
    date = models.DateTimeField(auto_now_add=True)
    event = models.IntegerField(null=False)

class LoginToken(models.Model):
    user = models.ForeignKey(EpiworkUser)
    key = models.CharField(max_length=40, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    usage_left = models.IntegerField(null=True, default=1)
    expires = models.DateTimeField(null=True)
    next = models.CharField(null=True, max_length=200)

    def __unicode__(self):
        return '%s (%s)' % (self.key, self.user.username)

    def is_valid(self):
        """
        Check if the key is valid.

        Key validation checks the value of ``usage_left`` and ``expires``
        properties of the key. If both are ``None`` then the key is always
        valid.
        """
        if self.usage_left is not None and self.usage_left <= 0:
            return False
        if self.expires is not None and self.expires < datetime.now():
            return False
        return True

    def update_usage(self):
        """
        Update key usage counter.

        This only relevant if the ``usage_left`` property is used.
        """
        if self.usage_left is not None and self.usage_left > 0:
            self.usage_left -= 1
            self.save()
    
    def get_url(self):
        """
        Get the absolute url to use the token
        """
        domain = Site.objects.get_current()
        path = reverse('auth_login_token', kwargs={'login_token': self.key}).strip('/')
        return 'http://%s/%s' % (domain, path)

class FakedUser(User):
    """
    Fake user to replace User django
    This proxy class protect the user object from a save action
    """

    class Meta:
        proxy = True
        """"
        """ 
    
    
    def personalize(self, user):
        """
        Personalize the account with real information
        """
        self.username = user.login
        self.email = user.email
        
    def save(self, force_insert=False, force_update=False, using=None):
        raise Exception
        """
            Fake User is readonly once authenticated this account
        """
    
    def safe_save(self, force_insert=False, force_update=False, using=None):
        self.save_base( force_insert=False, force_update=False, using=None)
        
# Provide a fake user list
class EpiworkUserProvider(object):
    
    def __init__(self):
        self.users = EpiworkUser.objects.filter(is_active=True)  
        self.iter = None
        
    def __iter__(self):
        self.iter = self.users.__iter__()
        return self
    
    def fake(self, user):
        django_user = user.get_fake_user()
        django_user.personalize(user)
        return django_user
    
    def get_by_login(self, login):
        return self.fake(EpiworkUser.objects.get(login=login))
    
    def get_by_email(self, email):
        return self.fake(EpiworkUser.objects.get(email__iexact=email))
    
    def next(self): 
        return self.fake(next(self.iter))