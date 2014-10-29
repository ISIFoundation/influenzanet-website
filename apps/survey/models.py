import uuid

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import connection

def create_global_id():
    return str(uuid.uuid4())

class SurveyUser(models.Model):
    user = models.ForeignKey(User, null=True) # null=True: only so because this happens 'in the wild', i.e.
                                              # in already existing data. Other than that there is no good
                                              # reason for it

    global_id = models.CharField(max_length=36, unique=True,
                                 default=create_global_id)
    last_participation_date = models.DateTimeField(null=True, blank=True)

    name = models.CharField(max_length=100)
    deleted = models.BooleanField(default=False)

    avatar = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'User'

    def __unicode__(self):
        return self.name

    def get_edit_url(self):
        """
        @deprecated: Not to be used
        """
        from . import views
        return '%s?gid=%s' % (reverse(views.people_edit), self.global_id)

    def get_profile_url(self):
        from . import views
        return '%s?gid=%s' % (reverse(views.profile_index), self.global_id)

    def get_survey_url(self):
        from . import views
        return '%s?gid=%s' % (reverse(views.index), self.global_id)

    def get_remove_url(self):
        from . import views
        return '%s?gid=%s' % (reverse(views.people_remove), self.global_id)

    def get_last_weekly_survey_date(self):
        try:
            cursor = connection.cursor()
            cursor.execute("select max(timestamp) from pollster_results_weekly where global_id = %s", [self.global_id])
        except:
            # (Klaas) not sure if this is still used in the actual app; it's used here at least for testing
            # The regular flow uses the pollster_results_weekly table
            if self.last_participation_date:
                return self.last_participation_date
            return self.user.date_joined

        row = cursor.fetchone()
        result = row[0]

        if result is None:
            return self.user.date_joined
        return result

