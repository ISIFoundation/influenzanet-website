from datetime import datetime
import uuid

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

def create_global_id():
    return str(uuid.uuid4())

class Survey(models.Model):
    survey_id = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    specification = models.TextField()

    def __unicode__(self):
        return '%s - %s' % (self.survey_id, self.title)

class Participation(models.Model):
    user = models.ForeignKey(SurveyUser)
    survey = models.ForeignKey(Survey)
    date = models.DateTimeField(auto_now_add=True)
    epidb_id = models.CharField(max_length=36, null=True)
    previous_participation = models.ForeignKey('self', null=True)
    previous_participation_date = models.DateTimeField(null=True)

    def __unicode__(self):
        return '%s (%s)' % (self.user.name, self.date)

    class Meta:
        verbose_name_plural = 'Survey participation log'

class ResponseSendQueue(models.Model):
    participation = models.ForeignKey(Participation)
    date = models.DateTimeField(auto_now_add=True)
    user_id = models.CharField(max_length=36)
    survey_id = models.CharField(max_length=50)
    answers = models.TextField()

    def set_sent(self, epidb_id):
        self.participation.epidb_id = epidb_id
        self.participation.save()
        self.delete()

class ProfileSendQueue(models.Model):
    owner = models.ForeignKey(SurveyUser)
    date = models.DateTimeField()
    user_id = models.CharField(max_length=36)
    survey_id = models.CharField(max_length=50)
    answers = models.TextField()

    def set_sent(self, epidb_id):
        self.delete()

class SurveyUser(models.Model):
    user = models.ForeignKey(User)
    global_id = models.CharField(max_length=36, unique=True,
                                 default=create_global_id)
    last_participation = models.ForeignKey(Participation, null=True)
    last_participation_date = models.DateTimeField(null=True)

    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'User'

class Profile(models.Model):
    user = models.ForeignKey(SurveyUser, unique=True)
    created = models.DateTimeField(null=True, default=None)
    updated = models.DateTimeField(null=True, default=None)
    valid = models.BooleanField(default=False)
    data = models.TextField(null=True, blank=True, default=None)
    survey = models.ForeignKey(Survey, null=True, default=None)

    def save(self):
        if self.valid:
            self.updated = datetime.now()
            if self.created is None:
                self.created = self.updated

        super(Profile, self).save()

    class Meta:
        verbose_name_plural = 'User profile'

class LastResponse(models.Model):
    user = models.ForeignKey(SurveyUser, unique=True)
    participation = models.ForeignKey(Participation, null=True, default=None)
    data = models.TextField(null=True, blank=True, default=None)

def add_first_survey_user(sender, **kwargs):
    instance = kwargs.get('instance', None)
    users = SurveyUser.objects.filter(user=instance)
    if len(users) == 0:
        name = '%s %s' % (instance.first_name, instance.last_name)
        name = name.strip()

        user = SurveyUser()
        user.user = instance
        user.name = name
        user.save()

def add_empty_profile(sender, **kwargs):
    instance = kwargs.get('instance', None)
    try:
        profile = Profile.objects.get(user=instance)
    except Profile.DoesNotExist:
        profile = Profile()
        profile.user = instance
        profile.save()

def add_empty_last_response(sender, **kwargs):
    instance = kwargs.get('instance', None)
    try:
        response = LastResponse.objects.get(user=instance)
    except LastResponse.DoesNotExist:
        response = LastResponse()
        response.user = instance
        response.save()

post_save.connect(add_first_survey_user, sender=User)
post_save.connect(add_empty_profile, sender=SurveyUser)
post_save.connect(add_empty_last_response, sender=SurveyUser)

