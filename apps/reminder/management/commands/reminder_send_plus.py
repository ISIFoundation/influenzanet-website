from optparse import make_option
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from ...send import send
from ...models import get_settings, UserReminderInfo, MockNewsLetter
from django.db import connection
from django.conf import settings
from django.contrib.auth.models import User
from apps.reminder.models import NewsLetter, NewsletterTracking


def get_user_provider():
    # Get a user provider to iter accross user list
    # This class allow access to user's data (email) regardless of the User model
    from apps.accounts.provider import UserProvider
    provider = UserProvider()
    print provider.__class__
    return provider

# @TODO If more complex user checking is required, a chain-filter model should be implemented
# To make the check of each user an encapsulated the checking rules
class UserListChecker:
    """
    UserChecker check if a given user should receive a newsletter based on a userlist field
    which contains the name of a table/view with the target users' id (user_id field)
    """
    def __init__(self, message):
        if message.userlist:
            self.user_list = self.get_userlist(message.userlist)
        else:
            self.user_list = None

    def get_userlist(self, table):
        query = "SELECT user_id FROM " + table
        cursor = connection.cursor()
        cursor.execute(query)
        userlist = [ row[0] for row in cursor.fetchall()]
        return userlist

    def check(self, user):
        if self.user_list is None:
            return True
        try:
            i = self.user_list.index(user.id)
            return True
        except Exception as e:
            return False


class Command(BaseCommand):
    help = "Send reminders."

    option_list = BaseCommand.option_list + (
        make_option('--fake', action='store_true', dest='fake', default=False, help='Fake the sending of the emails; print the emails to be sent on screen instead.'),
        make_option('--user', action='store', dest='user', default=None, help='Send only to this user (user login)'),
        make_option('--verbose', action='store_true', dest='verbose', default=False, help='Print verbose message'),
        make_option('--debug', action='store_true', dest='debug', default=False, help='Print debug messages'),
        make_option('--counter', action='store', dest='counter', default=None, help='Store counter value into this file'),
        make_option('--log', action='store', dest='log', default=None, help='Store user email in a log file'),
        make_option('--next', action='store', dest='next', default=None, help='Next url for login url'),
        make_option('--mock', action='store_true', dest="mock", default=False, help="Create a mock newsletter and fake send it (always fake)"),
        make_option('--force', action='store_true', dest="force", default=False, help="Force the newsletter to be sent regardless user info state"),
        make_option('--check', action='store_true', dest="check", default=False, help="Only check wich newsletter will be sent"),
    )

    def __init__(self):
        super(BaseCommand, self).__init__()
        self.log = None
        self.fake = False
        self.force = False

        self.headers = {
         'Sender': settings.EMAIL_DEFAULT_SENDER,
         'Return-Path': settings.EMAIL_DEFAULT_SENDER,
         'Reply-To': 'contact@grippenet.fr'
        }

    def get_reminder(self):
        res = list(NewsLetter.objects.language('fr').filter(published=True).order_by('-date'))
        if(len(res) > 0):
            return res[0]
        raise Exception("No reminder found")

    def get_mock_reminder(self):
        reminder = MockNewsLetter()
        reminder.id = 0
        reminder.subject = "Mock newsletter"
        reminder.message = "Lorem ipsum"
        reminder.sender_email = "mock@localhost"
        reminder.sender_name = "mock"
        reminder.date = datetime.now()
        reminder.userlist = None
        reminder.next = None
        return reminder

    def send_reminders(self, message, target, next, batch_size):

        now = datetime.now()

        users = get_user_provider()
        if self.verbose:
            print "> User provider class : %s " % str(users.__class__)

        if(target is not None):
            print "> target user=%s" % (target)
            try:
                users = [ users.get_by_login(target) ]
                print users
            except Exception:
                print "Unable to find user %s" % str(target)
                return

        checker = UserListChecker(message)

        i = -1
        language = 'fr'
        print "next=%s" % (next)
        try:
            for user in users :
                if self.debug:
                    print user
                if batch_size and i >= batch_size:
                    raise StopIteration

                to_send = False

                info, _ = UserReminderInfo.objects.get_or_create(user=user, defaults={'active': True, 'last_reminder': user.date_joined})

                if not info.active:
                    continue

                if self.verbose:
                    print "id=%d last=%s " % (user.id, str(info.last_reminder),),

                if info.last_reminder is None:
                    to_send = True
                elif info.last_reminder < message.date:
                    to_send = True

                if to_send:
                    if not checker.check(user):
                        if self.verbose:
                            print " [checker] skip id=%s" % str(user.id),
                        to_send = False

                # If enforced mode : send regardless user info (only for test)
                if self.force:
                    to_send = True

                if to_send:
                    i += 1

                    tracker,_=NewsletterTracking.objects.get_or_create(user=user, newsletter=message, date_sent=now)
                    if not self.fake:
                        if self.verbose:
                            print " > sending [%d] %s " % (user.id, user.email,)
                        send(now, user, message, language, next=next, headers=self.headers, tracker=tracker)
                    else:
                        print "[fake] sending [%d] %s %s " % (user.id, user.email, message.subject)
                else:
                    if self.verbose:
                        print " skip"
        except StopIteration:
            pass
        return i + 1

    def handle(self, *args, **options):
        self.fake    = options.get('fake', False)
        self.log = options.get('log', None)
        self.verbose = options.get('verbose', False)
        self.debug = options.get('debug', False)
        self.force = options.get('force', False)
        user    = options.get('user', None)
        counter = options.get('counter', None)
        next = options.get('next', None)
        mock = options.get('mock', False)
        check = options.get('check', False)
        try:
            conf = get_settings()
        except:
            return u"0 Unable to load reminder configuration"

        if conf is None:
            return u"0 reminders sent - not configured"
        else:
            if conf.currently_sending and conf.last_process_started_date + timedelta(hours=3) > datetime.now():
                return u"0 reminders sent - too soon"

        batch_size = conf.batch_size

        conf.currently_sending = True
        conf.last_process_started_date = datetime.now()
        conf.save()

        try:
            if mock:
                message = self.get_mock_reminder()
                self.fake = True
            else:
                message = self.get_reminder()

            print "Newsletter #%d [%s] %s" % (message.id, str(message.date), message.subject)
            if check:
                return

            if next is None:
                if message.next:
                    # use redirect page for the newsletter if defined
                    next = message.next
                else:
                    # force next to LOGIN_REDIRECT_URL because when next is None
                    # send_reminders() set it to survey_index's url.
                    next = settings.LOGIN_REDIRECT_URL

            count = self.send_reminders(message=message, target=user, batch_size=batch_size, next=next)

            if(counter is not None):
                file(counter,'w').write(str(count))
            return u'%d reminders sent.\n' % count
        finally:
            # conf = get_settings()
            conf.currently_sending = False
            conf.save()

