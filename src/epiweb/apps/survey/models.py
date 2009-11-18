from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

import uuid

class Survey(models.Model):
    survey_id = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    definition = models.TextField()
    active = models.BooleanField()

class Participation(models.Model):
    user = models.ForeignKey(User)
    survey = models.ForeignKey(Survey)
    date = models.DateTimeField(auto_now_add=True)
    epidb_id = models.CharField(max_length=36, null=True)
    previous_participation = models.ForeignKey('self')
    previous_participation_date = models.DateTimeField()

class Unsaved(models.Model):
    participation = models.ForeignKey(Participation)
    date = models.DateTimeField()
    data = models.TextField()

class SurveyUser(models.Model):
    global_id = models.CharField(max_length=36)
    last_participation = models.ForeignKey(Participation)
    last_participation_date = models.DateTimeField()

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    complete = models.BooleanField(default=False)
    data = models.TextField()

def add_global_id(sender, **kwargs):
    instance = kwargs.get('instance', None)
    try:
        user = SurveyUser.objects.get(user=instance)
    except SurveyUser.DoesNotExist:
        user = SurveyUser()
        user.user = instance
        user.global_id = str(uuid.uuid4())
        user.save()

post_save.connect(add_global_id, sender=User)

