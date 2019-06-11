from optparse import make_option
from django.core.management.base import CommandError, BaseCommand
from ...models import EpiworkUser
from django.contrib.sites.models import Site
from apps.sw_auth.utils import send_activation_email

from django.core.validators import email_re
from apps.sw_auth.models import AnonymizeLog
from datetime import date

def is_email_valid(email):
    return bool(email_re.match(email))

class Command(BaseCommand):
    help = 'allow to change some user email'

    option_list = BaseCommand.option_list + (
        make_option('-i', '--id', action='store', dest='id', default=None, help='User id (EpiworkUser id)'),
        make_option('-m', '--mail', action='store', dest='mail', default=None, help='User email'),
        make_option('-n', '--new', action='store', dest='mail_new', default=None, help='New User email'),
        make_option('-a', '--activate', action='store_true', dest='activate', default=None, help='Resend activation with new email'),
        make_option('-r', '--reactivate', action='store_true', dest='reactivate', default=None, help='Reactivate user & resend activation with new email'),
    )

    def handle(self, *args, **options):

        if options['mail'] is None and options['id'] is None:
            raise CommandError('Mail or id should be provided is not provided')
        if options['mail_new'] is None:
            raise CommandError('new Mail is not provided')

        if options['id'] is not None:
            users = [EpiworkUser.objects.get(id=options['id'])]
        else:
            mail = options['mail']
            # Dont check for source email validity (could be invalid=
            #if not is_email_valid(mail):
            #    raise CommandError('email "%s" invalid' % mail)
            users = EpiworkUser.objects.filter(email__iexact=mail)


        new_mail = options['mail_new']
        if not is_email_valid(new_mail):
            raise CommandError('email "%s" invalid' % new_mail)

        new_mail = new_mail.lower()

        activate = options['activate'] or options['reactivate']
        reactivate = options['reactivate']

        if activate:
            site = Site.objects.get_current()

        if len(users) == 0:
            print 'User not found'
            return
        print "%d user(s) found" % len(users)
        print '----'

        if reactivate:
            date_login = date.today()

        uu = EpiworkUser.objects.filter(email__iexact=new_mail, is_active=True)
        if len(uu) > 0:
            print "Email %s is already associated with an active account" % (new_mail)
            return

        for user in users:
            print "- User (id,login,mail): %d, %s, %s" % (user.id, user.login, user.email)
            confirm = raw_input("Confirm (yes/no) ")
            if confirm == "yes":

                if reactivate:
                    print("Reactivate user")
                    user.login = new_mail
                    user.anonymize_warn = None
                    user.is_active = True
                    dju = user.get_django_user()
                    dju.last_login = date_login # Fake a
                    dju.is_active = True
                    dju.save()
                    ano = AnonymizeLog.objects.create(user=user, event=AnonymizeLog.EVENT_REACTIVATED)
                    ano.save()

                user.email = new_mail
                user.save()
                print "user email changed to %s" % user.email
                if activate:
                    send_activation_email(user, site, reactivation=reactivate)
                    print "activation sended to %s" % user.email
