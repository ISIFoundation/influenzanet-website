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

    help = 'Send Reminder for Mask Study'

    option_list = BaseCommand.option_list + (
        make_option('-f', '--fake', action='store_true',  dest='fake', help='fake sending', default=False),
        make_option('-l', '--limit', action='store',  dest='limit', help='Number of user to process', default=0),
        make_option('-u', '--user', action='store',  dest='user', help='User to process', default=None),
        make_option('-n', '--from', action='store',  dest='from', help='Reminder date (for test)', default=None),
    )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.fake = False
        self.survey = 'mask1'
        self.template = 'grippenet/masques'

    def send_email(self, user, participant, email):

        gid = participant.global_id
        next_uri = reverse('survey_fill', kwargs={'shortname': self.survey}) + '?gid=' + gid

        message = create_reminder_message(user, next=next_uri, template_name=self.template )

        if self.fake:
            print ' [fake]'
            return True

        try:
            send_message(email, message)
            return True
        except Exception, e:
            print e
            return False

    """
        SELECT p.id, weekly_id, p.user as account_id, p.timestamp, s.id as person_id, h.status from pollster_results_weekly p left join pollster_health_status h on h.pollster_results_weekly_id=p.id left join survey_surveyuser s on p.global_id=s.global_id where status='ILI' order by timestamp
    """

    """
    " Get respondends to the mask survey
    """
    def get_respondents(self):
        cursor = get_cursor()
        query = 'SELECT s.id as "person_id", s.user_id, count(*) "nb" from pollster_results_mask1 p left join survey_surveyuser s on p.global_id=s.global_id group by person_id'

        cursor.execute(query)
        desc = cursor.description
        columns = [col[0] for col in desc]

        rr = {}
        for r in cursor.fetchall():
            d = dict(zip(columns, r))
            rr[ d['user_id'] ] = d
        return rr

    def get_cohort_user(self, user_id=None):
        """
            registred accounts in the cohort
            Already notified
        """
        accounts = {}

        if(user_id is not None):
            user = User.objects.get(id=user_id)
            qb = [ MaskCohort.objects.get(user=user) ]
        else:
            qb = MaskCohort.objects.all()

        for p in qb:
            accounts[p.user.id] = p
        return accounts

    def handle(self, *args, **options):

        self.fake = options.get('fake')
        verbosity = options.get('verbosity')

        limit = int(options.get('limit'))

        date_from = options.get('from')

        provider = EpiworkUserProxy()

        respondents = self.get_respondents()
        cohort_users = self.get_cohort_user(options.get('user'))

        # First date to start reminder
        cohort_min_date = datetime.date(2019, 1, 30)

        if date_from is None:
            reminder_date = datetime.date.today() - datetime.timedelta(days=5)
        else:
            reminder_date = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()

        print "First reminder will be sent on %s" % (reminder_date, )

        count_sent = 0 # Email sent
        count = 0 # Account proccessed

        for cohort in cohort_users.itervalues():

            user_id = cohort.user.id
            survey_user = cohort.survey_user
            created_at = cohort.date_created

            if verbosity >= 1:
                if verbosity > 1:
                    print "u%-6d last: %10s" % (user_id, created_at ),

            if respondents.has_key(user_id):

                if verbosity > 1:
                    print "Account already in responded to survey"

                continue

            if created_at < cohort_min_date:
                if verbosity > 1:
                    print "too old"
                continue

            ## created_at > -15
            ## created_at < -5 jour

            if created_at > reminder_date:

                if verbosity > 1:
                    print "Too soon"

                continue

            if cohort.notification_count > 1:
                if verbosity > 1:
                    print "Already notified "

                continue

            django_user = cohort.user

            account = provider.find_by_django(django_user)

            if self.send_email(django_user, survey_user, account.email):

                print "user %d notified" % (user_id)

                if not self.fake:
                    cohort.notification_count = 2
                    cohort.last_notification = datetime.date.today()
                    cohort.save()
                count_sent += 1

                if count_sent % 20 == 0:
                    time.sleep(5)

            count += 1

            if limit > 0 and count > limit:
                print ""
                print "Reached limit of %d " % (limit, )
                break
