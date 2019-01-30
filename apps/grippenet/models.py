from django.db import models
from django.contrib.auth.models import User
from apps.survey.models import SurveyUser

class PregnantCohort(models.Model):
    survey_user = models.ForeignKey(SurveyUser)

    # Inclusion date
    date_created = models.DateField(auto_now_add=True)

    # Is active in cohort
    active = models.BooleanField(default=True)

    # Do need to change the channel on the survey data
    change_channel = models.BooleanField(default=True)

    # Date when reminder should be sended from
    date_reminder = models.DateField(null=True)

    # Count of reminder sent
    reminder_count = models.IntegerField(default=0)

    def __str__(self):
        return '<Pregnant' + str(self.survey_user.id) +'>'

class ImmunoCohort(models.Model):
    survey_user = models.ForeignKey(SurveyUser, unique=True, primary_key=True)

    # Inclusion date
    date_created = models.DateField(auto_now_add=True)

    # Is active in cohort
    active = models.BooleanField(default=True)

    # Do need to change the channel on the survey data
    change_channel = models.BooleanField(default=True)

    def __str__(self):
        return '<Immuno ' + str(self.survey_user.id) +'>'


class Participation(models.Model):
    survey_user = models.ForeignKey(SurveyUser)
    first_season = models.IntegerField()
    last_season = models.IntegerField()


class MaskCohort(models.Model):
    """
        Mask cohort
        Notify the first user of each household (account)
    """
    user = models.ForeignKey(User, unique=True, primary_key=True)

    # Inclusion date
    date_created = models.DateField(auto_now_add=True)

    # Survey user who triggered the notification
    survey_user = models.ForeignKey(SurveyUser)

    # Is active in cohort
    active = models.BooleanField(default=True)

    notification_count = models.IntegerField(default=1)

    last_notification = models.DateField(null=True)

