from django.core.management.base import CommandError, BaseCommand
from optparse import make_option
from ...models import EpiworkUser
from ...anonymize import Anonymizer

from datetime import date, datetime

class Command(BaseCommand):
    help = 'Unsubscribing management of old accounts.'
    option_list = BaseCommand.option_list + (
        make_option('-f', '--fake', action='store_true',
            dest='fake', default=False,
            help='Fake the resent (show list).'),
        make_option('-l', '--limit', action='store',
            dest='limit', default=None,
            help='Number of user to process'),
    )

    def delay(self, d):
        """
        Delay in days
        """
        if d is None:
            return None
        if isinstance(d, datetime):
            d = d.date()
        delay = date.today() - d
        return delay.days

    def fake(self, action, user):
        print " + [fake] %s for user %d" % (action, user.id)

    def handle(self, *args, **options):

        # fake the action
        fake = options.get('fake')
        limit = int(options.get('limit'))

        users = EpiworkUser.objects.filter(is_active=True)

        anonymizer = Anonymizer()

        max_delay = anonymizer.login_delay # delay from last login
        waiting_delay = anonymizer.waiting_delay # waiting delay between warning and deactivation

        count_warning = 0
        count_anonymize = 0
        count_cancel = 0
        count_errors = 0
        count_waiting = 0
        for user in users:
            dju = user.get_django_user()
            login_delay = self.delay(dju.last_login)
            if user.anonymize_warn is not None:
                anonymize_delay = self.delay(user.anonymize_warn)
                if anonymize_delay >= login_delay:
                    # The user has been connected after the warning
                    # Reactivate the account
                    count_cancel += 1
                    if not fake:
                        print '%d cancel anonymize' % (user.id, )
                        anonymizer.cancel(user)
                    else:
                        self.fake('cancel', user)
                else:
                    if anonymize_delay > waiting_delay:
                        count_anonymize += 1
                        if not fake:
                            try:
                                anonymizer.anonymize(user)
                                print  "%d anonymized" % (user.id, )
                            except:
                                count_errors += 1
                                print "Error during anonymizing of user %d " % user.id
                        else:
                            self.fake('anonymize', user)
                    else:
                        # Warn activated waiting for anonymization
                        count_waiting += 1
                        # print "%d will be anonymized in %d days (if no login)" % (user.id,  waiting_delay - anonymize_delay)
            else:
                # No warning
                if login_delay > max_delay:
                    count_warning += 1
                    if not fake:
                        print
                        anonymizer.warn(user)
                    else:
                        self.fake('warn', user)

            count = count_anonymize + count_cancel + count_warning
            if limit is not None:
                if count >= limit:
                    print 'Processed accounts Limit reached. Stopping'
                    break

        print "%d accounts processed, %d warning, %d anonymize, %d cancel, %d waiting" % (count, count_warning, count_anonymize, count_cancel, count_waiting)