from django.db import models
from datetime import date

from apps.survey.models import SurveyUser

from django.utils.translation import ugettext_lazy as _

# Cohort is a group of user

class Cohort(models.Model):
    title = models.CharField(max_length=60)
    description = models.TextField()
    
    def __unicode__(self):
        return self.title


# Register a user in a given cohort
class CohortUser(models.Model):
    user = models.ForeignKey(SurveyUser)
    cohort = models.ForeignKey(Cohort)
    
    class Meta:
        unique_together = (('cohort','user'),)

# A token enables users to register in a given cohort (with a voucher for example).
# Once used you cannot know which user has used which token 
class Token(models.Model):
    cohort = models.ForeignKey(Cohort)
    token = models.CharField(max_length=30, unique=True)
    usage_left = models.PositiveIntegerField(null=True, blank=True)
    valid_until = models.DateField(null=True)
    
    class TokenException(Exception):
        """Exception for tokens"""
         
    # try to consume the token
    def consume(self):
        if self.usage_left is not None:
            if self.usage_left <= 0:
                raise Token.TokenException(_('No usage left for this token'))
            self.usage_left = self.usage_left - 1
        if self.valid_until:
            if self.valid_until < date.today():
                raise Token.TokenException(_('this token has expired'))
        self.save()
        
        
    def __unicode__(self):
        return self.token


            