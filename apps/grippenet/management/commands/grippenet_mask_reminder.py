from django.core.management.base import BaseCommand
from optparse import make_option

from apps.grippenet.models import PregnantCohort
from django.core.urlresolvers import reverse
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

import datetime
import time

from apps.common.db import get_cursor
from apps.sw_auth.models import EpiworkUserProxy

from ...models import MaskCohort 

from ...reminder import create_message

class Command(BaseCommand):
    help = 'Send Reminder about Pregnant survey'

    option_list = BaseCommand.option_list + (
        make_option('-f', '--fake', action='store_true',  dest='fake', help='fake sending', default=False),
    )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.fake = False

    def send_email(self, user, gid, email):

        next = reverse('survey_fill', kwargs={'shortname': self.survey}) + '?gid=' + gid

        text_content, html_content = create_message(user, next=next, template=self.template +'.html' )

        text_content = strip_tags(text_content)
        msg = EmailMultiAlternatives(
            'Etude G-GrippeNet',
            body=text_content,
            to=[email],
            )

        msg.attach_alternative(html_content, "text/html")

        if self.fake:
            print ' [fake]'
            return True

        try:
            msg.send()
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
        query = 'SELECT s.id as "person_id", count(*) "nb", min(timestamp) "first", max(timestamp) "last" from pollster_results_weekly p left join pollster_health_status h on h.pollster_results_weekly_id=p.id left join survey_surveyuser s on p.global_id=s.global_id where status=''ILI'' group by person_id'
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
            participants[p.survey_user] = p
        return participants

    def handle(self, *args, **options):

        self.fake = options.get('fake')

        provider = EpiworkUserProxy()

        participants = self.get_participants()

        # Get respondents
        respondents = self.get_respondents(survey)

        for r in respondents:
            person_id = r.person_id
            if person_id in participants:
                print "Already in participants"
                next
            

        print "%d particpants to scan" % ( len(participants))
        for p in participants:
            su = p.survey_user
            suid = su.id
            dju = su.user
            if suid in respondents:
                print "participant #%d already responded" % (suid,)
                continue

            account = provider.find_by_django(dju)
            if account is not None:
                print "sending reminder to participant #%d <%s>" %(suid, account.email),
                if self.send_email(dju, su.global_id, account.email):
                    p.reminder_count = p.reminder_count + 1
                    p.date_reminder = now + datetime.timedelta(days=15) # future date
                    p.save()
            else:
                print "Unable to find email for participant #%d" %(suid,)
        time.sleep(1)

