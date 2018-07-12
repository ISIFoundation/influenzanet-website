from optparse import make_option
from django.core.management.base import CommandError, BaseCommand
from ...models import EpiworkUser
from django.contrib.sites.models import Site
from apps.sw_auth.utils import send_activation_email
from datetime import date

class Command(BaseCommand):
    help = 'manage activation'
    #args = 'resend|clean'
    option_list = BaseCommand.option_list + (
        make_option('-u', '--user', action='store', dest='user', default=None, help='User id'),
        make_option('-m', '--mail', action='store', dest='mail', default=None, help='User email'),
        make_option('-d', '--max-delay', action='store', dest='max_delay', default=30, help='Maximum delay from the user subscription to now (in days)'),
        make_option('-j', '--min-delay', action='store', dest='min_delay', default=1, help='Minimum delay from the user subscription to now (in days)'),
        make_option('-f', '--fake', action='store_true', dest='fake', default=False, help='Fake action'),
    )

    def handle(self, *args, **options):

        users = None

        if options['user'] is not None:
            users = [EpiworkUser.objects.get(id=options['user'])]

        if options['user'] is not None:
            users = [EpiworkUser.objects.get(id=options['user'])]

        if users is None:
            users = EpiworkUser.objects.filter(is_active=False)

        max_delay = options['max_delay']
        min_delay = options['min_delay']
        self.fake = options['fake']
        self.verbosity = options['verbosity']

        self.resend_activation(users, max_delay, min_delay)

    def check_double_email(self, user):
        # Check if there is another account activated with this email
        email = user.email
        try:
            uu = EpiworkUser.objects.filter(email__iexact=email, is_active=True)
            for u in uu:
                print "%d, %s, %s" % (u.id, u.login, u.email, )
            if(len(uu) > 0):
                return False
        except EpiworkUser.DoesNotExist:
            pass
        return True

    def resend_activation(self, users, max_delay, min_delay):
        site = Site.objects.get_current()
        today = date.today()
        for u in users:
            print u.login,
            if u.is_active:
                print "already activated"
                continue
            if not self.check_double_email(u):
                print "Another activated account exists for with this email"
                continue
            try:
                dju = u.get_django_user()
            except Exception, e:
                print e
                pass
            delay = None
            skip = False
            if dju.date_joined:
                delay = today - dju.date_joined.date()
                delay = delay.days
                if delay > max_delay:
                    skip = True
                if delay <= min_delay:
                    skip = True
                if skip:
                    if int(self.verbosity) > 1:
                        print "joined %d days ago, skip" % delay

            if skip:
                print "skip"
                continue

            print "resend activation %s" % u.login,

            if self.fake:
                print " fake"
            else:
                if u.email is None:
					print "No email, skip"
					continue

                if u.email.endswith('@localhost'):
					print "localhost address, anonymized account"
					continue
                try:
                	send_activation_email(u, site, renew=False)
                	print " sent"
                except Exception, e:
                	print e
                	pass
