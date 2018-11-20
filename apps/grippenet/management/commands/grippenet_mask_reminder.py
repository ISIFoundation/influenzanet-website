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
        make_option('-t', '--mock', action='store',  dest='table', help='Use mock table to test algorithm', default=None),
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

    def get_respondents(self):
        cursor = get_cursor()

        if self.mock is not None:
            # Table should have
            #
            query = 'SELECT "person_id", user_id, "nb", "first", "last" from %s' % (self.table, )
        else:
            query = 'SELECT s.id as "person_id", s.user_id, count(*) "nb", date(min(timestamp)) "first", date(max(timestamp)) "last" from pollster_results_weekly p left join pollster_health_status h on h.pollster_results_weekly_id=p.id left join survey_surveyuser s on p.global_id=s.global_id where status=\'ILI\' group by person_id'

        cursor.execute(query)
        desc = cursor.description
        columns = [col[0] for col in desc]

        for r in cursor.fetchall():
            yield dict(zip(columns, r))

    def get_accounts(self):
        """
            registred accounts in the cohort
            Already notified
        """
        accounts = {}
        for p in MaskCohort.objects.all():
            accounts[p.user.id] = p
        return accounts

    def handle(self, *args, **options):


        self.fake = options.get('fake')
        self.mock = options.get('mock')

        verbosity = options.get('verbosity')

        limit = int(options.get('limit'))

        mocking = self.mock is not None

        date_from = options.get('from')


        provider = EpiworkUserProxy()

        if mocking:
            accounts = {}
        else:
            accounts = self.get_accounts()

        # Get respondents
        respondents = self.get_respondents()

        # First date to start reminder
        if date_from is None:
            reminder_date = datetime.date.today() - datetime.timedelta(days=15)
        else:
            reminder_date = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()

        print "First reminder will be sent on %s" % (reminder_date, )

        count_sent = 0 # Email sent
        count = 0 # Account proccessed

        for r in respondents:

            person_id = r['person_id']
            user_id = r['user_id']
            first = r['first']

            if verbosity >= 1:
                if verbosity > 1:
                    print "p%-6d u%-6d first: %10s last: %10s nb: %-2d" % (person_id, user_id, first, r['last'], r['nb'] ),
                else:
                    print "%6d %6d" % (person_id, user_id),

            if user_id in accounts:

                if verbosity > 1:
                    print "Account already in participants"

                continue

            if first < reminder_date:

                if verbosity > 1:
                    print "Too soon"

                continue

            survey_user = SurveyUser.objects.get(id=person_id)
            django_user = User.objects.get(id=user_id)

            account = provider.find_by_django(django_user)

            if self.send_email(django_user, survey_user, account.email):

                print "user %d notified" % (user_id)

                if not mocking and not self.fake:
                    part = MaskCohort()
                    part.user = django_user
                    part.survey_user = survey_user
                    part.active = True
                    part.notification = True
                    part.date_created = datetime.date.today()
                    part.save()
                count_sent += 1

                if count_sent % 20 == 0:
                    time.sleep(5)

            count += 1

            if limit > 0 and count > limit:
                print ""
                print "Reached limit of %d " % (limit, )
                break

