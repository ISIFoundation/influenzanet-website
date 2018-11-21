from django.core.management.base import BaseCommand

from django.conf import settings
from apps.common.db import get_cursor
from django.core.management.color import supports_color
from django.utils.termcolors import colorize
from apps.pollster import models
from apps.pollster.runner import get_workflows

LOG_OK = 1
LOG_WARN = 2
LOG_ERROR = 3

color_supported = supports_color()

def with_color(msg, color):
    if color_supported:
        return colorize(msg, fg=color)
    return msg

class Command(BaseCommand):
    help = 'Run check to start GrippeNet season'

    def log(self, type, message):
        tag = ''
        if type == LOG_OK:
            tag = with_color('[OK]', 'green')
        if type == LOG_WARN:
            tag = with_color('[WARNING]', 'yellow')
        if type == LOG_ERROR:
            tag = with_color('[ERROR]', 'red')

        print tag,' ', message


    def count_survey(self, shortname):
        survey = models.Survey.get_by_shortname(shortname)
        m = survey.as_model()
        return m.objects.count()

    def count_table(self, table):
        query = "select count(*) from %s" % table
        cursor = get_cursor()
        cursor.execute(query)
        r = cursor.fetchone()
        return r[0]

    def check_survey_empty(self, name):
        count = self.count_survey(name)
        if count > 0:
            self.log(LOG_WARN, "survey %s is not empty (%d rows)" % (name, count,))
        else:
            self.log(LOG_OK, "Survey %s is empty" % name)

    def check_table_empty(self, name):
        count = self.count_table(name)
        if count > 0:
            self.log(LOG_WARN, "table %s is not empty (%d rows)" % (name, count,))
        else:
            self.log(LOG_OK, "table %s is empty" % name)


    def handle(self, *args, **options):

        has_error = False

        if settings.SURVEY_WAIT_LAUNCH:
            self.log(LOG_ERROR, 'SURVEY_WAIT_LAUNCH is True')
            has_error = True
        else:
            self.log(LOG_OK, 'SURVEY_WAIT_LAUNCH is False')

        intake = getattr(settings, 'POLLSTER_USER_PROFILE_SURVEY', 'intake')
        self.check_survey_empty(intake)

        self.check_survey_empty("weekly")

        self.check_table_empty('dashboard_userbadge')

        workflows = get_workflows()
        last= workflows[-1]
        cn = last.__module__ + '.' + last.__class__.__name__
        if cn == 'apps.survey.workflow.InfluenzanetWorkflow':
            self.log(LOG_OK, 'Influenzanet Workflow set')
        else:
            self.log(LOG_ERROR, 'Influenzanet workflow is not the last workflow')

