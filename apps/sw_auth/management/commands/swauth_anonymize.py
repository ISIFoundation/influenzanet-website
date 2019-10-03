from datetime import date, datetime
from optparse import make_option

from django.core.management.base import CommandError, BaseCommand
from django.contrib.auth.models import UNUSABLE_PASSWORD
from django.utils.translation import activate
from django.conf import settings

from ...models import EpiworkUser
from ...anonymize import Anonymizer
from apps.sw_auth.models import AnonymizeRequest, AnonymizeLog

class Command(BaseCommand):
    """
        Automatic anonymizing management

        This command handle 2 actions :

        1 - look for accounts with a big delay from the last connection and mark them to be anonymzed (send a warning email)
        2 - Proceed to anonymizing after a user request

    """
    args = "request|delay|inactive"
    help = 'Unsubscribing management of old accounts.'

    option_list = BaseCommand.option_list + (
        make_option('-f', '--fake', action='store_true',
            dest='fake', default=False,
            help='Fake the resent (show list).'),
        make_option('-l', '--limit', action='store',
            dest='limit', default=-1, type="int",
            help='Number of user to process'),
        make_option('-u', '--user', action='store',
            dest='user', default=None,
            help='User login to restrict action to'),
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
        print(" + [fake] %s for user %d" % (action, user.id))


    def lookup_old_account(self, fake, limit, user):

        print("Handle account without login")

        if user is not None:
            users = [user]
        else:
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

            if not user.is_active:
                print("#%d user is already inactive, skip" % user.id)
                continue

            dju = user.get_django_user()
            login_delay = self.delay(dju.last_login)
            if user.anonymize_warn is not None:
                anonymize_delay = self.delay(user.anonymize_warn)
                if anonymize_delay >= login_delay:
                    # The user has been connected after the warning
                    # Reactivate the account
                    count_cancel += 1
                    if not fake:
                        print("#%d cancel anonymize" % (user.id, ))
                        anonymizer.cancel(user)
                    else:
                        self.fake('cancel', user)
                else:
                    if anonymize_delay > waiting_delay:
                        count_anonymize += 1
                        if not fake:
                            try:
                                anonymizer.anonymize(user)
                                print("#%d anonymized" % (user.id, ))
                            except:
                                count_errors += 1
                                print("Error during anonymizing of user #%d " % user.id)
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
                        print "#%d warn user" % user.id
                        anonymizer.warn(user)
                    else:
                        self.fake('warn', user)

            count = count_anonymize + count_cancel + count_warning
            if limit > 0:
                if count >= limit:
                    print('Processed accounts Limit reached. Stopping')
                    break

        print("%d accounts processed, %d warning, %d anonymize, %d cancel, %d waiting" % (count, count_warning, count_anonymize, count_cancel, count_waiting))


    def handle_request(self, fake, limit, user):

        print("Handle account closing request")

        if user is not None:
            requests = AnonymizeRequest.objects.filter(user=user)
        else:
            requests = AnonymizeRequest.objects.all()

        anonymize = Anonymizer()

        count_waiting = 0
        count_anonymized = 0
        count_skip = 0
        count_error = 0
        count = 0
        for request in requests:
            delay = self.delay(request.date)
            id = request.id
            if delay < 5:
                count_waiting += 1
                continue
            user = request.user
            if user.is_active:
                if not fake:
                    try:
                        print("#%d anonymizing" % id)
                        anonymize.anonymize(user)
                        request.delete()
                        count_anonymized +=1
                    except Exception, e:
                        count_error += 1
                        print(e)
                else:
                    self.fake("anonymize", user)
            else:
                print("#%d skipped, user already inactive" % id)
                count_skip += 1
                request.delete()
            count += 1
            if limit > 0:
                if count >= limit:
                    print('Processed accounts Limit reached. Stopping')
                    break

        print("Requests: %d, %d anonymized, %d waiting, %d skipped" % (count, count_anonymized, count_waiting, count_skip))

    def handle_inactive(self, fake, limit, user):
        """
            Handle inactive accounts (never activated)
        """
        print("Handle inactive accounts")

        if user is not None:
            users = [user]
        else:
            users = EpiworkUser.objects.filter(is_active=False)

        anonymizer = Anonymizer()

        activation_delay = settings.ACCOUNT_ACTIVATION_DAYS * 5

        count_anonymize = 0
        count_waiting = 0
        count_never_active = 0
        for user in users:

            if user.is_active:
                continue

            dju = user.get_django_user()

            if dju.is_active:
                print("Warning: inconsistent is_active for %d %d" % (user.id, dju.id))
                continue

            if self.delay(user.anonymize_warn) < 365:
                continue

            login_delay = self.delay(dju.last_login)
            join_delay = self.delay(dju.date_joined)

            # Already anonymized
            if user.password == UNUSABLE_PASSWORD:

                ano_prefix = "user%d" % (user.id)

                if not user.login.startswith(ano_prefix):
                    print("Warning inconsistent login for %d" % (user.id))

                if dju.password != UNUSABLE_PASSWORD:
                    print("Warning: inconsistent password for %d" % (user.id))

                continue

            if login_delay < activation_delay:
                count_waiting += 1
                continue

            if login_delay == join_delay:
                count_never_active += 1

            count_anonymize += 1

            # print(" %")

            if not fake:
                user.anonymize()
                anonymizer.log(user, AnonymizeLog.EVENT_INACTIVE)
            else:
                self.fake('anonymize', user)

            count = count_anonymize
            if limit > 0:
                if count >= limit:
                    print('Processed accounts Limit reached. Stopping')
                    break
        print(" %d anonymized (%d never activated), %d recent activation" % (count_anonymize, count_never_active, count_waiting))

    def handle_check(self, fake, limit, user):
        """
            Handle inactive accounts (never activated)
        """
        print("Handle inactive accounts")

        activation_delay = settings.ACCOUNT_ACTIVATION_DAYS * 3

        if user is not None:
            users = [user]
        else:
            users = EpiworkUser.objects.filter(is_active=False)

        exceptions = [5705701869822915378, ]

        for user in users:

            if user.id in exceptions:
                continue;

            dju = user.get_django_user()
            problems = []
            if dju.is_active != user.is_active:
                problems.append("is_active")

            if not user.is_active:

                login_delay = self.delay(dju.last_login)

                ano_prefix = "user%d" % (user.id)

                if login_delay < activation_delay:
                    # Still waiting for activation
                    continue

                if not user.login.startswith(ano_prefix):
                    print("Warning inconsistent login for %d" % (user.id))

                if dju.password != UNUSABLE_PASSWORD:
                    print("Warning: inconsistent password for %d" % (user.id))

            if len(problems) > 0:
                print "User %d :" % (user.id,) + problems.join(',')




    def test_mail(self, user):
        anonymize = Anonymizer()
        anonymize.send_warning(user, test=True)
        anonymize.send_request(user, test=True)
        anonymize.send_anonymized(user.id, user.email, test=True)

    def handle(self, *args, **options):

        activate('fr')

        # fake the action
        fake = options.get('fake')
        limit = int(options.get('limit'))

        user = options.get('user')

        if user is not None:
            try:
                user = EpiworkUser.objects.get(login=user)
            except EpiworkUser.DoesNotExist:
                print("User '%s' not found ")
                return

        if len(args) == 0:
            raise CommandError("Please provide at least one subcommand")

        for command in args:
            command = command.lower()
            if command == 'request':
                print("Processing anonymize request")
                self.handle_request(fake=fake, limit=limit, user=user)
            elif command == 'delay':
                print("Processing account deactivation")
                self.lookup_old_account(fake=fake, limit=limit, user=user)
            elif command == 'mail':
                self.test_mail(user=user)
            elif command == 'inactive':
                self.handle_inactive(fake, limit, user)
            elif command == 'check':
                self.handle_check(fake, limit, user)
            else:
                CommandError("Unknown subcommand %s" % command)
