from optparse import make_option
from django.core.management.base import CommandError, BaseCommand
from apps.sw_auth.models import EpiworkUser
from django.core.urlresolvers import reverse
from django.utils.http import int_to_base36
from apps.sw_auth.utils import send_user_email

class Command(BaseCommand):
    help = 'manage email token activation'
    #args = 'resend|clean'
    option_list = BaseCommand.option_list + (
        make_option('-p', '--proposal', action='store', dest='proposal', default=None, help='User email'),
        make_option('-f', '--fake', action='store_true', dest='fake', default=False, help='Fake action'),
    )

    def handle(self, *args, **options):

        users = None

        if options['proposal'] is not None:
            email = options['proposal']
            users = [EpiworkUser.objects.get(email_proposal=email)]

            if(len(users) != 0):
                uu = EpiworkUser.objects.filter(email=email)
                if(len(uu) > 0):
                    raise Exception('email %s is already associated with a user' % email)
                if len(users) > 1:
                    raise Exception('email %s is already associated with more than one user' % email)

        email = email.strip()

        user = users[0]

        token = user.create_email_proposal(email)
        user_id = int_to_base36(user.id)

        u = reverse('auth_email_change', kwargs={'user_id': user_id, 'token': token})

        url = 'https://www.grippenet.fr/' + u

        send_user_email('email_proposal', email, data={'url': url})
        send_user_email('email_proposal_warning', user.email, {'email': email})


