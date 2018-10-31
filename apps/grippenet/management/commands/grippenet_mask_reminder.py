from django.core.management.base import BaseCommand
from optparse import make_option

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from apps.survey.models import SurveyUser

import datetime
import time

from apps.common.db import get_cursor
from apps.common.mail import send_message
from apps.sw_auth.models import EpiworkUserProxy

from ...models import MaskCohort

from ...reminder import create_reminder_message

class Command(BaseCommand):
    help = 'Send Reminder about Pregnant survey'

    option_list = BaseCommand.option_list + (
        make_option('-f', '--fake', action='store_true',  dest='fake', help='fake sending', default=False),
    )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.fake = False
        self.survey = 'gripmask'
        self.template = 'grippenet/masques'

    def send_email(self, user, gid, email):

        next = reverse('survey_fill', kwargs={'shortname': self.survey}) + '?gid=' + gid

        message = create_reminder_message(user, next=next, template=self.template )

        if self.fake:
            print ' [fake]'
            return True

        try:
            send_message(email, message)
            print ' sent.'
            return True
        except Exception, e:
            print e
            return False

    """
        SELECT p.id, weekly_id, p.user as account_id, p.timestamp, s.id as person_id, h.status from pollster_results_weekly p left join pollster_health_status h on h.pollster_results_weekly_id=p.id left join survey_surveyuser s on p.global_id=s.global_id where status='ILI' order by timestamp
    """

    def get_respondents(self):
        cursor = get_cursor()
        query = 'SELECT s.id as "person_id", s.user as "user_id", count(*) "nb", min(timestamp) "first", max(timestamp) "last" from pollster_results_weekly p left join pollster_health_status h on h.pollster_results_weekly_id=p.id left join survey_surveyuser s on p.global_id=s.global_id where status=\'ILI\' group by person_id'
        cursor.execute(query)
        desc = cursor.description
        columns = [col[0] for col in desc]

        for r in cursor.fetchall():
            yield dict(zip(columns, r))

    def get_participants(self):
        """
            registred participants in the cohort
            Already notified
        """
        participants = {}
        for p in MaskCohort.objects.all():
            participants[p.user.id] = p
        return participants

    def handle(self, *args, **options):

        count_sent = 0

        self.fake = options.get('fake')

        now = datetime.date.today()

        provider = EpiworkUserProxy()

        participants = self.get_participants()

        # Get respondents
        respondents = self.get_respondents()

        # First date to start reminder
        reminder_date = now - datetime.timedelta(days=15)

        for r in respondents:
            person_id = r['person_id']
            user_id = r['user_id']
            first = r['first']
            if user_id in participants:
                print "Account already in participants"
                next

            if first > reminder_date:
               print "Too soon"
               next

            survey_user = SurveyUser.objects.get(id=person_id)
            django_user = User.objects.get(id=user_id)

            account = provider.find_by_django(django_user)
            if self.send_email(django_user, survey_user.global_id, account.email):
                print "user %d notified" % (user_id)
                part = MaskCohort()
                part.user = django_user
                part.survey_user = survey_user
                part.active = True
                part.save()
                count_sent += 1
                if count_sent % 20 == 0:
                    time.sleep(5)
