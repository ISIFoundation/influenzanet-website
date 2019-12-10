from django.db import models

# Create your models here.

class Session(models.Model):
    IDSession = models.CharField(max_length=60)
    Username = models.CharField(max_length=255, default="AnonymousUser")
    AESkey = models.CharField(max_length=255, blank=True, null=True)
    HMACkey = models.CharField(max_length=255, blank=True, null=True)

    expiration = models.DateTimeField('time expiration', blank=True, null=True)

    def __unicode__(self):
        return self.IDSession


class Temp(models.Model):
    IDSession = models.CharField(max_length=60)
    data = models.CharField(max_length=510, blank=True, null=True)

    def __unicode__(self):
        return self.IDSession